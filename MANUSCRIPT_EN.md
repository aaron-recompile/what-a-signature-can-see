# What a Signature Can See
## How the Conditions of a Bitcoin Payment Are Defined

*A book in the spirit of Feynman's QED.*

v0.1 · a Feynman-style idea-book · ships with an interactive playground and runnable code (see `sighash-playground/`)

---

## Preface · One Promise

This is not a book that teaches you to write code.

When you finish it you will not have memorized one more byte offset, nor one more BIP number. But you *will* completely understand a single sentence — short enough to write on a napkin, yet holding up the entire world of Bitcoin contracts:

> The conditions of a Bitcoin payment are the sum of what each signature can see and commit to.

Feynman wrote a slim book called *QED: The Strange Theory of Light and Matter*. In four lectures, with almost no equations, he made plain how light deals with matter — by leaning on one recurring scene (light striking a sheet of glass) and one little toy you could play with using a pencil (a small spinning hand, like a clock's). When you finished that book you couldn't compute quantum electrodynamics, but you *understood* it.

I want to take you, the same way, from **a dinner** to **a wall**.

Some names will show up along the road — sighash, covenant, CSFS, CAT, CTV, APO. Don't tense up. Here's my promise: I will not let them appear before you need them, and when they do appear I will explain them first in the language of the dinner table. Everything that truly grates — byte offsets, tagged hashes, preimage field tables — I have banished to the appendices. The body speaks only plain words.

Let's begin. Sit down; let's have dinner.

---

## Chapter 1 · A Dinner

Wang and Li had dinner together.

When it was over, the bill came. Three hundred, all told. How to pay? Maybe Wang puts in two hundred and Li one hundred; maybe they split evenly; maybe Wang just got paid and covers it all. However it's split, one thing is certain: **the "payment terms" of this dinner — who pays how much, where the money goes — are *fixed* by something.**

By what?

You might say: by the rules, by the bill. But look closely — the bill only says "three hundred total." It doesn't say who pays. What actually makes the money *move* is the moment Wang and Li each **nod**: Wang says "this two hundred, I own it," Li says "this one hundred, I own it." Both nod, and only then can the money go out. **One missing nod, and the bill goes unpaid.**

A Bitcoin transaction is almost exactly the same.

A transaction can have several **inputs** — think of each input as a person at the table, bringing some money. For the transaction to be valid, **every input must "sign and nod."** No central rule dictates how the money moves, no miner decides, no one's server decides — what defines the conditions of this payment is the thing **all the signatures jointly agree to**. One input refuses, and the whole transaction is void, just as one person refusing to pay leaves the dinner bill unpaid.

Now look down at the bill again. What's written on it is *dishes* — dish by dish, the price, whose pocket the money ends in. It says "🍜 this one, eight coins, to the restaurant."

But notice: **there is no line on the bill that says "of these eight, Wang put in five and Li three."** The restaurant doesn't care, and cannot see it. To the restaurant, the bill's **resolution** stops at "this dish, eight coins"; any finer — who chipped in how much for this dish — is your business under the table, and **the bill has no column for it.**

A Bitcoin transaction is exactly the same. The "dishes" on the bill are called **outputs**, each line saying only "how much, to whom." The money each person brings is called an **input**; the chain remembers Wang's coin is five and Li's is three (how much each brought *is* recorded) — but it will **never record** "of Wang's five, how many went to 🍜 and how many came back as change." The instant money enters this transaction it's as if **poured into one bowl**: total in equals total out (minus a small tip), but whose coin in the bowl this once was, which dish it flowed to — **that ledger the chain simply does not keep.**

Hold onto this. It's the first time in this book you bump into **a thing the chain cannot see** — not because it won't look, but because its ledger **doesn't go that fine.** This invisible **margin** comes back twice: once as the **wall** of Chapter 8; and once… that's another story — go ask the people who study privacy why a coin can hide its origins in the bowl.

This sounds simple, but it puts a deep question on the table:

> **If the "conditions of a payment" are jointly agreed to by the signatures, then what, exactly, did each signature agree to?**

Did it agree to "I put in two hundred"? To "this dinner is three hundred total"? To "Li must pay too"? At the moment it signed, **how much did it actually see**?

That is the question of this whole book. We will not ask "what does the protocol decree." We ask something humbler and deeper: **what does each signature see; what can it commit to on your behalf; and what is it that it cannot see.**

Hold that question. In the next chapter we sit down and watch which lines of the bill Wang actually reads before he signs.

---

## Chapter 2 · How Clearly You See the Bill

Before you sign, how carefully do you read the bill?

I've met three kinds of people.

The first reads the whole thing before signing. Every dish, every number, the total, whose pocket the money finally lands in — he reads it all, makes sure, then signs. His stance: "I own this bill end to end. **Change anything, and my signature is void.**"

The second reads only his own line. "What did my dish cost? Fine, I own that part, the rest is none of my business."

The third is the breeziest of all: when he signs, he simply doesn't care about anyone else. "I pay my share. Whether someone slides up later and adds a dish, whether the bill grows another diner — not my concern, my share stands."

Bitcoin gives every signature exactly this "how carefully" dial. Its name is **sighash** — *sig* for signature, *hash* for the digest it actually puts its mark on. This dial decides: **how much of the bill your one signature covers.** It has a few main settings:

- **See the whole bill** (called `SIGHASH_ALL`): every destination (output) is nailed down by your signature. Change one number, and the signature dies. The first kind of person.
- **Don't look at destinations** (`SIGHASH_NONE`): you've signed, but where the money goes you didn't watch; others may change it freely.
- **See only your own line** (`SIGHASH_SINGLE`): you answer only for your own corresponding destination. The second kind.
- **Don't care who else joins the table** (`ANYONECANPAY`): whether others add inputs to this transaction has nothing to do with your signature. The third kind.

Here I want to hand you a **toy** — the thing you'll get to keep in your hands for the rest of this book.

Picture a **long paper strip**. Printed across it, left to right, are labeled cells: version number, which inputs there are, which outputs the money goes to, the lock time… This strip is **the very thing you press your fingerprint onto when you sign** (its proper name is the *sighash preimage*, but we'll just call it "the strip").

And the "how carefully" dial does something wonderfully concrete: **it decides which cells of the strip you cover, and which you leave exposed, when you press your print.**

- See the whole bill: the whole strip is exposed; your print runs the full length.
- See only your own line: only the "your one destination" cell is exposed; the rest covered.
- Don't care who joins: cover the "which inputs there are" cells — so others adding inputs later leaves your print valid.

That's the whole secret of sighash: **a signature is not signed over the whole transaction, but over the cells of the strip you chose to expose.** What you expose, you commit to; what you cover, you cannot govern.

Now, a real cost.

In Bitcoin's history, the "see only your own line" setting had a famous bug. If you chose it but had **no** corresponding destination (your cell was empty), early implementations didn't error out — they quietly let you press your print on a **fixed, well-known constant**. And a fingerprint everyone knows? Anyone can copy it. Expose one fewer cell, see one place less, and an attack surface cracks open.

Remember this, because it's the first — and far from the last — time this book lets you touch its main thread:

> **What you can see, you can govern; what you cannot see is where risk and constraint come from.**

In the next chapter we bring a third character to the table — not Wang, not Li, but **the person who gave the money, and the note he pinned to it.**

---

## Chapter 3 · The Note From Dad

Where did the two hundred on Wang's side of the table come from?

Not out of thin air. His dad gave it to him a few days ago. And when he gave it, he attached a line — a whole **note**, even: "This money — spend it only on food, not on video games."

So from the moment it entered Wang's pocket, this money **carries a constraint**. Paying for dinner is fine (it fits the note), but if Wang wanted to spend that two hundred on something else, the note says no.

Bitcoin has exactly this thing, and its name is **covenant** — a pact, or just think of it as "the note the money carries."

To understand it, you first need to know what Bitcoin money looks like. The "balance" in your wallet is really money in separate, **as-yet-unspent** chunks (each chunk is called a UTXO). And every such chunk is not a bare number — it **carries a little rule** stating "to spend me, here's what you must satisfy." The commonest rule is "prove you hold the private key." But the rule can be written finer.

How fine? Fine enough to dictate **how this money may next be spent.**

This is the crucial turn. An ordinary note says only "you need the key to spend"; a covenant note says: "you may spend, **but the money you spend must go to a designated place.**" Note that this constraint **is not set on the fly by the signer** — the money **carries it inherently**, written in by the previous hand. Wang cannot tear off his dad's note, just as this bitcoin cannot shake off the rule the previous hand engraved upon it.

By now there are really **two distinct forces** on the table, and together they define a payment's conditions:

- One is **sighash** — last chapter — **how clearly a signature sees the bill**. The force of *seeing*.
- One is **covenant** — this chapter — **what prior constraint the money carries**. The force of *binding*.

Whether a payment can happen, and what it looks like, is the **composition** of these two forces. One governs how much you see, the other how tightly you're bound.

Nearly the whole rest of this book does one thing: **push these two forces to their limits, and see how complex a constraint they can compose — and what they cannot.**

In the next chapter we push the *binding* force first. Because dad's note is fiercer than you think — it doesn't stop at this one dinner.

---

## Chapter 4 · The Note That Follows the Money

That note from last chapter was still too gentle. It governed only Wang's one dinner.

A truly fierce father writes it like this: "The restaurant may take this money — **but once the owner has it, he too may only buy ingredients, nothing else.**" Do you see the difference? This note constrains not just Wang; it **travels with the money**, binding the next hand, and the hand after that. Wherever the money flows, the note's rule sticks.

This is a **recursive covenant** — the constraint copies itself, passed hand to hand along the money. Many of Bitcoin's most interesting constructions — like **vaults** (a safe-deposit-box structure where even a stolen key can't carry the money off) — are built on it.

So, technically, how do you make a note "govern the next hand"?

Enter a new character, **CTV** (full name OP_CHECKTEMPLATEVERIFY, but the name is useless — remember what it does). In dinner-table terms, CTV does this: **it takes a photograph in advance of exactly what this money's next move must look like, and nails that photo to the note.** Whoever spends this money must make the transaction look identical to the photo — same destinations, same structure — or it won't spend.

To make it recursive, just have that photo **require the next hand to wear the same note too**. And so the constraint copies itself onward: the photo on the restaurant owner's money again reads "your next hand may also only buy ingredients"… link after link.

Now take out that **strip** and play.

How does CTV "take a photo"? It doesn't really photograph; what it does is take the "which outputs the money goes to" **cells** off the strip, **trace** them, knead them into one unique **fingerprint** (a hash), and nail that fingerprint into the spending rule. Anyone who later wants to spend must produce the "where the money goes" cells on the spot, trace them again, and **match the fingerprint** — match and pass, mismatch and forget it.

Please remember one small thing, because next chapter it comes back: **in this entire process we used only "trace + match fingerprint" — not a single signature.** CTV forces the money's destination by whether a hash matches, not by who signed.

This chapter, the *binding* force has been pushed quite far — money can be told where to go next, and that command can even be passed down the line.

But.

So far, every force we've used has been spent on **one person, himself**: Wang reads his own bill (sighash), Wang carries his own dad's note (covenant), Wang's money has its destination nailed (CTV).

Li is still sitting at the table.

Can Wang see **Li's** note?

That one question is the turn of the whole book. See you next chapter.

---

## Chapter 5 · Can You See Your Neighbor's Note?

Wang has a quiet doubt.

That hundred Li pulled out to chip in — **is it clean?** Is it money Li's dad properly gave him, money carrying its own honest note, or cash Li lifted from somewhere, of murky origin?

At a real table this is easy. Wang turns and asks: "Hey, where's this from — show me your note?" Li hands it over, Wang takes a look, and now he knows. **Face to face, two people can see each other's constraints.**

But in Bitcoin — **Wang cannot see it.**

This is a sentence you must stop and stare at for three full seconds. Bitcoin's execution rules carry a deep, almost counter-intuitive limit:

> **One input cannot see the other inputs in the same transaction.**

Wang's input, when it signs and checks its own rules, **has no way to read** which money Li's input spends, what note it carries, what rule governs it. Each person can only look down at his own dad's note, and looking up, **sees only the shared bill in the middle of the table (all the outputs — where the money went in total)** — but he **cannot see the note clenched in his neighbor's hand.**

This capability — "can one input see and inspect another input" — has a name: **cross-input introspection**. And Bitcoin **natively has none of it.**

Feel how wide this crack is.

In the four chapters before, we pushed *seeing* and *binding* pretty far: the bill seen clearly (sighash), money carrying a note (covenant), destinations nailed and even passed onward (CTV). But look back and you'll find **all of these forces were spent on the "output side" and on "oneself"** — governing "where the money goes" and "what I myself am bound by." The moment the question becomes "can I inspect **the input sitting next to me**," Bitcoin throws up its hands: cannot.

So the situation at the table is really this:

- **Cooperation**, on the output side, is solved. "Our money together must be ≥ this dinner, and must pay only this restaurant" — that kind of shared-destination constraint, the earlier forces can lock.
- **Mutual inspection**, on the input side, is still a **gaping hole**. "I want to confirm Li is also under his dad's rule, not chipping in dirty cash" — that neighbor-to-neighbor check, Bitcoin natively cannot do.

This gaping hole is the entire battlefield of the next three chapters.

Next chapter, a sly trick: since Wang can't peek at Li's note directly, can we… **have Li read his note aloud, and let Wang copy it out and verify it by hand?**

---

## Chapter 6 · Copying the Note by Hand

Wang can't read Li's note directly. Fine. Let's try another way.

**Have Li read out every word of his note, one by one, laid flat on the table. Then Wang takes his own sheet, copies it out, and checks by hand: does the signature on this note check out?**

Roundabout, yes. But savor it — this trick actually **verifies**. Wang has no superpower to "see" Li's note, but as long as Li lays the contents out, Wang can rebuild it himself and check it himself.

This chapter is about pulling off that trick in Bitcoin. It needs two tools.

The first is **CAT** — its talent is laughably simple: **join two stretches of bytes into one.** Give it two pieces, it glues them into one. Sounds dull, but "gluing the words Li reads out, piece by piece, back into a complete note" runs on exactly this.

The second is **CSFS** (OP_CHECKSIGFROMSTACK). To explain it, meet its elder, OP_CHECKSIG. Ordinary signature checking uses OP_CHECKSIG, and it's a **black box**: you hand in the signature, and it assembles the strip-to-be-signed by its own rules **internally**, checks it itself — you can't reach in, and you can't see what it assembled. CSFS is a **glass box**: it says, "what signature do you want checked? **Hand me the note to be signed, and I'll check it.**" It takes the decision of "what content should be signed" out of the protocol's hands and into **yours**.

Put the two tools together and the sly trick stands:

> Have Li lay the fields on the table as evidence (push them into the witness), have Wang use **CAT** to **glue those fields back into a complete strip**, then use **CSFS** to check the signature against the strip he assembled with his own hands. **Hand-copied introspection — done.**

The power of this trick is that it can **forge by hand the effects of those "native" capabilities.** Two examples:

- **Want to mimic that special "signature doesn't bind a specific source" capability** (its proper name is APO / ANYPREVOUT)? Easy: when you glue the strip, **deliberately leave the "where exactly this money came from" cell out.** A strip missing that cell, signed, naturally doesn't bind the source. Put plainly, APO is nothing but "the standard strip with one cell snipped out" — and this hand-copy trick can glue whatever cells it likes from the start.
- **Want to mimic CTV's "nail the destination" trick?** Also easy: glue the "where the money goes" cells, take a fingerprint, compare it to the nailed value. — And notice: here you barely even need CSFS; CAT to glue, a fingerprint, a compare, and you're done. That half of CTV is pure "glue bytes + match fingerprint."

This has a proper name: **capability parity** — **this hand-copy trick (CAT+CSFS) can simulate the constraints that APO and CTV impose.** It is the hardest result on Wang's line: relying not on a native capability the protocol hands you, but purely on laying out fields, re-gluing by hand, verifying by hand, he reaches them.

Now run the strip toy at full power. The whole essence of this trick is to **cut the strip along its fields and recombine**: pull the "source" cell and you get APO; keep only the "destination" cells and fingerprint them and you get CTV; glue whatever cells you like and you get an **arbitrary, custom strip.** Hand-copying turns "introspection" from a superpower you don't have into a piece of **handiwork.**

But I owe you honesty — that's this book's rule — about what this trick is **not**.

It is "**simulating the effect of the constraint**," **not** an engineering "**replacement**." Li reading his whole note aloud onto the table has a cost: the longer the note, the more crowded the table (the witness data is bigger, costlier), and ultimately this is still "make the spender lay out the fields and then check them," not a pair of eyes that grew in to read directly. So you may say Wang "hand-copied the same effect," but don't think it's engineering-identical to the native capability. **The effect is approached; the cost and the means are not the same.** Keep this measure in mind — the next chapter and the last both use it.

This chapter has on-chain proof: Wang really did use CAT+CSFS to hand-forge the strip that "nails the destination," and that transaction sits on-chain; the byte-level dissection I've put in the appendix.¹

The next chapter is lighter. We can hand-copy now — so let's look at a fun fact: **the same goal often has more than one road to it.**

---

## Chapter 7 · Two Roads, Same Place

There's a game at the table that shows off the finesse of Bitcoin contracts especially well, and it's called **Eltoo** (also Lightning Symmetry).

The problem it solves is this: Wang and Li want to open a long-running "shared ledger," transferring back and forth and updating their balances repeatedly, and — here's the key — **at any time, a newer state can override an older one.** If anyone tries to cheat by settling on an old ledger that favors them, the other can always slap down a newer ledger that covers it. This is the lifeblood of layer-two networks like Lightning.

The interesting part: to set this "always re-openable" game on the table, there's **more than one way to lay it out.**

- **The first layout** leans on that "signature doesn't bind the source" capability from last chapter (APO). Because later states can rebind to any prior state, updating is flexible. This road Wang actually ran on-chain — **six transactions, three states**, a complete state chain.²
- **The second layout** uses no APO at all, switching to the **CSFS + CTV** combo from the hand-copy line. It plays a neat interlock: have a signature sign a CTV fingerprint, and have that fingerprint appear a second time in the witness; the two bite together and the state locks. This road is leaner — **two transactions, three states**, and it's done.³

See — **the same destination, two completely different roads.** One six transactions, one two; one with APO, one with CSFS+CTV. The endpoints are identical — a shared ledger you can refresh at any time — but the routes run opposite ways.

Here is a truth often confused, and worth a lifetime's remembering:

> **A protocol is not an opcode faction.**

People out there love to argue "should we ship APO or CTV," fighting as if picking one betrays the other. But Eltoo shows you plainly: Eltoo is a **goal**, not the private property of one opcode. There are several roads to that goal; opcodes are merely different **routes**. What you should care about was never "which opcode wins," but "**can the constraint I want be reached; if so, by how many roads; and what does each road cost.**"

This is exactly the ruler this book wants to put in your hand — **don't take sides; measure capability.**

(This chapter owes thanks to one person: Christian Decker, who answered Wang in a public thread; that reply is itself a side-proof that this all stands up.)

We've climbed high now. We can hand-copy, and we've seen more than one road.

So it's time to go hit the wall. Next chapter we go find a thing that **no amount of hand-copying can forge.**

---

## Chapter 8 · The Wall

Wang has gotten hooked on hand-copying. He's starting to believe that as long as the other party lays the fields on the table for him to re-glue and re-check, **there's no constraint he can't forge.**

This chapter I'll make him hit the wall. And I'll make you **see with your own eyes why this wall is here, and why there's no going around it** — this is the intellectual climax of the book, so please read slowly.

What Wang wants is these two things, both sounding reasonable enough:

- One is **co-spend**: "**For my share of money to spend, Li's share must be spending on the table at the same time.**" And he wants the **rule itself to enforce it**, not relying on Li's cooperative signature — so that even if Li is unwilling, the rule forces this transaction to carry Li's share.
- The other is **value conservation**: "**The total going out must equal exactly the total coming in, minus a fixed tip.**" Not a cent more, not a cent less, nailed down by the rule.

Wang rolls up his sleeves for the old method: have the other party lay out the fields, and I'll re-glue and re-check.

**He fails. However he tries, he cannot forge it.**

Why? This is where I want you to slow down. The answer is not "he isn't clever enough." The answer is a **structural, mathematical deadlock**:

Recall Wang's whole hand-copy move — the note he can check is **one he assembled himself.** And with what does he assemble it? Only with the **fields laid on the table, the ones he can see.** In other words, **the note in Wang's hand is a function of "the things he can see."**

So what about the things he **cannot** see? — say, exactly which source Li's money came from, exactly how much that money is. Those fields are **not laid on the table; Wang cannot touch them at all.** And since he can't touch them, they **never enter the note Wang assembles.**

Here's the deadlock:

> Suppose two transactions whose **only difference** is "whether Li's share is present."
> Because Wang assembles his note entirely from fields he can see, and "whether Li is present" is something he cannot see —
> the note Wang assembles for the two transactions is **identical.**
> Same note, same signature check. **Wang can never tell the two transactions apart.**

And since he **can't tell them apart**, he **can't let one through and block the other.** But co-spend wants exactly that: let "Li present" through, block "Li absent." Wang can't distinguish, so the rule can't enforce.

**This is the wall.** It is not a fence you could clear with one more push; it is a **logical hard line**: a function can never depend on an input it cannot read. What you cannot see, the note you assemble is indifferent to; and what your note is indifferent to, you are forever powerless over. Value conservation dies on the same deadlock — that "how much money" number can't be laid on the table, can't be read out in the clear, so it too can't enter the note, so you too can't conserve it.

Remember the **bowl** from Chapter 1? That's the same wall, an earlier brick of it. Pour money into the bowl and the ledger of "whose coin this was, which dish it flowed to" was never kept — the chain doesn't go to that **margin**. So even if today you wanted a rule "this dish must be Li's money," there is nothing to build on: that fact **never existed**, no cell on the chain holds it, and the note you assemble naturally can't touch it. **Sometimes you can't govern a thing because it simply isn't on the books.**

This can be **rigorously proved** — not "I tried for hours and failed," but "I can prove **no one could possibly succeed.**" Its shape:

> Every constraint you can check is a function of "the fields that can be laid on the table";
> any field that cannot be laid on the table, the constraint is necessarily indifferent to;
> therefore any two transactions differing only in such fields are necessarily indistinguishable, and cannot be treated differently.

Back in Chapter 6 we proved hand-copying is "**strong enough**" — strong enough to simulate APO and CTV. This chapter we prove the other half, the more valuable half: hand-copying is "**exactly** strong enough" — **its capability boundary stops precisely at this wall.** (A semi-formal version of the wall is in the appendix⁴, and it is also the heart of Wang's formal-methods paper.)

Now, please, in Feynman's favorite spirit, look at this wall **with delight, not dejection.**

Because this wall is **not a defect of CAT+CSFS at all.** It is the **grammar boundary of the sighash language itself.** It says something deep: in Bitcoin, **what you can commit to is exactly what you can see; you cannot see the note in your neighbor's hand, so some constraints can never be hand-forged.**

And — the loveliest point — **that "nail the destination" CTV cannot clear this wall either.** Co-spend, value conservation — CTV can't do them either. So this wall is not a "who's stronger" matter; it isn't between Wang and anyone else, **it's under everyone's feet.** What it draws is the very edge of the earth for "what a signature can see."

By now you should truly understand that napkin sentence from the opening:

> The conditions of a Bitcoin payment are the sum of what each signature can see and commit to.

You've now touched both ends of it. One end is Chapter 6 — **whatever can be seen and laid on the table, hand-copying can commit to.** The other end is this chapter — **whatever cannot be seen, no one can commit to.** The line between them is this wall.

In the last chapter we step out of the restaurant and listen to the grown-ups arguing at the door. You'll find that the thing they've argued about for years is really just **whether this wall should have a window cut into it.**

---

## Chapter 9 · The Grown-Ups Are Arguing About How Detailed the Note Should Be

Step out of the restaurant, and at the door stands a crowd of grown-ups, arguing fiercely.

Lean in and you'll find they're arguing about the very thing you just worked out at the dinner table — **how detailed should the note be allowed to get?**

Some say the note should be able to say "**someone must pay together with you**" (isn't that just Wang's co-spend?). Some say it should say "**this money can't exceed this amount**" (isn't that just value conservation?). And some say don't open it that far — too detailed a note will cause trouble.

You can follow this fight now. What they're arguing over is not the name of any opcode. They're arguing over something more fundamental:

> **Do we, or do we not, let signatures see a little more?**

Because you understand Chapter 8's wall now: Wang can't forge co-spend, can't forge value conservation — **not for lack of skill, but because he cannot see his neighbor's note.** To clear that wall there's only one road — **fit Bitcoin with a new pair of eyes**, so one input can read another input's source and amount directly. These "new eyes" are exactly what those proposals out there are fighting over (they have a pile of names — OP_VAULT, CCV, INSPECTINPUT and such, and it doesn't matter whether you remember them). What they want to grant is **precisely the capability CAT+CSFS cannot — to see the neighbor's note.**

So you can file all these arguments neatly into one box. Every covenant proposal is, at bottom, picking a position on three dials:

- **How much can you see** (which fields can be introspected)?
- **How much can you bind** (which constraints can be nailed)?
- **Can you hand it off** (can the authority be delegated)?

Each proposal **picks one corner to stand in** the space these three dials make. The fight is over which corner. No corner is inherently right — each has its cost: the wider the window you open, the finer the note you can write, but the more trouble you take on too.

Now I **hand the opening sentence back to you.** It is no longer a slogan I wrote on a napkin and asked you to memorize — it is a truth you **earned by hand, chapter by chapter**:

> **The conditions of a Bitcoin payment are the sum of what each signature can see and commit to.
> And the covenant debate, argued for years, comes down to one question:
> do we let signatures see a little more?**

The book should close here. But I don't want to give you a full stop; I want to give you a **ruler.**

From here on, Bitcoin will sprout new proposals, new opcodes, new fights. You needn't take any side. Just take out this ruler and ask three questions: **what does this new thing let signatures see more of? Therefore what can it bind more of? In that three-dial space, which corner does it stand in?**

Answer those three, and you'll see clearer than most of the people arguing.

And "seeing clearer," from that first-page dinner to now, **has been the only thing this book was ever about.**

---

## Appendices

### Appendix A · The Cut-Out Sighash Strip

Draw the BIP-143 / BIP-341 sighash-preimage fields as a one-page physical strip, with cut lines printed along the fields. Readers can actually cut it out and play in Chapters 2, 4, and 6: cover some cells (sighash flag), pull the source cell (APO), fingerprint only the destination cells (CTV). The offset table the body kept dodging becomes, here, a piece of handiwork.
*(Figure to be added at book stage.)*

### Appendix B · On-Chain TxIDs (public)

The transactions cited in the body all live on **Bitcoin Inquisition signet** (a public signet where these not-yet-mainnet opcodes actually run). Full hashes and step-by-step walkthroughs are in the author's **public write-ups**:

- Ch.6 · CAT+CSFS hand-forged output binding (`2f3451…`) → [OP_CAT + OP_CHECKSIGFROMSTACK on Signet](https://medium.com/@aaron.recompile/op-cat-op-checksigfromstack-on-signet-dynamic-message-oracle-authorization-8c73e1ef5353)
- Ch.7 · APO-road Eltoo, six-tx state chain (`386dbb6a…` et al.) → [SIGHASH_ANYPREVOUT on Signet](https://medium.com/@aaron.recompile/sighash-anyprevout-on-signet-when-signatures-stop-binding-to-utxos-eed4fc475668)
- Ch.7 · CSFS+CTV-road Eltoo (`92efc475…`, `b96324da…`) → [OP_CHECKTEMPLATEVERIFY on Signet](https://medium.com/@aaron.recompile/op-checktemplateverify-on-signet-locking-outputs-at-utxo-creation-time-1d623fbe3899)
- Ch.8 · sha_prevouts input-side binding (`7311da…`) → the signet lab code in Appendix D

Inquisition is a custom signet with no general block explorer; the public posts above are the authoritative record of these transactions.

### Appendix C · For the Curious: The Real Byte Offsets

The hard things the body banished here: the field order and offsets of the BIP-143 preimage, the tagged-hash construction of Taproot (BIP-341), the byte ranges of sha_outputs / sha_prevouts / sha_amounts, midstate details.

But the fastest route is to **open the interactive playground** (`sighash-playground/index.html`): it assembles these fields live in your browser, greys them SEE vs BLIND as you turn the dials, recomputes the digest instantly — and it is byte-verified against `bitcoinutils`. Specs: [BIP-341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki), [BIP-342](https://github.com/bitcoin/bips/blob/master/bip-0342.mediawiki), [BIP-143](https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki).

### Appendix D · Further Reading (all public)

This book carries one idea and skips the details. To go deep on each opcode, the author has a full **public signet series**, mapped chapter by chapter:

- Ch.2 · sighash & the shape of Script → [The Anatomy of Bitcoin Scripts: From P2PKH to Taproot](https://medium.com/@aaron.recompile/the-anatomy-of-bitcoin-scripts-from-p2pkh-to-taproot-4db16924232f)
- Ch.3 / 4 · covenants, recursion (CTV) → [OP_CHECKTEMPLATEVERIFY on Signet](https://medium.com/@aaron.recompile/op-checktemplateverify-on-signet-locking-outputs-at-utxo-creation-time-1d623fbe3899)
- Ch.6 · copying the note (CSFS + CAT) → [OP_CAT on Signet](https://medium.com/@aaron.recompile/op-cat-on-signet-concatenation-commitment-and-bitcoin-inquisition-ed34a07866d6) · [OP_CHECKSIGFROMSTACK on Signet](https://medium.com/@aaron.recompile/op-checksigfromstack-on-signet-sign-anything-verify-on-stack-9cf70ab07583) · [OP_CAT + OP_CHECKSIGFROMSTACK on Signet](https://medium.com/@aaron.recompile/op-cat-op-checksigfromstack-on-signet-dynamic-message-oracle-authorization-8c73e1ef5353)
- Ch.7 · Eltoo / signatures that don't bind to a UTXO (APO) → [SIGHASH_ANYPREVOUT on Signet](https://medium.com/@aaron.recompile/sighash-anyprevout-on-signet-when-signatures-stop-binding-to-utxos-eed4fc475668)
- whole-book "commit-reveal" backdrop → [Commit-Reveal vs Dual-Layer Scripts](https://medium.com/@aaron.recompile/commit-reveal-vs-dual-layer-scripts-the-real-architecture-of-bitcoin-script-665a79b0bd34)

All of the author's public writing: <https://medium.com/@aaron.recompile>

**Specifications (BIPs):** [Taproot sighash BIP-341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki) · [Tapscript BIP-342](https://github.com/bitcoin/bips/blob/master/bip-0342.mediawiki) · [legacy sighash BIP-143](https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki) · [CTV BIP-119](https://github.com/bitcoin/bips/blob/master/bip-0119.mediawiki) · [APO BIP-118](https://github.com/bitcoin/bips/blob/master/bip-0118.mediawiki) · [OP_CAT BIP-347](https://github.com/bitcoin/bips/blob/master/bip-0347.mediawiki) · [OP_CHECKSIGFROMSTACK BIP-348](https://github.com/bitcoin/bips/blob/master/bip-0348.mediawiki)

**Where it runs:** [Bitcoin Inquisition](https://github.com/bitcoin-inquisition/bitcoin) — a public signet carrying these not-yet-mainnet opcodes.

**Interactive + code:** this book's companion **sighash playground** (turn the dials, watch SEE vs BLIND, and *tamper* a field to prove it) and the single→multi-input field printer, both under `sighash-playground/`.

---

*v0.1 complete. English edition; Chinese edition in `MANUSCRIPT_CN.md`. Companion playground and code under `sighash-playground/`.*
*The body carries zero code and zero internal references; every further resource — opcode deep-dives, BIPs, on-chain transactions — is a public link, in Appendices B / C / D.*

---
¹ See Appendix B. Full step-by-step walkthrough in the public post [OP_CAT + OP_CHECKSIGFROMSTACK on Signet](https://medium.com/@aaron.recompile/op-cat-op-checksigfromstack-on-signet-dynamic-message-oracle-authorization-8c73e1ef5353), and the companion playground (watch sha_outputs get assembled in your browser).
² See Appendix B (APO-road Eltoo, six transactions).
³ See Appendix B (CSFS+CTV-road Eltoo, two transactions).
⁴ See Appendix C and the companion playground; this wall (the separation result) can be taken further into a machine-checked theorem.
