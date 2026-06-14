"""Console report formatting for SpeechLens analysis results."""

from .analyzer import timing_verdict

WIDTH = 62


def _heading(title):
    return "\n" + title.upper() + "\n" + "-" * WIDTH


def _bar(count, max_count, max_width=30):
    """A simple text bar so the report is readable in any terminal."""
    if max_count <= 0:
        return ""
    length = max(1, int(round(count / max_count * max_width)))
    return "#" * length


def build_report(results, title, target_min=None, target_max=None):
    """Build the full console report as a single string."""
    lines = []
    lines.append("=" * WIDTH)
    lines.append("SPEECHLENS REPORT".center(WIDTH))
    lines.append(title.center(WIDTH))
    lines.append("=" * WIDTH)

    lines.append(_heading("Delivery time"))
    lines.append(
        "Estimated duration : {}  (at {} words/min)".format(
            results["estimated_duration"], results["wpm"]
        )
    )
    if target_min is not None and target_max is not None:
        verdict = timing_verdict(
            results["estimated_minutes"], target_min, target_max
        )
        lines.append("Timing check       : " + verdict)

    lines.append(_heading("Length and structure"))
    lines.append("Words              : {}".format(results["total_words"]))
    lines.append("Sentences          : {}".format(results["total_sentences"]))
    lines.append(
        "Avg sentence       : {} words".format(results["avg_sentence_length"])
    )
    lines.append(
        "Longest sentence   : {} words".format(
            results["longest_sentence_words"]
        )
    )

    lines.append(_heading("Clarity"))
    lines.append(
        "Reading ease       : {}  ({})".format(
            results["flesch_reading_ease"], results["readability"]
        )
    )
    lines.append(
        "Vocabulary richness: {:.0%} unique words".format(
            results["vocabulary_richness"]
        )
    )

    lines.append(_heading("Filler words"))
    filler_counts = results["filler_counts"]
    if filler_counts:
        lines.append(
            "Total fillers      : {}  ({} per 100 words)".format(
                results["total_fillers"], results["fillers_per_100_words"]
            )
        )
        max_count = max(filler_counts.values())
        for filler, count in sorted(
            filler_counts.items(), key=lambda item: item[1], reverse=True
        ):
            lines.append(
                "  {:<18} {:>3}  {}".format(
                    filler, count, _bar(count, max_count)
                )
            )
    else:
        lines.append("No filler words detected. Excellent!")

    lines.append(_heading("Most repeated words"))
    top_words = results["top_words"]
    if top_words:
        max_count = top_words[0][1]
        for word, count in top_words:
            lines.append(
                "  {:<18} {:>3}  {}".format(word, count, _bar(count, max_count))
            )
    else:
        lines.append("Not enough content words to analyze.")

    lines.append("")
    lines.append("=" * WIDTH)
    lines.append("Tip: read the speech aloud once with a timer - SpeechLens")
    lines.append("estimates pace, but your real delivery is what counts.")
    lines.append("=" * WIDTH)

    return "\n".join(lines)
