"""Unit tests for speechlens.analyzer.

Run from the project root with:
    python -m unittest discover tests -v
"""

import unittest

from speechlens.analyzer import (
    analyze,
    clean_words,
    count_fillers,
    count_syllables,
    estimate_duration,
    flesch_reading_ease,
    format_duration,
    split_sentences,
    timing_verdict,
)


class TestCleanWords(unittest.TestCase):
    def test_basic_split(self):
        self.assertEqual(clean_words("Hello, world!"), ["hello", "world"])

    def test_keeps_apostrophes(self):
        self.assertEqual(clean_words("Don't stop"), ["don't", "stop"])

    def test_empty_text(self):
        self.assertEqual(clean_words(""), [])


class TestSplitSentences(unittest.TestCase):
    def test_three_sentences(self):
        text = "I came. I saw! Did I conquer?"
        self.assertEqual(len(split_sentences(text)), 3)

    def test_ignores_trailing_punctuation(self):
        self.assertEqual(len(split_sentences("One sentence.")), 1)


class TestCountSyllables(unittest.TestCase):
    def test_single_syllable(self):
        self.assertEqual(count_syllables("cat"), 1)

    def test_two_syllables(self):
        self.assertEqual(count_syllables("table"), 2)

    def test_silent_e(self):
        self.assertEqual(count_syllables("stage"), 1)

    def test_three_syllables(self):
        self.assertEqual(count_syllables("beautiful"), 3)

    def test_minimum_is_one(self):
        self.assertEqual(count_syllables("rhythm"), 1)


class TestFillers(unittest.TestCase):
    def test_counts_single_word_fillers(self):
        counts = count_fillers("Um, this is, um, basically a test.")
        self.assertEqual(counts["um"], 2)
        self.assertEqual(counts["basically"], 1)

    def test_counts_phrases(self):
        counts = count_fillers("You know, it works. You know it does.")
        self.assertEqual(counts["you know"], 2)

    def test_clean_text_has_no_fillers(self):
        counts = count_fillers("The quick brown fox jumps over a lazy dog.")
        self.assertEqual(sum(counts.values()), 0)


class TestTiming(unittest.TestCase):
    def test_duration_at_130_wpm(self):
        self.assertAlmostEqual(estimate_duration(650, 130), 5.0)

    def test_format_duration(self):
        self.assertEqual(format_duration(5.4), "5m 24s")

    def test_verdict_on_target(self):
        self.assertIn("ON TARGET", timing_verdict(6.0, 5, 7))

    def test_verdict_under(self):
        self.assertIn("UNDER TIME", timing_verdict(3.0, 5, 7))

    def test_verdict_over(self):
        self.assertIn("OVER TIME", timing_verdict(8.0, 5, 7))


class TestFlesch(unittest.TestCase):
    def test_simple_text_scores_high(self):
        text = "I like dogs. Dogs are fun. We run and play."
        words = clean_words(text)
        syllables = sum(count_syllables(w) for w in words)
        score = flesch_reading_ease(len(words), 3, syllables)
        self.assertGreater(score, 80)

    def test_zero_words_is_safe(self):
        self.assertEqual(flesch_reading_ease(0, 0, 0), 0.0)


class TestAnalyze(unittest.TestCase):
    SPEECH = (
        "Good evening everyone. Um, today I want to talk about courage. "
        "Courage is not the absence of fear. Courage is action in spite "
        "of fear. You know, every speaker in this room has felt fear."
    )

    def setUp(self):
        self.results = analyze(self.SPEECH, wpm=130)

    def test_word_count_positive(self):
        self.assertGreater(self.results["total_words"], 30)

    def test_sentence_count(self):
        self.assertEqual(self.results["total_sentences"], 5)

    def test_fillers_detected(self):
        self.assertIn("um", self.results["filler_counts"])
        self.assertIn("you know", self.results["filler_counts"])

    def test_top_words_excludes_stopwords(self):
        top = dict(self.results["top_words"])
        self.assertIn("courage", top)
        self.assertNotIn("the", top)

    def test_duration_format(self):
        self.assertRegex(self.results["estimated_duration"], r"^\d+m \d{2}s$")

    def test_vocabulary_richness_between_0_and_1(self):
        self.assertGreater(self.results["vocabulary_richness"], 0)
        self.assertLessEqual(self.results["vocabulary_richness"], 1)


if __name__ == "__main__":
    unittest.main()
