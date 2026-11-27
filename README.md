# Text Readability Interval Analyzer

## Overview

The **Text Readability Interval Analyzer** is a lightweight, offline command‑line tool that splits a plain‑text document into user‑defined chunks and computes readability metrics for each chunk.  It is designed for educators, writers, and accessibility specialists who need to spot problematic passages without running a full text‑analysis suite.

Key features:

* **Chunking** – split by paragraph, line, or a fixed number of characters.
* **Readability metrics** – Flesch‑Kincaid Grade Level and SMOG for each chunk.
* **Heat‑map** – an ASCII bar chart that visualises the relative difficulty of each chunk.
* **Optional JSON report** – a machine‑readable array of raw metrics.

The tool is written in pure Python 3.11+ and relies only on the standard library.

---

## Installation

The project is a single Python module, so you can copy the file `text_readability_interval_analyzer.py` into your project or run it directly with the interpreter:

```bash
python -m text_readability_interval_analyzer --help
```

No external dependencies are required.

---

## Usage

```bash
python -m text_readability_interval_analyzer \
  --file book.txt \
  --chunk paragraph \
  --json-output report.json
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file` | Path to the input plain‑text file. | **Required** |
| `--chunk` | Chunking strategy: `paragraph`, `line`, or `char`. | `paragraph` |
| `--chunk-size` | Number of characters per chunk when `--chunk=char`. | *Required if `char`* |
| `--json-output` | Path to write a JSON report. | *Optional* |

### Output

The tool prints a table to stdout:

```
 #   FK Grade   SMOG Heat
--------------------------------------------
 1   10.23   12.45 *****************************************
 2    8.12   10.30 *********************************
 3   12.50   14.00 *******************************************
```

The *Heat* column is an ASCII bar whose length is proportional to the Flesch‑Kincaid score relative to the minimum and maximum scores in the document.

If `--json-output` is supplied, a JSON file containing an array of objects is written.  Each object has the following keys:

```json
{
  "words": 123,
  "sentences": 10,
  "syllables": 200,
  "complex_words": 5,
  "fk_grade": 8.12,
  "smog": 10.30
}
```

---

## Example

```text
Paragraph one. It has a few sentences.

Paragraph two is a bit longer and contains more complex words such as extraordinary.
```

Running the analyzer:

```bash
python -m text_readability_interval_analyzer --file example.txt --chunk paragraph
```

Output:

```
 #   FK Grade   SMOG Heat
--------------------------------------------
 1    6.45    7.80 *********
 2    9.12    10.45 *****************
```

---

## Development

The project is intentionally minimal.  The source file contains only the CLI implementation and the core logic.  Tests are located in `tests/test_cli.py` and use the standard `unittest` framework.

### Running tests

```bash
python -m unittest discover -s tests -v
```

All tests run in a temporary directory and do not modify the host filesystem.

---

## License

This project is released under the MIT License.


## Installation

```bash
pip install git+https://github.com/ScobieWorks/text-readability-interval-analyzer.git
```


## Command-line usage

```bash
text-readability-interval-analyzer --help
```

## Limitations
<!-- generated-limitations:cda8b356e8dd1f9076a128adbef6a862d0f909906767c90a782336f24e866b25 -->
- The `--chunk` option accepts only `paragraph`, `line`, `char`.
- The text reader in `text_readability_interval_analyzer.py` uses UTF-8; supply UTF-8 text for that reading path.
<!-- /generated-limitations -->
