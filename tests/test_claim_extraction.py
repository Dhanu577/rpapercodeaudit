import unittest

from rpapercodeaudit.claim_extraction import MIN_WORDS, normalize_whitespace, validate_claims


class ClaimValidationTests(unittest.TestCase):
    PAPER = "Methods\nThe method filters\n genes below 10 counts.\nThe method uses a fixed size factor."

    def claim(self, sentence, claim_id="C001"):
        return {
            "id": claim_id,
            "verbatim_sentence": sentence,
            "section_or_figure": "Methods",
            "claim_type": "filtering",
            "what_to_look_for": "threshold or default",
        }

    def test_real_sentence_is_accepted_after_whitespace_normalization(self):
        result = validate_claims(self.PAPER, [self.claim("The method filters genes below 10 counts.")])
        self.assertEqual([claim.id for claim in result.accepted], ["C001"])
        self.assertEqual(result.rejected, [])

    def test_slightly_altered_sentence_is_rejected(self):
        result = validate_claims(self.PAPER, [self.claim("The method filters genes below 10 read counts.")])
        self.assertEqual(result.accepted, [])
        self.assertEqual(len(result.rejected), 1)
        self.assertIn("exact substring", result.rejected[0].reason)

    def test_invented_sentence_is_rejected(self):
        result = validate_claims(self.PAPER, [self.claim("The method uses a Bayesian prior.")])
        self.assertEqual(result.accepted, [])
        self.assertEqual(len(result.rejected), 1)
        self.assertIn("exact substring", result.rejected[0].reason)

    def test_whitespace_normalization_does_not_change_other_text(self):
        self.assertEqual(normalize_whitespace("A\n  B\tC"), "A B C")
        self.assertNotEqual(normalize_whitespace("Counts"), normalize_whitespace("counts"))
        self.assertNotEqual(normalize_whitespace("10 counts."), normalize_whitespace("10 counts"))

    def test_claim_minimum_word_count_is_five(self):
        self.assertEqual(MIN_WORDS, 5)
        result = validate_claims(self.PAPER, [
            self.claim(""),
            self.claim(" \t\n "),
            self.claim("The method filters genes"),
            self.claim("method filters genes below 10"),
        ])
        self.assertEqual([claim.verbatim_sentence for claim in result.accepted], ["method filters genes below 10"])
        self.assertEqual(len(result.rejected), 3)
        self.assertTrue(all("at least 5 words" in item.reason for item in result.rejected))


if __name__ == "__main__":
    unittest.main()
