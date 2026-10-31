# SIGHASH playground

"What does a signature really sign?" — a playable, readable three-piece kit for the sighash message (BIP-341 TapSighash).
A companion to the book *What a Signature Can See*: it turns the book's SEE/BLIND paper strip into **real bytes + interactive + publishable**.

## The three pieces

| File | What it is | How to use it |
|---|---|---|
| **`index.html`** | Interactive page: two dials (input side ANYONECANPAY / output side ALL·NONE·SINGLE); watch live which fields are **SEE** / **BLIND**, with the digest computed on the fly | Just open it (pure front-end, built-in SHA-256, **no network needed**). Built-in self-test: the JS digests are compared against values verified with Python/bitcoinutils, and any mismatch shows a red warning |
| **`print_sighash_fields.py`** | A Feynman-style field printer: single input → multiple inputs, printing the SigMsg field by field + what each flag SEES/leaves BLIND. Also uses `bitcoinutils` as an oracle for a **byte-for-byte cross-check** | `python3 print_sighash_fields.py` (the printing part runs on any python3; the cross-check needs `pip install bitcoinutils`) |
| **`blog/`** | Two technical blog posts in English (in the author's Medium style) | `blog1_what_a_signature_signs.md` (teaches sighash + the page/code) · `blog2_when_two_signatures_collide.md` (collisions, with signet experiments) |

## Correctness guarantee (not mental math)

`index.html` (JS), `print_sighash_fields.py` (hand-rolled), and `bitcoinutils` (a production library) agree
on **single input × 6 flags + two inputs × 2 inputs × 6 flags = 18 digests**, byte for byte. The page also
runs its self-test when opened. So "the bytes you see are real".

## Two dials = six flags

```
                 OUT: ALL          OUT: NONE         OUT: SINGLE
 IN: all         SIGHASH_ALL       SIGHASH_NONE      SIGHASH_SINGLE
 IN: only-mine   ALL|ANYONECANPAY  NONE|ANYONECANPAY SINGLE|ANYONECANPAY
```
The input side has only 2 settings (you can't go BLIND on the coin you are spending), the output side has 3 → 2×3=6. The real name = "how much it SEES" in the toy.

## Publishing

- Blog: the two `blog/*.md` posts can be pasted straight into Medium (@aaron.recompile); remember to swap relative links for the deployed URLs.
- Page: `index.html` is a single file and can be hosted anywhere static (bitcoincoding.dev / GitHub Pages); the blog posts link to it.
- Sister experiment: the signet evidence for a two-party sighash collision + a CTV covenant collision (judged authoritatively by the node's `testmempoolaccept` +
  on-chain txids) is exactly what **blog2** covers; it runs on Bitcoin Inquisition signet.

*2026-07-02. For the sample data and the three-way cross-check, see the header comment of `print_sighash_fields.py`.*
