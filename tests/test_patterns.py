import unittest
from typing import Iterable

from interegular import parse_pattern
from interegular.patterns import InvalidSyntax, Unsupported


class SyntaxTestCase(unittest.TestCase):
    def parse_unsupported(self, s: str):
        with self.assertRaises(Unsupported):
            parse_pattern(s).to_fsm()

    def parse_invalid_syntax(self, s: str):
        with self.assertRaises(InvalidSyntax):
            parse_pattern(s).to_fsm()

    def parse_valid(self, re: str, targets: Iterable[str] = (), non_targets: Iterable[str] = ()):
        fsm = parse_pattern(re).to_fsm()
        for s in targets:
            self.assertTrue(fsm.accepts(s), f"{re!r} does not match {s!r}")
        for s in non_targets:
            self.assertFalse(fsm.accepts(s), f"{re!r} does match {s!r}")

    def test_basic_syntax(self):
        self.parse_valid("a", ("a",), ("", "aa", "b"))
        self.parse_valid("a+", ("a", "aa", "aaaaa"), ("", "b", "ab"))
        self.parse_valid("a*", ("", "a", "aa", "aaaaa"), ("b", "ab"))
        self.parse_valid("a{2,10}", ("a" * 2, "a" * 5, "a" * 10), ("a" * 1, "a" * 11, "b", "ab"))
        self.parse_valid("a{,10}", ("a" * 1, "a" * 2, "a" * 5, "a" * 10), ("a" * 11, "b", "ab"))
        self.parse_valid("a{2,}", ("a" * 2, "a" * 5, "a" * 10, "a" * 11), ("a" * 1, "b", "ab"))
        self.parse_valid("[a-h]", (*"abcdef",), ("", "aa", *"ijk"))
        self.parse_valid("[^a-h]", (*"ijk?0\n",), ("", "aa", *"abcdef"))
        self.parse_valid("(ab)", ("ab",), ("", "a", "b", "abb"))
        self.parse_valid("(?:ab)", ("ab",), ("", "a", "b", "abb"))
        self.parse_valid("(?P<start>ab)", ("ab",), ("", "a", "b", "abb"))
        self.parse_unsupported("(?P=start)")
        self.parse_unsupported("\\1")
        self.parse_invalid_syntax("(")
        self.parse_invalid_syntax(")")
        self.parse_invalid_syntax("\\g")

    def test_looks(self):
        self.parse_valid("(?=ab)...", ("ab?",), ("cd?", ""))
        self.parse_valid("(?!ab)...", ("cd?",), ("ab?", ""))
        self.parse_unsupported("(?<=ab)")
        self.parse_unsupported("(?<!ab)")

    def test_flags(self):
        self.parse_valid("(?i)a", (*"aA",), ("", "b"))
        self.parse_valid("(?m).", (*"a0?",), ("", "\n"))
        self.parse_valid("(?s).", (*"a0?\n",), ("",))
        self.parse_unsupported("(?a)")
        self.parse_unsupported("(?L)")
        self.parse_unsupported("(?u)")
        self.parse_unsupported("(?x)")


if __name__ == '__main__':
    unittest.main()
