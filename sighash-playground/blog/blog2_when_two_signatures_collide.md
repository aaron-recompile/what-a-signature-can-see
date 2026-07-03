# When Two Signatures Collide

### Two parties, two sighash flags, one transaction. We made them fight on Inquisition signet and let the node judge.

---

In the [previous post](./blog1_what_a_signature_signs.md) we saw that a Bitcoin signature doesn't sign the transaction — it signs a *message*, assembled from only the fields its sighash flag chooses to see. Everything left blind, anyone can change.

That raises a sharp question the moment more than one party is involved:

> If each signature only commits to *its own* view of the transaction, what happens when two parties in the same transaction pick **incompatible** views?

Do they conflict? Can the transaction still be built? We didn't want to argue it on a whiteboard. We built it on **Inquisition signet** and asked the node — with `testmempoolaccept`, which returns Bitcoin Core's own verdict (`allowed` / rejected + the exact reason), no hand-waving.

Here's the mental model the experiments confirm.

## Signatures don't negotiate. They intersect.

Each signature carves out a **set of final transactions it will accept**: the fields it *sees* are pinned to fixed values; the fields it leaves *blind* can be anything. Put two parties in one transaction and the valid transaction must lie in the **intersection** of both their accepted sets.

- **Intersection non-empty** → a transaction exists that satisfies both → the node accepts. *Cooperation.*
- **Intersection empty** → no such transaction exists → the node rejects. *Conflict.*

And crucially: the two inputs never read each other's flags. They only both touch the *shared transaction*. A conflict is not two parties arguing — it's two commitments to the same field that can't both be true at once.

We ran three collisions.

## Collision 1 — same field, two values → deadlock

Alice signs `SIGHASH_ALL` believing the outputs are **O1** (all funds to her). Bob signs `SIGHASH_ALL` believing the outputs are **O2** (all funds to him). Now try to assemble the final transaction:

- Build it with outputs **O1** → Bob's signature was over O2 → invalid.
- Build it with outputs **O2** → Alice's signature was over O1 → invalid.

There is no output set that satisfies both. The node, on both assemblies:

```
allowed = false
reject-reason: mempool-script-verify-flag-failed (Invalid Schnorr signature)
```

Two `SIGHASH_ALL` signatures over different bills = empty intersection = a transaction that **cannot be built**. This is the base case of conflict, and the node states it flatly.

## Collision 2 — offered freedom, quietly revoked

This one is subtler and more real. Alice signs `ALL | ANYONECANPAY` — "anyone can add inputs, I only commit to my own." She is *offering freedom*: others may join and pay. Bob signs plain `SIGHASH_ALL` — which commits to the **entire input set** as it stood when he signed.

- With exactly `{Alice, Bob}` as inputs → both valid → **accepted**.
- Now Carol actually *uses* Alice's offered freedom and adds herself as a third input. Alice's `ANYONECANPAY` signature doesn't care (she only committed to her own input) — but Bob's `SIGHASH_ALL` was over `{Alice, Bob}`, and the input set is now `{Alice, Bob, Carol}`:

```
allowed = false
reject-reason: mempool-script-verify-flag-failed (Invalid Schnorr signature)
```

Bob's signature shatters. **The freedom Alice offered was only real as long as nobody else locked the input set.** The instant one party commits to "all inputs," the door another party held open slams shut — using it destroys the transaction. (Control: when *both* Alice and Bob use `ANYONECANPAY`, Carol joins fine → accepted. So the rejection is provably Bob's `ALL`, nothing else.)

This is the exact texture of multi-party PSBT flows: the party who signs "all inputs" must sign **last**, or watch their signature die every time the input set changes.

## Collision 3 — a covenant vs. a spender's intent

Sighash is one way to fix a field. A **covenant** is another — and it can collide too. We locked a coin with `OP_CHECKTEMPLATEVERIFY` (CTV): the covenant fixes the outputs of the *next* spend to an exact template T ("50000 − fee to address X, one input, one output").

- Spend it exactly as T → **accepted**.
- Spend it to a *different* recipient (address Y) → the covenant and the spender's intent have empty intersection:

```
allowed = false
reject-reason: mempool-script-verify-flag-failed
              (Script failed an OP_CHECKTEMPLATEVERIFY operation)
```

- Spend it with a *different amount* → same rejection.

The covenant nails the "where the money goes" cell shut at funding time. Any spender who wants it elsewhere is refused — and the opcode names itself in the rejection. This is a covenant-vs-party conflict: the coin's issuer pre-committed one field, and no later signature can un-commit it.

## Conflict is sometimes exactly the point

It's tempting to read "conflict" as failure. It isn't. The base case (Collision 1) is the machinery behind **atomic swaps**: a buyer who tries to take the goods without paying must build a transaction missing the seller's payment output — but the seller's `SINGLE | ANYONECANPAY` signature commits to *exactly that output*. Empty intersection → the theft can't be assembled → goods and money move together or not at all. The conflict *is* the lock that makes trustless swaps work.

## The receipts

All verdicts are Bitcoin Core's own, via `testmempoolaccept`, on Inquisition signet. The two cooperating cases we also broadcast, as permanent on-chain artifacts:

- **Two-party cooperation** (both `ALL`, compatible outputs): `5ec7a5244454f00200224f06290d084150c597109cff119e86196be968aab2ba`
- **Covenant satisfied** (CTV spend matching template): `a346a1c892a53dca4e6cea287337e14811f313eec04d37b13435a53b2e66ca29`

The full runnable lab — `run_A_sighash.py` (two-party sighash) and `run_B_covenant.py` (CTV) — reproduces every verdict against a live node.

---

So: two signatures in one transaction don't bargain. They **intersect**. Land inside the overlap and the node accepts; land outside it and the node refuses — sometimes because two parties wanted the same field to be two things, sometimes because one party's covenant already spoke for it. The conditions of a Bitcoin payment are the sum of what every signature can see — and a conflict is just two of those views, touching the same cell, disagreeing.

---

*Sequel to "What a Bitcoin Signature Actually Signs." Both accompany the book **What a Signature Can See**. Play with the sighash dials: [`index.html`](../index.html). Reproduce the collisions: the sighash-conflict lab on Inquisition signet.*
