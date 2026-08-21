# Divergences

Points where Malbolge implementations are known to disagree. Each says what
this oracle does and why.

**None of these is a claim that other implementations are wrong.** The
specification is a 1998 reference interpreter, not a standard document, and
several of these choices are defensible in more than one direction. What
matters for a control is that its position is fixed, stated, and pinned by a
test — so that a disagreement is a finding rather than a surprise.

---

## D1 — state after `v` (halt)

**This oracle:** returns immediately. The halting cell is not encrypted, and
neither `c` nor `d` advances.

**Some implementations:** run the tail of the interpreter loop after `v`, which
encrypts the halting cell and advances both registers.

**Why this position:** the reference interpreter's `case 'v': return;` exits the
switch *and* the loop before reaching the encrypt-and-advance tail at the
bottom.

**What it looks like when it bites:** two runtimes agree on every byte of
output, agree that the program halted, and disagree on the contents of exactly
one cell and on `c`/`d` by one. Comparing final memory across implementations
without accounting for this produces a false positive on every program that
halts.

**Pinned by:** `DivergenceTests.test_D1_execution_returns_immediately_on_halt`

---

## D2 — reserved

Kept so numbering stays stable across documents that already cite D1 and D3.

---

## D3 — `/` (input) at EOF

**This oracle:** sets `a = 59048`.

**Some implementations:** raise an error instead, treating exhausted input as a
condition the program should not continue past.

**Why this position:** the reference interpreter is explicit —

```c
if ( x == EOF ) a = 59048; else a = x;
```

**Independent corroboration:** an unrelated Rust implementation
([`sprang/malbolge-rs`](https://github.com/sprang/malbolge-rs), MIT, 2018) sets
`r_a = MAX_MEMORY - 1` on a zero-length read, with `MAX_MEMORY = 59049`. Running
its `cat` and `copy` sample programs with empty stdin emits the byte `168`
repeatedly, and `59048 & 0xFF == 168`.

That is evidence rather than proof — any value congruent to 168 modulo 256
prints the same byte — but it is a second implementation, by a different author,
in a different language, landing on the same rule.

**What it looks like when it bites:** a program that reads input runs to
completion under one runtime and aborts under another, with no difference in
the program itself.

**Note on non-termination:** with `a = 59048` rather than an error, a program
that loops on input does not stop at EOF. It keeps going. An implementation
without a step limit will run until killed. Any comparison involving `/` needs
a timeout, and a timeout is an inconclusive result — not a divergence.

**Pinned by:** `DivergenceTests.test_D3_input_at_eof_yields_59048`

---

## A trap that is not a semantic divergence

Worth recording because it looks exactly like one.

Implementations differ in how they *write* a byte:

| | For output value 168 |
|---|---|
| `putc( a, stdout )` — reference C | one byte: `a8` |
| `print!("{}", a as u8 as char)` — Rust | two bytes: `c2 a8` (UTF-8) |

For any output byte ≥ 128 these disagree on stdout while agreeing completely on
the machine state. It never shows up on hello-world, because printable ASCII is
below 128, where UTF-8 is one byte.

A differential comparison that treats stdout as bytes will flag this as a
divergence. It is not one: it is an I/O encoding difference, and it belongs in a
different bucket from anything about Malbolge itself.
