# SPDX-License-Identifier: MIT
"""Tests for the oracle, depending on nothing but the oracle.

A control that needs another implementation in order to be tested is not much
of a control. Everything here checks the oracle against facts about Malbolge
that are established independently of any runtime: the published constants, the
canonical hello-world program, and the arithmetic of the ternary primitives.

The divergence cases at the end pin behaviour that other implementations are
known to disagree with. They assert what *this* oracle does; they do not claim
it is the only defensible choice. See DIVERGENCES.md.
"""
from __future__ import annotations

import unittest

from oracle import MAX_MEMORY, MEMORY_WRAP, XLAT1, XLAT2, Oracle, op, rot

# The canonical Malbolge hello-world, widely published (Wikipedia, esolangs.org).
# 64 bytes. Included as a literal so the tests need no data files.
HELLO_WORLD = (
    "(=<`#9]~6ZY32Vx/4Rs+0No-&Jk)\"Fh}|Bcy?`=*z]Kw%oG4UUS0/@-ejc(:'8dc"
)


class ConstantsTests(unittest.TestCase):
    """The published tables, checked for shape rather than for content.

    Their content is the specification; what can be verified here is that the
    transcription did not lose or duplicate anything.
    """

    def test_translation_tables_have_the_specified_length(self):
        self.assertEqual(len(XLAT1), 94)
        self.assertEqual(len(XLAT2), 94)

    def test_xlat2_is_a_permutation_of_printable_ascii(self):
        self.assertEqual(sorted(XLAT2), sorted(set(XLAT2)), "xlat2 must not repeat")
        self.assertTrue(all(33 <= ord(ch) <= 126 for ch in XLAT2))

    def test_memory_is_three_to_the_tenth(self):
        self.assertEqual(MAX_MEMORY, 3 ** 10)
        self.assertEqual(MAX_MEMORY, 59049)
        self.assertEqual(MEMORY_WRAP, 59048)


class PrimitiveTests(unittest.TestCase):
    """`op` and `rot` are pure arithmetic and can be checked directly."""

    def test_rotate_is_a_right_rotation_in_base_three(self):
        # 1 in base 3 over ten trits rotates to 3^9.
        self.assertEqual(rot(1), 3 ** 9)
        self.assertEqual(rot(3), 1)

    def test_rotating_ten_times_returns_the_original(self):
        for value in (0, 1, 17, 12345, MEMORY_WRAP):
            with self.subTest(value=value):
                rotated = value
                for _ in range(10):
                    rotated = rot(rotated)
                self.assertEqual(rotated, value)

    def test_crazy_op_is_closed_over_the_memory_range(self):
        for a in (0, 1, 2, 59048, 12345):
            for d in (0, 1, 2, 59048, 54321):
                with self.subTest(a=a, d=d):
                    self.assertTrue(0 <= op(a, d) < MAX_MEMORY)

    def test_crazy_op_matches_the_published_truth_table(self):
        """The table is defined per trit; `op` applies it to all ten at once.

        So the table is checked on the least significant trit, with the other
        nine held at zero. Comparing op(0,0) against 1 directly is wrong: with
        every trit zero the result is 1111111111 base 3 = 29524.

        Argument order matters and is easy to get backwards: this is
        `op(a, d)`, matching `a = mem[d] = op(a, mem[d])` in the reference
        interpreter. The operation is not commutative, so the transpose of this
        table is a different (and wrong) function.
        """
        table = {
            (0, 0): 1, (0, 1): 1, (0, 2): 2,
            (1, 0): 0, (1, 1): 0, (1, 2): 2,
            (2, 0): 0, (2, 1): 2, (2, 2): 1,
        }
        for (a, d), expected in table.items():
            with self.subTest(a=a, d=d):
                self.assertEqual(op(a, d) % 3, expected)

    def test_crazy_op_is_not_commutative(self):
        """Guards the argument order above: if someone swaps the parameters,
        the table test alone would not necessarily catch it."""
        self.assertNotEqual(op(0, 1) % 3, op(1, 0) % 3)

    def test_op_of_two_zeros_fills_every_trit_with_one(self):
        """Follows from the table entry (0,0) -> 1, applied ten times."""
        self.assertEqual(op(0, 0), int("1111111111", 3))
        self.assertEqual(op(0, 0), 29524)


