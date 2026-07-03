# What a Bitcoin Signature Actually Signs

### You don't sign the transaction. You sign a message you assemble yourself — and the fields you leave out, anyone can change.

---

Ask a Bitcoin developer "what does a signature sign?" and most will say: *the transaction.*

They can't. When you sign an input, the transaction isn't finished — its txid depends on the very signatures you haven't made yet. You cannot sign a thing that doesn't exist. So what *do* you sign?

You sign a **message**. A specific, deterministic byte string, assembled out of *some* of the transaction's fields — the ones your **sighash flag** tells the protocol to include. In Taproot that message is the BIP-341 `TapSighash`. This message is the most important object in Bitcoin that almost nobody has looked at byte by byte. There's very little written about it, and even less code that just *prints it out*. So let's print it out.

We built two things to go with this post:

- a **playground** — flip the sighash dials in your browser and watch the fields light up or grey out, with the real digest recomputed live: [`index.html`](../index.html)
- a **field printer** — [`print_sighash_fields.py`](../print_sighash_fields.py), a self-contained Python script that assembles the message by hand and cross-checks every byte against `bitcoinutils`.

Everything below is real output from that script.

---

## The message, for a single input

Here is a plain 1-input, 1-output Taproot spend, signed with `SIGHASH_ALL`. This is the entire message your key puts its signature on:

```
👁 epoch              00
👁 hash_type          01
👁 nVersion           02000000
👁 nLockTime          00000000
👁 sha_prevouts       d60f3f6d…857d5f25   ← hash of ALL inputs' outpoints
👁 sha_amounts        184c0ede…b33b0270   ← hash of ALL inputs' amounts
👁 sha_scriptpubkeys  ba8a81ed…32421077   ← hash of ALL inputs' locking scripts
👁 sha_sequences      ad95131b…367bfd0e   ← hash of ALL inputs' sequences
👁 sha_outputs        af4d5d75…5c0b791f   ← hash of ALL outputs (the whole bill)
👁 spend_type         00
👁 input_index        00000000

TapSighash = 63e5c52ee032870b76d1e127767f4e8a0e388bbb336d048ffa3af02440a91c5d
```

That digest is what gets signed. Notice what's in here: **commitments to every input and every output of the transaction.** With `SIGHASH_ALL`, your signature nails the whole thing down. Change any output, add any input — the digest changes, and your signature is instantly invalid.

Think of the message as a **paper strip** of labeled cells. Signing is pressing your thumbprint over the cells you're willing to *see*. `SIGHASH_ALL` = you read the whole strip.

## The flag is a dial that greys out cells

Here's the same input, same transaction, signed with `SINGLE | ANYONECANPAY` instead:

```
👁 epoch              00
👁 hash_type          83
👁 nVersion           02000000
👁 nLockTime          00000000
🙈 sha_prevouts       (BLIND) ← ANYONECANPAY: you no longer see the other inputs
🙈 sha_amounts        (BLIND)
🙈 sha_scriptpubkeys  (BLIND)
🙈 sha_sequences      (BLIND)
🙈 sha_outputs        (BLIND) ← SINGLE: you don't commit to the whole output list
👁 spend_type         00
👁 outpoint           aaaa…aaaa 00000000  ← instead: just MY own input
👁 amount             a086010000000000
👁 scriptPubKey       225120…111111
👁 nSequence          ffffffff
👁 sha_single_output  af4d5d75…5c0b791f   ← only the ONE output paired with me

TapSighash = 7d193bd7c955f721d4757831b080b833a775dfd476882a438b69b745cbae53e4
```

Same transaction. Completely different message, completely different digest. The flag didn't change *what the transaction is* — it changed **what your signature looked at**. The greyed-out (`🙈`) cells are the fields you left **blind**. And here is the whole point:

> **A field you didn't sign is a field anyone can change after you sign — without breaking your signature.**

`ANYONECANPAY` blinded the "all inputs" cells → so other people can add their own inputs to this transaction and your signature still verifies. `SINGLE` blinded the output list → so other output rows can be added or reordered; you only locked the one paired with your input.

