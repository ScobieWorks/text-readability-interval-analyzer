import argparse
import json
import re
import textwrap
from pathlib import Path

# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, strategy: str, chunk_size: int | None = None) -> list[str]:
    """Split *text* into chunks according to *strategy*.

    *strategy* can be ``paragraph``, ``line`` or ``char``.  For ``char`` a
    positive integer *chunk_size* must be supplied.
    """
    if strategy == "paragraph":
        # Split on one or more blank lines, preserving surrounding whitespace
        return [c for c in re.split(r"\n\s*\n", text.strip()) if c]
    if strategy == "line":
        return [c for c in text.splitlines() if c]
    if strategy == "char":
        if chunk_size is None or chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer for 'char' strategy")
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    raise ValueError(f"Unknown chunk strategy: {strategy}")

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _count_syllables(word: str) -> int:
    """Heuristic syllable counter: count contiguous vowel groups.
    """
    return len(re.findall(r"[aeiouyAEIOUY]+", word))


def compute_metrics(chunk: str) -> dict:
    """Return a dict with word, sentence, syllable, complex word counts and
    Flesch‑Kincaid and SMOG scores.
    """
    words = re.findall(r"\b\w+\b", chunk)
    word_count = len(words)
    sentence_count = len(re.findall(r"[.!?]+", chunk)) or 1
    syllable_count = sum(_count_syllables(w) for w in words)
    complex_words = sum(1 for w in words if _count_syllables(w) >= 3)
    fk_grade = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59
    smog = 1.0430 * (30 * (complex_words / sentence_count)) ** 0.5 + 3.1291
    return {
        "words": word_count,
        "sentences": sentence_count,
        "syllables": syllable_count,
        "complex_words": complex_words,
        "fk_grade": fk_grade,
        "smog": smog,
    }

# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def render_report(metrics_list: list[dict]) -> None:
    """Print a table with chunk number, FK, SMOG and an ASCII bar.
    The bar length is scaled to the range 0–50 based on FK scores.
    """
    if not metrics_list:
        print("No chunks to report.")
        return
    fk_values = [m["fk_grade"] for m in metrics_list]
    min_fk, max_fk = min(fk_values), max(fk_values)
    bar_max = 50
    header = f"{'#':>3} {'FK Grade':>9} {'SMOG':>6} {'Heat':>50}"
    print(header)
    print("-" * len(header))
    for idx, m in enumerate(metrics_list, start=1):
        fk = m["fk_grade"]
        smog = m["smog"]
        if max_fk > min_fk:
            bar_len = int(round((fk - min_fk) / (max_fk - min_fk) * bar_max))
        else:
            bar_len = bar_max // 2
        bar = "*" * bar_len
        print(f"{idx:>3} {fk:9.2f} {smog:6.2f} {bar:>50}")

# ---------------------------------------------------------------------------
# JSON output helper
# ---------------------------------------------------------------------------

def write_json_report(result_path: Path, report: list[dict]) -> None:
    with open(result_path, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)

# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Interval readability analyzer")
    parser.add_argument("--file", required=True, type=Path, help="Path to input text file")
    parser.add_argument(
        "--chunk",
        choices=["paragraph", "line", "char"],
        default="paragraph",
        help="Chunking strategy",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        help="Number of characters per chunk when --chunk=char",
    )
    parser.add_argument("--json-output", type=Path, help="Optional JSON report file")
    args = parser.parse_args(argv)

    if args.chunk == "char" and args.chunk_size is None:
        parser.error("--chunk-size is required when --chunk=char")

    # Gracefully handle missing input file
    try:
        text = args.file.read_text(encoding="utf-8")
    except FileNotFoundError:
        parser.error(f"No such file or directory: {args.file}")

    chunks = chunk_text(text, args.chunk, args.chunk_size)
    metrics = [compute_metrics(c) for c in chunks]
    render_report(metrics)
    if args.json_output:
        write_json_report(args.json_output, metrics)


if __name__ == "__main__":
    main()