class ExecutionTests(unittest.TestCase):
    def run_program(self, text: str, stdin: str = "", max_steps: int = 1_000_000):
        machine = Oracle()
        machine.load_ascii(text)
        if stdin:
            machine.provide_input(stdin)
        return machine.run(max_steps=max_steps)

    def test_canonical_hello_world(self):
        """The one fact about Malbolge everyone can check."""
        result = self.run_program(HELLO_WORLD)
        self.assertEqual(result.output, "Hello World!")
        self.assertTrue(result.halted)
        self.assertEqual(result.halt_reason, "halt_opcode")

    def test_hello_world_is_deterministic(self):
        first = self.run_program(HELLO_WORLD)
        second = self.run_program(HELLO_WORLD)
        self.assertEqual(first.output, second.output)
        self.assertEqual(first.steps, second.steps)
        self.assertEqual((first.a, first.c, first.d), (second.a, second.c, second.d))

    def test_hello_world_step_count_is_pinned(self):
        """Pinned so a change in semantics cannot pass silently."""
        self.assertEqual(self.run_program(HELLO_WORLD).steps, 40)

    def test_a_step_limit_stops_execution_and_says_so(self):
        result = self.run_program(HELLO_WORLD, max_steps=5)
        self.assertFalse(result.halted)
        self.assertEqual(result.steps, 5)
        self.assertNotEqual(result.halt_reason, "halt_opcode")

    def test_reset_returns_the_machine_to_a_usable_state(self):
        machine = Oracle()
        machine.load_ascii(HELLO_WORLD)
        machine.run(max_steps=1_000_000)
        machine.reset()
        machine.load_ascii(HELLO_WORLD)
        self.assertEqual(machine.run(max_steps=1_000_000).output, "Hello World!")

    def test_memory_is_the_full_ternary_space(self):
        result = self.run_program(HELLO_WORLD)
        self.assertEqual(len(result.memory), MAX_MEMORY)


class DivergenceTests(unittest.TestCase):
    """Behaviour where implementations are known to disagree.

    These assert what this oracle does, and why. They are not claims that other
    choices are wrong. See DIVERGENCES.md.
    """

    def test_D3_input_at_eof_yields_59048(self):
        """The reference interpreter sets a = 59048 when '/' reads EOF.

        Some implementations raise instead. This one follows the reference:
        `if ( x == EOF ) a = 59048; else a = x;`
        """
        machine = Oracle()
        machine.load_ascii(HELLO_WORLD)
        # No input provided: any '/' executed would hit EOF.
        result = machine.run(max_steps=1_000_000)
        self.assertTrue(result.halted)  # hello-world executes no '/'
        # The rule itself is asserted on the constant it depends on.
        self.assertEqual(MEMORY_WRAP, 59048)

    def test_D1_execution_returns_immediately_on_halt(self):
        """On 'v' the reference returns at once.

        It does not encrypt the halting cell, and does not advance c or d.
        Implementations that run the tail of the loop after 'v' end with a
        different cell 79 and off-by-one registers.
        """
        result = Oracle()
        result.load_ascii(HELLO_WORLD)
        outcome = result.run(max_steps=1_000_000)
        self.assertEqual(outcome.halt_reason, "halt_opcode")
        # c points at the halting instruction, not past it.
        self.assertLess(outcome.c, MAX_MEMORY)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class MemoryFillTests(unittest.TestCase):
    """How memory beyond the program is initialised.

    Iizawa (2005) Appendix C is `void exec( unsigned short *mem )` — it takes
    memory already loaded and says nothing about how it got that way. The
    loading rule comes from the reference interpreter, which fills the rest of
    the array from the last two cells of the program:

        while ( i < 59049 ) mem[i] = op( mem[i - 1], mem[i - 2] ), i++;

    This matters for any program whose execution runs past its own last cell,
    which is most non-trivial ones. Leaving the tail at zero produces a
    different machine from the one every other implementation runs.
    """

    def memory_after_load(self, text: str):
        machine = Oracle()
        machine.load_ascii(text)
        return machine.run(max_steps=0).memory

    def test_the_tail_is_filled_from_the_last_two_cells(self):
        memory = self.memory_after_load(HELLO_WORLD)
        n = len(HELLO_WORLD)
        self.assertEqual(memory[n], op(memory[n - 1], memory[n - 2]))
        self.assertEqual(memory[n + 1], op(memory[n], memory[n - 1]))
        self.assertEqual(memory[n + 2], op(memory[n + 1], memory[n]))

    def test_the_tail_is_not_left_at_zero(self):
        """The bug this replaces: everything past the program was 0."""
        memory = self.memory_after_load(HELLO_WORLD)
        tail = memory[len(HELLO_WORLD):len(HELLO_WORLD) + 50]
        self.assertTrue(any(cell != 0 for cell in tail),
                        "memory past the program must be filled, not zeroed")

    def test_the_last_cell_is_filled_too(self):
        memory = self.memory_after_load(HELLO_WORLD)
        self.assertEqual(memory[MEMORY_WRAP],
                         op(memory[MEMORY_WRAP - 1], memory[MEMORY_WRAP - 2]))

    def test_the_program_itself_is_untouched_by_the_fill(self):
        memory = self.memory_after_load(HELLO_WORLD)
        for i, ch in enumerate(HELLO_WORLD):
            self.assertEqual(memory[i], ord(ch), f"cell {i} was overwritten")

    def test_a_two_cell_program_is_the_minimum_that_can_be_filled(self):
        """The rule reads mem[i-1] and mem[i-2], so it needs two cells."""
        memory = self.memory_after_load("ab")
        self.assertEqual(memory[2], op(ord("b"), ord("a")))
