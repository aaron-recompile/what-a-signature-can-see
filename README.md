# What a Signature Can See · 签名能看见什么

### 🔗 Live: **[sighash.bitcoincoding.dev](https://sighash.bitcoincoding.dev)** — read the book & play with the interactive SIGHASH playground

**How the conditions of a Bitcoin payment are defined — a Feynman-style idea-book, with an interactive playground you can actually touch.**

A Bitcoin signature doesn't sign "the transaction." It signs a *message* — the sighash — assembled from only the fields its flag chooses to **SEE (看)**. Everything left **BLIND (蒙)**, anyone can change after you sign. This little book walks from a dinner table to the exact edge of what a signature can commit to; the playground lets you flip the dials and watch the bytes.

There is very little written about the sighash message, and even less code that just *prints it out*. So this repo does both — and everything is byte-verified against a production library.

---

## What's here

| | |
|---|---|
| **`MANUSCRIPT_EN.md` / `MANUSCRIPT_CN.md`** | The book (English / 中文). Nine short chapters: a dinner → the paper-strip → covenants → *can you see your neighbour's note?* → copying it by hand → the wall. |
| **`APPENDIX_A_strip_game_CN.md`** | A print-and-play paper game — build it with paper and scissors, play it with a kid. The whole book, as seven levels. |
| **`sighash-playground/index.html`** | **The interactive playground.** A whole transaction laid out Sparrow-style; turn the two sighash dials and watch each field go SEE or BLIND; hit **✎ tamper** on any field to prove that changing a BLIND field is harmless and changing a SEE field kills your signature. Real BIP-341, self-contained SHA-256, **no network** — just open the file. |
| **`sighash-playground/print_sighash_fields.py`** | A Feynman-style field printer: single- → multi-input, the sighash message printed field by field, cross-checked byte-for-byte against `bitcoinutils`. |
| **`sighash-playground/blog/`** | Two technical blog drafts (*What a Bitcoin Signature Actually Signs* · *When Two Signatures Collide*). |

## Quick start

Open **`sighash-playground/index.html`** in any browser. Flip `ANYONECANPAY`, switch `ALL → SINGLE`, and tamper a field. That's the whole idea, in thirty seconds.

## Is it real?

Yes. The playground (JS), the field printer (hand-rolled Python), and `bitcoinutils` (a production library used to make signatures that were broadcast on signet) agree on **all 18 digests** (single-input × 6 flags + two-input × 2 inputs × 6 flags), byte for byte. The page also self-tests on load.

## Further reading (all public)

A companion signet series by the author, opcode by opcode:
[Anatomy of Bitcoin Scripts](https://medium.com/@aaron.recompile/the-anatomy-of-bitcoin-scripts-from-p2pkh-to-taproot-4db16924232f) ·
[OP_CAT](https://medium.com/@aaron.recompile/op-cat-on-signet-concatenation-commitment-and-bitcoin-inquisition-ed34a07866d6) ·
[OP_CHECKSIGFROMSTACK](https://medium.com/@aaron.recompile/op-checksigfromstack-on-signet-sign-anything-verify-on-stack-9cf70ab07583) ·
[OP_CHECKTEMPLATEVERIFY](https://medium.com/@aaron.recompile/op-checktemplateverify-on-signet-locking-outputs-at-utxo-creation-time-1d623fbe3899) ·
[SIGHASH_ANYPREVOUT](https://medium.com/@aaron.recompile/sighash-anyprevout-on-signet-when-signatures-stop-binding-to-utxos-eed4fc475668) ·
[all posts →](https://medium.com/@aaron.recompile)

Specs: [BIP-341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki) (Taproot sighash) · [BIP-143](https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki) (legacy sighash) · [BIP-342](https://github.com/bitcoin/bips/blob/master/bip-0342.mediawiki) · [BIP-119](https://github.com/bitcoin/bips/blob/master/bip-0119.mediawiki) (CTV) · [BIP-118](https://github.com/bitcoin/bips/blob/master/bip-0118.mediawiki) (APO) · [BIP-347](https://github.com/bitcoin/bips/blob/master/bip-0347.mediawiki) (OP_CAT) · [BIP-348](https://github.com/bitcoin/bips/blob/master/bip-0348.mediawiki) (OP_CHECKSIGFROMSTACK).
Where these run: [Bitcoin Inquisition](https://github.com/bitcoin-inquisition/bitcoin).

## License

Text and figures © the author. Code (playground + field printer) is MIT.

---

*Companion to the author's Bitcoin Inquisition signet series. `_internal/` is planning material and is not part of the publication (git-ignored).*