Blind is not a bug. Blind is a *feature you are choosing*: "I don't care about this part; someone else can fill it in later."

## Two dials, six flags — the whole space

There are only two independent choices, and each is a real field-group in the message:

- **INPUT dial** — do I commit to *all* inputs, or *only mine*?
  `default` (all) vs `ANYONECANPAY` (only mine). This is the `sha_prevouts / sha_amounts / sha_scriptpubkeys / sha_sequences` block appearing or being replaced by *this input's* own outpoint/amount/script/sequence.
- **OUTPUT dial** — do I commit to *all* outputs, *none*, or *only my paired row*?
  `ALL` / `NONE` / `SINGLE`. This is `sha_outputs` present, absent, or replaced by `sha_single_output`.

Two input-modes × three output-modes = **six flags**. That's the entire sighash matrix, and now you can see it's not six facts to memorize — it's two dials:

```
                 OUT: ALL          OUT: NONE         OUT: SINGLE
 IN: all         SIGHASH_ALL       SIGHASH_NONE      SIGHASH_SINGLE
 IN: only-mine   ALL|ANYONECANPAY  NONE|ANYONECANPAY SINGLE|ANYONECANPAY
```

Why does the input dial have only two positions while the output dial has three? Because your signature is *for* the input you're spending — you can never blind yourself to your own coin. The minimum is "at least mine." Outputs carry no such anchor, so they get a full "none" position. (There's no `SIGHASH_NONE`-for-inputs; it's structurally impossible.)

These corners aren't academic. They're how real protocols are built:

- **`ALL`** — the default. Lock everything.
- **`ALL | ANYONECANPAY`** — crowdfunding / assurance contracts. "The goal output is fixed; anyone can add money."
- **`SINGLE | ANYONECANPAY`** — the classic Ordinals / PSBT atomic swap. The seller signs *only* "my inscription goes in, my price comes out" and leaves everything else blind for the buyer to fill.

## Multi-input: this is where it gets interesting

With one input there's nobody else at the table. Add a second input — now two parties are co-signing one transaction, and the "all inputs" block (`sha_prevouts` and friends) is exactly the machinery by which one input's signature *reaches across* to commit to the others.

Sign input 0 of a 2-input transaction with `SIGHASH_ALL`:

```
sha_prevouts = d9ade445…b554b6c3a8   ← this now hashes BOTH inputs' outpoints
TapSighash(in0, ALL) = 781880953371345bbb9922cf0bb2e3aabaecb53ead5261c2a9ef784748137465
```

Flip on `ANYONECANPAY` and that `sha_prevouts` cell goes blind — input 0's signature stops caring who else is in the transaction. This single bit is the difference between "I'm locking exactly who pays" and "others can join." It is the entire basis of how independent parties cooperate — or collide — inside one Bitcoin transaction. (That collision has its own post: what happens when two inputs pick *incompatible* flags, proven on signet, is the sequel to this one.)

## Go press the dials yourself

Reading about it is one thing. Open [the playground](../index.html), flip `ANYONECANPAY`, and *watch* the four input-commitment cells grey out and the digest jump. Switch `ALL → SINGLE` and watch the output commitment collapse to a single row. The page computes real BIP-341 in your browser (self-contained SHA-256, no network) and self-tests its digests against the `bitcoinutils`-verified values — so what you see is real, not a cartoon.

Then read [`print_sighash_fields.py`](../print_sighash_fields.py) — 150 lines that assemble the message by hand and prove, byte for byte, that they match a production library. Once you've seen the message printed out, "what does a signature sign?" stops being a mystery and becomes a thing you can hold.

A Bitcoin signature doesn't sign the transaction. It signs a message you assemble — and everything you leave blind, you leave to someone else.

---

*This is a companion to the book **What a Signature Can See** — a Feynman-style walk from a dinner table to the exact edge of what a signature can commit to. Code and playground: [github/...]. Built and byte-verified on Bitcoin Inquisition signet.*
