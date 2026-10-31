#!/usr/bin/env python3
"""
print_sighash_fields.py — a Feynman-style sighash field printer
=====================================================
Prints "what a signature actually signs" (the SigMsg of BIP-341 TapSighash) field
by field, and shows which fields each sighash flag SEES (commits to) and which it
leaves BLIND (does not commit to). Two examples: single input → multiple inputs.

The code is self-contained (BIP-341 hand-rolled with hashlib only), and uses
bitcoinutils as a "correctness oracle" for cross-checking: the hand-rolled digest
must equal the one bitcoinutils computes, byte for byte. If it passes, the layout
is correct, and the web page (index.html) mirrors exactly these bytes.

Run:  python3 print_sighash_fields.py
The field printing runs on any python3; the bitcoinutils cross-check at the end
needs `pip install bitcoinutils` (skipped automatically if missing; printing is
unaffected).
"""
import hashlib, struct

# ----------------------------------------------------------------- serialization primitives
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

def cscript(spk):  # scriptPubKey with length prefix
    return compact_size(len(spk)) + spk

def hx(b): return b.hex()

# sighash flag constants
SIGHASH_DEFAULT = 0x00
SIGHASH_ALL = 0x01
SIGHASH_NONE = 0x02
SIGHASH_SINGLE = 0x03
SIGHASH_ANYONECANPAY = 0x80


# ----------------------------------------------------------------- transaction model
class TxIn:
    def __init__(self, txid_hex_internal, vout, amount, spk_hex, seq=0xFFFFFFFF):
        # txid_hex_internal: 32 bytes in internal serialization order (the reverse of what block explorers display)
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


# --------------------------------------------- BIP-341 SigMsg, assembled field by field
def sigmsg_fields(tx, input_index, hash_type):
    """Return an ordered list of fields: each item = dict(name, cn, bytes, included, group, note).
    (`cn` is a short plain-language label for the field.)
    Fields with included=False do not go into the digest: "you left this cell BLIND,
    you didn't sign it, others can change it"."""
    anyonecanpay = (hash_type & SIGHASH_ANYONECANPAY) != 0
    out_type = hash_type & 0x03
    if out_type == 0:  # SIGHASH_DEFAULT has the same output semantics as ALL
        out_type = SIGHASH_ALL

    F = []
    def add(name, cn, data, included, group, note=""):
        F.append({"name": name, "cn": cn, "bytes": data, "included": included, "group": group, "note": note})

    # 0. epoch (0x00) — always
    add("epoch", "epoch byte", b"\x00", True, "head", "BIP-341 prefix, always 0x00")
    # 1. hash_type — always (value changes with the flag)
    add("hash_type", "sighash type", bytes([hash_type]), True, "head", "the flag you chose")
    # 2. nVersion — always
    add("nVersion", "version", i32(tx.version), True, "head", "")
    # 3. nLockTime — always
    add("nLockTime", "lock time", u32(tx.locktime), True, "head", "")

    # ---- commitments that SEE all inputs (only when NOT ANYONECANPAY) ----
    inc_all_inputs = not anyonecanpay
    sha_prevouts = sha256(b"".join(i.outpoint() for i in tx.vins))
    sha_amounts = sha256(b"".join(u64(i.amount) for i in tx.vins))
    sha_spks = sha256(b"".join(cscript(i.spk) for i in tx.vins))
    sha_seqs = sha256(b"".join(u32(i.seq) for i in tx.vins))
    note_ac = "" if inc_all_inputs else "ANYONECANPAY → BLIND: you can't see the other inputs; others can add/swap inputs"
    add("sha_prevouts", "where all inputs come from (prevouts)", sha_prevouts, inc_all_inputs, "all_inputs", note_ac)
    add("sha_amounts", "amounts of all inputs", sha_amounts, inc_all_inputs, "all_inputs", "")
    add("sha_scriptpubkeys", "locking scripts of all inputs", sha_spks, inc_all_inputs, "all_inputs", "")
    add("sha_sequences", "sequences of all inputs", sha_seqs, inc_all_inputs, "all_inputs", "")

    # ---- SEE all outputs (only when out_type == ALL) ----
    inc_outputs = (out_type == SIGHASH_ALL)
    sha_outputs = sha256(b"".join(o.serialize() for o in tx.vouts))
    note_out = "" if inc_outputs else ("NONE → BLIND: you don't care at all where the money goes" if out_type == SIGHASH_NONE
                                       else "SINGLE → the outputs as a whole are BLIND; only the row paired with you counts (see below)")
    add("sha_outputs", "all outputs (the whole bill)", sha_outputs, inc_outputs, "all_outputs", note_out)

    # ---- spend_type — always ----
    add("spend_type", "spend type", b"\x00", True, "mid", "0 = keypath, no annex")

    # ---- input side: with ANYONECANPAY, include the details of "my input"; otherwise just input_index ----
    if anyonecanpay:
        me = tx.vins[input_index]
        add("outpoint", "where my input comes from", me.outpoint(), True, "this_input",
            "ANYONECANPAY → commits only to my own coin")
        add("amount", "my input's amount", u64(me.amount), True, "this_input", "")
        add("scriptPubKey", "my input's locking script", cscript(me.spk), True, "this_input", "")
        add("nSequence", "my input's sequence", u32(me.seq), True, "this_input", "")
    else:
        add("input_index", "which input I am", u32(input_index), True, "this_input",
            "not ANYONECANPAY → just the index (the full input set is committed above)")

    # ---- SINGLE: only the output row paired with me counts ----
    inc_single = (out_type == SIGHASH_SINGLE)
    if inc_single and input_index < len(tx.vouts):
        sha_single = sha256(tx.vouts[input_index].serialize())
        add("sha_single_output", "the output on my row", sha_single, True, "single",
            "SINGLE → locks only my paired row; other output rows can be added/changed freely")

    return F


