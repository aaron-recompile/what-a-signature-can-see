#!/usr/bin/env python3
"""
print_sighash_fields.py — 费曼式 sighash 字段打印器
=====================================================
把"签名到底签的是什么"(BIP-341 TapSighash 的 SigMsg)一个字段一个字段打印出来,
并演示每个 sighash flag 到底"看见(commit)"哪些字段、"蒙住(不 commit)"哪些字段。
单输入 → 多输入两个例子。

这份代码是自洽的(只用 hashlib 手搓 BIP-341),同时用 bitcoinutils 当"正确性预言机"
交叉验证:手搓的 digest 必须逐字节等于 bitcoinutils 算的。跑通 = 布局绝对正确,网页
(index.html) 就镜像这套字节。

跑:  python3 print_sighash_fields.py
纯字段打印任何 python3 都能跑;末尾的 bitcoinutils 交叉验证需要 `pip install bitcoinutils`
(缺了会自动跳过,不影响打印)。
"""
import hashlib, struct

# ----------------------------------------------------------------- 序列化原语
def sha256(b): return hashlib.sha256(b).digest()

def tagged_hash(tag, msg):
    t = sha256(tag.encode())
    return sha256(t + t + msg)

def u32(n): return struct.pack("<I", n)
def i32(n): return struct.pack("<i", n)
def u64(n): return struct.pack("<Q", n)

def compact_size(n):
    if n < 253: return bytes([n])
    if n < 0x10000: return b"\xfd" + struct.pack("<H", n)
    if n < 0x100000000: return b"\xfe" + struct.pack("<I", n)
    return b"\xff" + struct.pack("<Q", n)

def cscript(spk):  # scriptPubKey 带长度前缀
    return compact_size(len(spk)) + spk

def hx(b): return b.hex()

# sighash flag 常量
SIGHASH_DEFAULT = 0x00
SIGHASH_ALL = 0x01
SIGHASH_NONE = 0x02
SIGHASH_SINGLE = 0x03
SIGHASH_ANYONECANPAY = 0x80


# ----------------------------------------------------------------- 交易模型
class TxIn:
    def __init__(self, txid_hex_internal, vout, amount, spk_hex, seq=0xFFFFFFFF):
        # txid_hex_internal: 32 字节的内部序列化顺序 (即区块浏览器显示的反转)
        self.txid = bytes.fromhex(txid_hex_internal)
        assert len(self.txid) == 32
        self.vout = vout
        self.amount = amount
        self.spk = bytes.fromhex(spk_hex)
        self.seq = seq
    def outpoint(self): return self.txid + u32(self.vout)

class TxOut:
    def __init__(self, amount, spk_hex):
        self.amount = amount
        self.spk = bytes.fromhex(spk_hex)
    def serialize(self): return u64(self.amount) + cscript(self.spk)

class Tx:
    def __init__(self, version, locktime, vins, vouts):
        self.version = version
        self.locktime = locktime
        self.vins = vins
        self.vouts = vouts


