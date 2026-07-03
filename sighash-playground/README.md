# SIGHASH playground · 签名能看见什么

"什么是签名真正签的内容" —— sighash message (BIP-341 TapSighash) 的可玩可读三件套。
配套书《签名能看见什么》,把小册子里的"看/蒙纸带"变成**真实字节 + 可交互 + 可发布**。

## 三件套

| 文件 | 是什么 | 怎么用 |
|---|---|---|
| **`index.html`** | 交互网页:两个旋钮(输入侧 ANYONECANPAY / 输出侧 ALL·NONE·SINGLE),实时看哪些字段被 **SEE 看** / **BLIND 蒙**,digest 现算 | 双击打开即可(纯前端,内置 SHA-256,**无需联网**)。内置自检:JS digest 对比 Python/bitcoinutils 验过的值,算错会红字报警 |
| **`print_sighash_fields.py`** | 费曼式字段打印器:单输入→多输入,把 SigMsg 一个字段一个字段打印 + 每个 flag 看/蒙什么。同时用 `bitcoinutils` 当预言机**逐字节交叉验证** | `…/btcaaron/.venv-test/bin/python print_sighash_fields.py`(纯打印部分任何 python3 都行) |
| **`blog/`** | 两篇英文技术博客(Aaron Medium 风格) | `blog1_what_a_signature_signs.md`(教 sighash + 网页/代码) · `blog2_when_two_signatures_collide.md`(冲突,配 signet 实验) |

## 正确性保证(不是口算)

`index.html`(JS)、`print_sighash_fields.py`(手搓)、`bitcoinutils`(生产库)三方,对
**单输入×6 flag + 双输入×2 input×6 flag = 18 个 digest** 全部逐字节一致。网页打开时也会
自跑自检。所以"你看到的字节是真的"。

## 两个旋钮 = 六种 flag

```
                 OUT: ALL          OUT: NONE         OUT: SINGLE
 IN: all         SIGHASH_ALL       SIGHASH_NONE      SIGHASH_SINGLE
 IN: only-mine   ALL|ANYONECANPAY  NONE|ANYONECANPAY SINGLE|ANYONECANPAY
```
输入侧只有 2 档(你蒙不掉自己正在花的那枚币),输出侧 3 档 → 2×3=6。真名 = 玩具里"看多少"。

## 发布

- 博客:两篇 `blog/*.md` 直接可贴 Medium(@aaron.recompile),记得把相对链接换成部署后的 URL。
- 网页:`index.html` 单文件,可托管在 bitcoincoding.dev / GitHub Pages 任意静态位置,博客链过去。
- 姊妹实验:两方 sighash 冲突 + CTV covenant 冲突的 signet 实证(节点 `testmempoolaccept` 权威判定 +
  上链 txid),就是 **blog2** 讲的内容;跑在 Bitcoin Inquisition signet 上。

*2026-07-02。数据样例与三方对拍见 `print_sighash_fields.py` 顶部注释。*
