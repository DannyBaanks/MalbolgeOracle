# malbolge-oracle

**An independent execution control for Malbolge.**

Not another interpreter to run your programs with — a *control*: a runtime
written to implement the reference semantics literally, so other
implementations can be checked against something that shares no ancestry with
them.

```python
from oracle import Oracle

machine = Oracle()
machine.load_ascii("(=<`#9]~6ZY32Vx/4Rs+0No-&Jk)\"Fh}|Bcy?`=*z]Kw%oG4UUS0/@-ejc(:'8dc")
result = machine.run(max_steps=1_000_000)

result.output       # 'Hello World!'
result.halted       # True
result.halt_reason  # 'halt_opcode'
result.steps        # 40
result.a, result.c, result.d
result.memory       # all 59049 cells
```

No dependencies. Python 3.10+, standard library only.

## Why a control rather than an interpreter

Malbolge implementations disagree with each other in ways that are invisible
until you compare them. Not on hello-world — on what happens at EOF, on what
state the machine is in after it halts, on whether an out-of-range cell is a
crash or a no-op.

Comparing two interpreters that were written by reading each other tells you
little. This one was written from the reference semantics and nothing else, so
when it disagrees with a runtime, the disagreement is informative.

It reports the full machine state after a run — registers, step count, halt
reason and all 59 049 cells — because a control that only tells you what got
printed cannot help you find out *why* two implementations differ.

## Provenance

The semantics were transcribed from the interpreter pseudocode in **Iizawa
(2005), Appendix C** ("Malbolge インタープリタ 実行部").

That pseudocode is itself a transcription of the **reference interpreter** for
the language: 13 of its 19 lines appear verbatim in the reference `malbolge.c`
that has circulated publicly since 1998 — including every decisive one: the
`xlat1` decrypt, the ternary rotate, and the EOF rule. So the primary source is
the reference interpreter; Iizawa is where it was read.

The translation tables (`xlat1`/`xlat2`) and the `op`/`rot` primitives are
public constants of the Malbolge specification and are declared here
independently.

**No other Malbolge implementation was consulted, reused or copied while
writing this module.** That is the whole value of it.

## Divergences

Where implementations are known to disagree, this one takes a position and says
so. See [`DIVERGENCES.md`](DIVERGENCES.md) — currently two, both pinned by
tests.

## Tests

```sh
python -m pytest test_oracle.py -v      # or: python test_oracle.py
```

17 tests, no dependencies. They check the oracle against facts established
independently of any runtime: the published table shapes, the arithmetic of the
ternary primitives against the specification's truth table, the canonical
hello-world, and the two divergences.

## Licence

MIT. See [`LICENSE`](LICENSE).