# --------------------------------------------- BIP-341 SigMsg 逐字段组装
def sigmsg_fields(tx, input_index, hash_type):
    """返回一个有序字段列表: 每项 = dict(name, cn, bytes, included, group, note)。
    included=False 的字段不进 digest,代表"这格你蒙住了、没签,别人能改"。"""
    anyonecanpay = (hash_type & SIGHASH_ANYONECANPAY) != 0
    out_type = hash_type & 0x03
    if out_type == 0:  # SIGHASH_DEFAULT 的输出语义 = ALL
        out_type = SIGHASH_ALL

    F = []
    def add(name, cn, data, included, group, note=""):
        F.append({"name": name, "cn": cn, "bytes": data, "included": included, "group": group, "note": note})

    # 0. epoch (0x00) — 永远
    add("epoch", "纪元字节", b"\x00", True, "head", "BIP-341 前缀,恒为 0x00")
    # 1. hash_type — 永远 (值随 flag 变)
    add("hash_type", "签名类型", bytes([hash_type]), True, "head", "你选的 flag 本身")
    # 2. nVersion — 永远
    add("nVersion", "版本", i32(tx.version), True, "head", "")
    # 3. nLockTime — 永远
    add("nLockTime", "锁定时间", u32(tx.locktime), True, "head", "")

    # ---- 看见所有输入的承诺 (仅当 NOT ANYONECANPAY) ----
    inc_all_inputs = not anyonecanpay
    sha_prevouts = sha256(b"".join(i.outpoint() for i in tx.vins))
    sha_amounts = sha256(b"".join(u64(i.amount) for i in tx.vins))
    sha_spks = sha256(b"".join(cscript(i.spk) for i in tx.vins))
    sha_seqs = sha256(b"".join(u32(i.seq) for i in tx.vins))
    note_ac = "" if inc_all_inputs else "ANYONECANPAY → 蒙住:你看不见别的输入了,别人能加/换输入"
    add("sha_prevouts", "所有输入的来源(prevouts)", sha_prevouts, inc_all_inputs, "all_inputs", note_ac)
    add("sha_amounts", "所有输入的金额", sha_amounts, inc_all_inputs, "all_inputs", "")
    add("sha_scriptpubkeys", "所有输入的锁定脚本", sha_spks, inc_all_inputs, "all_inputs", "")
    add("sha_sequences", "所有输入的 sequence", sha_seqs, inc_all_inputs, "all_inputs", "")

    # ---- 看见所有输出 (仅当 out_type == ALL) ----
    inc_outputs = (out_type == SIGHASH_ALL)
    sha_outputs = sha256(b"".join(o.serialize() for o in tx.vouts))
    note_out = "" if inc_outputs else ("NONE → 蒙住:钱去哪你全不管" if out_type == SIGHASH_NONE
                                       else "SINGLE → 蒙住整体输出,只认对着你那一行(见下)")
    add("sha_outputs", "所有输出(整张账单)", sha_outputs, inc_outputs, "all_outputs", note_out)

    # ---- spend_type — 永远 ----
    add("spend_type", "花费类型", b"\x00", True, "mid", "0=keypath 无 annex")

    # ---- 输入侧:ANYONECANPAY 时放"我这个输入"的明细;否则放 input_index ----
    if anyonecanpay:
        me = tx.vins[input_index]
        add("outpoint", "我这个输入的来源", me.outpoint(), True, "this_input",
            "ANYONECANPAY → 只承诺我自己这枚币")
        add("amount", "我这个输入的金额", u64(me.amount), True, "this_input", "")
        add("scriptPubKey", "我这个输入的锁定脚本", cscript(me.spk), True, "this_input", "")
        add("nSequence", "我这个输入的 sequence", u32(me.seq), True, "this_input", "")
    else:
        add("input_index", "我是第几个输入", u32(input_index), True, "this_input",
            "不 ANYONECANPAY → 只记序号(承诺整套输入已在上面)")

    # ---- SINGLE:只认对着我那一行输出 ----
    inc_single = (out_type == SIGHASH_SINGLE)
    if inc_single and input_index < len(tx.vouts):
        sha_single = sha256(tx.vouts[input_index].serialize())
        add("sha_single_output", "对着我那一行的输出", sha_single, True, "single",
            "SINGLE → 只锁我对应那一行,别的输出行随便加/改")

    return F


def compute_digest(tx, input_index, hash_type):
    F = sigmsg_fields(tx, input_index, hash_type)
    msg = b"".join(f["bytes"] for f in F if f["included"])
    return tagged_hash("TapSighash", msg)


# ----------------------------------------------------------------- 打印
FLAGS = [
    ("SIGHASH_ALL           ", SIGHASH_ALL),
    ("SIGHASH_NONE          ", SIGHASH_NONE),
    ("SIGHASH_SINGLE        ", SIGHASH_SINGLE),
    ("ALL | ANYONECANPAY    ", SIGHASH_ALL | SIGHASH_ANYONECANPAY),
    ("NONE | ANYONECANPAY   ", SIGHASH_NONE | SIGHASH_ANYONECANPAY),
    ("SINGLE | ANYONECANPAY ", SIGHASH_SINGLE | SIGHASH_ANYONECANPAY),
]