def compute_digest(tx, input_index, hash_type):
    F = sigmsg_fields(tx, input_index, hash_type)
    msg = b"".join(f["bytes"] for f in F if f["included"])
    return tagged_hash("TapSighash", msg)


# ----------------------------------------------------------------- printing
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
    print(f"(signing input {input_index}; the transaction has {len(tx.vins)} input(s) / {len(tx.vouts)} output(s))")
    print("=" * 78)
    # show the full field layout + SEE/BLIND with SIGHASH_ALL
    for label, ht in [("SIGHASH_ALL", SIGHASH_ALL), ("SINGLE | ANYONECANPAY", SIGHASH_SINGLE | SIGHASH_ANYONECANPAY)]:
        print(f"\n--- flag = {label} (0x{ht:02x}) —— which fields does the signature actually sign ---")
        F = sigmsg_fields(tx, input_index, ht)
        for f in F:
            mark = "👁 SEE  " if f["included"] else "🙈 BLIND"
            b = f["bytes"]
            shown = hx(b) if len(b) <= 40 else hx(b[:36]) + "…"
            line = f"  {mark}  {f['name']:<18} {shown}"
            print(line)
            if f["note"]:
                print(f"          ↳ {f['note']}")
        d = tagged_hash("TapSighash", b"".join(x["bytes"] for x in F if x["included"]))
        print(f"  => TapSighash digest = {hx(d)}")

    # digests of all six flags at a glance (all different = each signs different content)
    print(f"\n--- TapSighash digest for each of the six flags (input {input_index}) ---")
    for label, ht in FLAGS:
        print(f"  {label} 0x{ht:02x}  {hx(compute_digest(tx, input_index, ht))}")


def cross_check(tx, input_index):
    """Use bitcoinutils as an oracle to verify the hand-rolled digest byte for byte."""
    try:
        from bitcoinutils.setup import setup
        from bitcoinutils.transactions import Transaction, TxInput, TxOutput
        from bitcoinutils.script import Script
        setup("signet")
    except Exception as e:
        print(f"\n[cross-check skipped: bitcoinutils not available: {e}]")
        return
    bu_ins = [TxInput(i.txid[::-1].hex(), i.vout) for i in tx.vins]  # bitcoinutils uses display order (reversed)
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
    print("  => ALL MATCH ✅ hand-rolled layout is correct; the web page can mirror it" if ok else "  => MISMATCH ❌ needs fixing")
    return ok


# ----------------------------------------------------------------- sample transactions
# P2TR scriptPubKey = 5120 + 32-byte x-only key
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
    print_example("Example 1 · single input", t1, 0)
    cross_check(t1, 0)

    print()
    t2 = two_input_tx()
    print_example("Example 2 · multiple inputs (signing input 0)", t2, 0)
    cross_check(t2, 0)
    print_example("Example 2 · multiple inputs (signing input 1)", t2, 1)
    cross_check(t2, 1)
