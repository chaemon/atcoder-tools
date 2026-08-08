import re
import unittest
from dataclasses import dataclass

from atcodertools.client.models.problem_content import (
    ProblemContent,
)
from atcodertools.fmtprediction.query_identifier_alias import (
    encode_spliced_query_identifiers,
    restore_identifier_aliases,
)


@dataclass(frozen=True)
class _Node:
    name: str
    children: tuple


class QueryIdentifierAliasTest(unittest.TestCase):
    def _content(self, text):
        return ProblemContent(
            input_format_text=text,
            samples=[],
        )

    def test_digit_bases_get_deterministic_alpha_aliases(self):
        content = self._content(
            "Q\n"
            "h1_1 h2_1 w1_1 w2_1\n"
            "h1_2 h2_2 w1_2 w2_2\n"
            "\\vdots\n"
            "h1_Q h2_Q w1_Q w2_Q"
        )

        encoded, aliases = (
            encode_spliced_query_identifiers(
                content
            )
        )

        self.assertEqual(
            list(aliases.values()),
            ["h1", "h2", "w1", "w2"],
        )
        self.assertEqual(
            list(aliases),
            ["zzqa", "zzqb", "zzqc", "zzqd"],
        )

        encoded_text = encoded.get_input_format()

        for alias in aliases:
            self.assertRegex(
                encoded_text,
                re.compile(
                    r"\b"
                    + re.escape(alias)
                    + r"_[12Q]\b"
                ),
            )

        self.assertNotIn("h1_1", encoded_text)
        self.assertNotIn("w2_Q", encoded_text)

    def test_alpha_only_bases_preserve_content_identity(self):
        content = self._content(
            "Q\n"
            "x_1 y_1\n"
            "\\vdots\n"
            "x_Q y_Q"
        )

        encoded, aliases = (
            encode_spliced_query_identifiers(
                content
            )
        )

        self.assertIs(encoded, content)
        self.assertEqual(aliases, {})

    def test_alias_allocation_avoids_existing_alpha_run(self):
        content = self._content(
            "zzqa_1\n"
            "Q\n"
            "A0_1 A1_1 A2_1\n"
            "\\vdots\n"
            "A0_Q A1_Q A2_Q"
        )

        encoded, aliases = (
            encode_spliced_query_identifiers(
                content
            )
        )

        self.assertNotIn("zzqa", aliases)
        self.assertEqual(
            list(aliases.values()),
            ["A0", "A1", "A2"],
        )
        self.assertIn(
            "zzqa_1",
            encoded.get_input_format(),
        )

    def test_restore_identifier_aliases_recurses(self):
        value = _Node(
            "zzqa",
            (
                _Node(
                    "zzqb",
                    (),
                ),
                "prefix zzqa suffix",
            ),
        )

        restored = restore_identifier_aliases(
            value,
            {
                "zzqa": "h1",
                "zzqb": "A0",
            },
        )

        self.assertEqual(restored.name, "h1")
        self.assertEqual(
            restored.children[0].name,
            "A0",
        )
        self.assertEqual(
            restored.children[1],
            "prefix h1 suffix",
        )


if __name__ == "__main__":
    unittest.main()
