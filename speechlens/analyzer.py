"""Core text analysis for SpeechLens.

All functions work on plain text (a speech script or transcript) and use
only the Python standard library, so the tool runs anywhere Python runs.
"""

import re
from collections import Counter

# Average speaking pace for a prepared speech, in words per minute.
# Conversational pace is roughly 120-150 wpm; 130 is a safe default.
DEFAULT_WPM = 130

# Single-word fillers commonly heard in spoken English. Note that words
# like "actually" and "basically" are legitimate words; they are flagged
# because speakers tend to overuse them as verbal padding.
FILLER_WORDS = {
    "um", "uh", "er", "ah", "erm", "hmm",
    "like", "actually", "basically", "literally",
    "honestly", "anyway", "okay", "right",
}

# Multi-word filler phrases, matched as whole phrases.
FILLER_PHRASES = [
    "you know",
    "i mean",
    "sort of",
    "kind of",
    "at the end of the day",
    "to be honest",
]

# Common English words excluded from the "most repeated words" list so
# that the list highlights meaningful vocabulary instead of "the"/"and".
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "so", "of", "to", "in", "on",
    "at", "for", "with", "from", "by", "as", "is", "are", "was", "were",
    "be", "been", "being", "am", "it", "its", "this", "that", "these",
    "those", "i", "me", "my", "we", "our", "us", "you", "your", "he",
    "she", "his", "her", "they", "them", "their", "who", "whom", "which",
    "what", "when", "where", "why", "how", "not", "no", "yes", "do",
    "does", "did", "have", "has", "had", "will", "would", "can", "could",
    "shall", "should", "may", "might", "must", "there", "here", "then",
    "than", "too", "very", "just", "also", "into", "about", "all", "if",
    "because", "while", "out", "up", "down", "over", "under", "again",
}


def clean_words(text):
    """Return a list of lowercase words, keeping internal apostrophes."""
    return re.findall(r"[a-z']+", text.lower())


def split_sentences(text):
    """Split text into sentences on ., ! and ? (ignores empty pieces)."""
    pieces = re.split(r"[.!?]+", text)
    return [piece.strip() for piece in pieces if piece.strip()]


def count_syllables(word):
    """Estimate syllables in a word by counting vowel groups.

    This is the classic heuristic used by readability formulas: count
    groups of consecutive vowels, then subtract one for a silent
    trailing 'e' (as in "stage"), and never return less than 1.
    """
    word = word.lower().strip("'")
    if not word:
        return 0
    vowels = "aeiouy"
    count = 0
    previous_was_vowel = False
    for letter in word:
        is_vowel = letter in vowels
        if is_vowel and not previous_was_vowel:
            count += 1
        previous_was_vowel = is_vowel
    if word.endswith("e") and not word.endswith(("le", "ee")) and count > 1:
        count -= 1
    return max(count, 1)


def flesch_reading_ease(total_words, total_sentences, total_syllables):
    """Flesch Reading Ease score (higher = easier to follow by ear).

    90-100 very easy, 60-70 plain English, below 30 very difficult.
    Spoken speeches should usually score 60 or higher.
    """
    if total_words == 0 or total_sentences == 0:
        return 0.0
    words_per_sentence = total_words / total_sentences
    syllables_per_word = total_syllables / total_words
    score = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
    return round(score, 1)


def readability_label(score):
    """Translate a Flesch score into a speaker-friendly label."""
    if score >= 80:
        return "Very easy to follow"
    if score >= 60:
        return "Conversational - good for a speech"
    if score >= 40:
        return "Fairly complex - simplify long sentences"
    return "Difficult - audiences will struggle to follow by ear"


def count_fillers(text):
    """Count filler words and phrases. Returns a Counter keyed by filler."""
    counts = Counter()
    lowered = text.lower()

    for phrase in FILLER_PHRASES:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        found = len(re.findall(pattern, lowered))
        if found:
            counts[phrase] = found

    for word in clean_words(text):
        if word in FILLER_WORDS:
            counts[word] += 1

    return counts


def estimate_duration(total_words, wpm=DEFAULT_WPM):
    """Estimated speaking time in minutes (float) at the given pace."""
    if wpm <= 0:
        return 0.0
    return total_words / wpm


def format_duration(minutes):
    """Format a duration in minutes as 'Xm YYs' (e.g. '5m 24s')."""
    total_seconds = int(round(minutes * 60))
    return "{}m {:02d}s".format(total_seconds // 60, total_seconds % 60)


def timing_verdict(minutes, target_min, target_max):
    """Compare estimated duration against a target window (in minutes)."""
    if minutes < target_min:
        gap = format_duration(target_min - minutes)
        return "UNDER TIME - add about " + gap + " of content"
    if minutes > target_max:
        gap = format_duration(minutes - target_max)
        return "OVER TIME - cut about " + gap + " of content"
    return "ON TARGET - within the {}-{} minute window".format(
        target_min, target_max
    )


def analyze(text, wpm=DEFAULT_WPM):
    """Run the full analysis and return all metrics in a dictionary."""
    words = clean_words(text)
    sentences = split_sentences(text)

    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(count_syllables(word) for word in words)

    filler_counts = count_fillers(text)
    total_fillers = sum(filler_counts.values())

    unique_words = len(set(words))
    vocabulary_richness = (unique_words / total_words) if total_words else 0.0

    content_words = [
        word for word in words
        if word not in STOPWORDS and word not in FILLER_WORDS and len(word) > 2
    ]
    top_words = Counter(content_words).most_common(8)

    sentence_lengths = [len(clean_words(sentence)) for sentence in sentences]
    avg_sentence_length = (
        sum(sentence_lengths) / total_sentences if total_sentences else 0.0
    )
    longest_sentence = max(sentence_lengths) if sentence_lengths else 0

    flesch = flesch_reading_ease(total_words, total_sentences, total_syllables)
    duration = estimate_duration(total_words, wpm)

    return {
        "total_words": total_words,
        "total_sentences": total_sentences,
        "total_syllables": total_syllables,
        "unique_words": unique_words,
        "vocabulary_richness": round(vocabulary_richness, 3),
        "avg_sentence_length": round(avg_sentence_length, 1),
        "longest_sentence_words": longest_sentence,
        "filler_counts": dict(filler_counts),
        "total_fillers": total_fillers,
        "fillers_per_100_words": round(
            (total_fillers / total_words * 100) if total_words else 0.0, 1
        ),
        "top_words": top_words,
        "flesch_reading_ease": flesch,
        "readability": readability_label(flesch),
        "wpm": wpm,
        "estimated_minutes": round(duration, 2),
        "estimated_duration": format_duration(duration),
    }
