import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

# Import the module under test
import text_readability_interval_analyzer

class TestChunking(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.input_file = self.root / "input.txt"

    def tearDown(self):
        self.tmp.cleanup()

    def write_input(self, content: str):
        self.input_file.write_text(content, encoding="utf-8")

    def capture_output(self, argv):
        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            try:
                text_readability_interval_analyzer.main(argv)
            except SystemExit as e:
                # Capture exit codes for error tests
                return f.getvalue(), e.code
        return f.getvalue(), None

    def test_paragraph_chunking(self):
        content = "Para one.\n\nPara two."
        self.write_input(content)
        out, code = self.capture_output(["--file", str(self.input_file), "--chunk", "paragraph"])
        self.assertIsNone(code)
        self.assertIn("#", out)
        self.assertIn("1", out)
        self.assertIn("2", out)

    def test_line_chunking(self):
        content = "Line one.\nLine two.\nLine three."
        self.write_input(content)
        out, code = self.capture_output(["--file", str(self.input_file), "--chunk", "line"])
        self.assertIsNone(code)
        self.assertIn("1", out)
        self.assertIn("2", out)
        self.assertIn("3", out)

    def test_char_chunking(self):
        content = "A" * 100
        self.write_input(content)
        out, code = self.capture_output(["--file", str(self.input_file), "--chunk", "char", "--chunk-size", "30"])
        self.assertIsNone(code)
        # Expect 4 chunks (30,30,30,10)
        self.assertIn("1", out)
        self.assertIn("4", out)

    def test_missing_chunk_size(self):
        content = "Hello world."
        self.write_input(content)
        out, code = self.capture_output(["--file", str(self.input_file), "--chunk", "char"])
        self.assertIsNotNone(code)
        self.assertIn("error", out.lower())

    def test_invalid_chunk(self):
        content = "Hello world."
        self.write_input(content)
        out, code = self.capture_output(["--file", str(self.input_file), "--chunk", "invalid"])
        self.assertIsNotNone(code)
        self.assertIn("error", out.lower())

class TestMetrics(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.input_file = self.root / "input.txt"

    def tearDown(self):
        self.tmp.cleanup()

    def write_input(self, content: str):
        self.input_file.write_text(content, encoding="utf-8")

    def capture_output(self, argv):
        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            try:
                text_readability_interval_analyzer.main(argv)
            except SystemExit as e:
                return f.getvalue(), e.code
        return f.getvalue(), None

    def test_metrics_values(self):
        content = "Hello world. This is a test."
        self.write_input(content)
        out, code = self.capture_output(["--file", str(self.input_file), "--chunk", "paragraph"])
        self.assertIsNone(code)
        # Expect one chunk
        self.assertIn("1", out)
        # FK grade around -0.64, SMOG around 3.13
        self.assertRegex(out, r"-0\.6[0-9] ")
        self.assertRegex(out, r"3\.13")

    def test_json_output(self):
        content = "Hello world. This is a test."
        self.write_input(content)
        json_path = self.root / "report.json"
        out, code = self.capture_output(["--file", str(self.input_file), "--chunk", "paragraph", "--json-output", str(json_path)])
        self.assertIsNone(code)
        self.assertTrue(json_path.exists())
        data = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        chunk = data[0]
        self.assertEqual(chunk["words"], 6)
        self.assertEqual(chunk["sentences"], 2)
        self.assertEqual(chunk["complex_words"], 0)
        self.assertAlmostEqual(chunk["fk_grade"], -0.64, places=1)
        self.assertAlmostEqual(chunk["smog"], 3.13, places=2)

class TestCLIErrorHandling(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.input_file = self.root / "input.txt"

    def tearDown(self):
        self.tmp.cleanup()

    def write_input(self, content: str):
        self.input_file.write_text(content, encoding="utf-8")

    def capture_output(self, argv):
        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            try:
                text_readability_interval_analyzer.main(argv)
            except SystemExit as e:
                return f.getvalue(), e.code
        return f.getvalue(), None

    def test_missing_file(self):
        out, code = self.capture_output(["--file", str(self.root / "doesnotexist.txt")])
        self.assertIsNotNone(code)
        self.assertIn("No such file", out)

    def test_no_arguments(self):
        out, code = self.capture_output([])
        self.assertIsNotNone(code)
        self.assertIn("error", out.lower())

if __name__ == "__main__":
    unittest.main()