def print_example(title, tx, input_index):
    print("=" * 78)
    print(title)
    print(f"(为第 {input_index} 个输入签名; 交易有 {len(tx.vins)} 个输入 / {len(tx.vouts)} 个输出)")
    print("=" * 78)
    # 用 SIGHASH_ALL 展示完整字段布局 + 看/蒙
    for label, ht in [("SIGHASH_ALL", SIGHASH_ALL), ("SINGLE | ANYONECANPAY", SIGHASH_SINGLE | SIGHASH_ANYONECANPAY)]:
        print(f"\n--- flag = {label} (0x{ht:02x}) —— 签名到底签了哪些字段 ---")
        F = sigmsg_fields(tx, input_index, ht)
        for f in F:
            mark = "👁 看" if f["included"] else "🙈 蒙"
            b = f["bytes"]
            shown = hx(b) if len(b) <= 40 else hx(b[:36]) + "…"
            line = f"  {mark}  {f['name']:<18} {shown}"
            print(line)
            if f["note"]:
                print(f"          ↳ {f['note']}")
        d = tagged_hash("TapSighash", b"".join(x["bytes"] for x in F if x["included"]))
        print(f"  => TapSighash digest = {hx(d)}")

    # 六种 flag 的 digest 一览 (看它们互不相同 = 签的是不同内容)
    print(f"\n--- 六种 flag 各自的 TapSighash digest (为 input {input_index}) ---")
    for label, ht in FLAGS:
        print(f"  {label} 0x{ht:02x}  {hx(compute_digest(tx, input_index, ht))}")


def cross_check(tx, input_index):
    """用 bitcoinutils 当预言机, 验证手搓 digest 逐字节正确。"""
    try:
        from bitcoinutils.setup import setup
        from bitcoinutils.transactions import Transaction, TxInput, TxOutput
        from bitcoinutils.script import Script
        setup("signet")
    except Exception as e:
        print(f"\n[cross-check skipped: bitcoinutils not available: {e}]")
        return
    bu_ins = [TxInput(i.txid[::-1].hex(), i.vout) for i in tx.vins]  # bitcoinutils 用显示序(反转)
    for k, i in enumerate(tx.vins):
        bu_ins[k].sequence = struct.pack("<I", i.seq)
    bu_outs = [TxOutput(o.amount, Script.from_raw(o.spk.hex())) for o in tx.vouts]
    bu_tx = Transaction(bu_ins, bu_outs, has_segwit=True)
    bu_tx.version = i32(tx.version)
    bu_tx.locktime = u32(tx.locktime)
    spks = [Script.from_raw(i.spk.hex()) for i in tx.vins]
    amts = [i.amount for i in tx.vins]
    print(f"\n--- cross-check vs bitcoinutils (input {input_index}) ---")
    ok = True
    for label, ht in FLAGS:
        mine = compute_digest(tx, input_index, ht)
        theirs = bu_tx.get_transaction_taproot_digest(input_index, spks, amts, sighash=ht)
        match = (mine == theirs)
        ok = ok and match
        print(f"  {label} 0x{ht:02x}  {'✅ match' if match else '❌ MISMATCH'}")
    print("  => ALL MATCH ✅ 手搓布局正确, 网页可镜像" if ok else "  => 有 MISMATCH ❌ 需修")
    return ok


# ----------------------------------------------------------------- 样例交易
# P2TR scriptPubKey = 5120 + 32字节x-only-key
SPK_A = "5120" + "a1" * 32
SPK_B = "5120" + "b2" * 32
SPK_IN0 = "5120" + "11" * 32
SPK_IN1 = "5120" + "22" * 32

def single_input_tx():
    vin = TxIn("aa" * 32, 0, 100_000, SPK_IN0)
    vouts = [TxOut(95_000, SPK_A)]  # fee 5000
    return Tx(2, 0, [vin], vouts)

def two_input_tx():
    v0 = TxIn("aa" * 32, 0, 100_000, SPK_IN0)
    v1 = TxIn("cc" * 32, 1, 50_000, SPK_IN1)
    vouts = [TxOut(90_000, SPK_A), TxOut(55_000, SPK_B)]  # fee 5000
    return Tx(2, 0, [v0, v1], vouts)


if __name__ == "__main__":
    t1 = single_input_tx()
    print_example("例 1 · 单输入", t1, 0)
    cross_check(t1, 0)

    print()
    t2 = two_input_tx()
    print_example("例 2 · 多输入 (为 input 0 签)", t2, 0)
    cross_check(t2, 0)
    print_example("例 2 · 多输入 (为 input 1 签)", t2, 1)
    cross_check(t2, 1)
