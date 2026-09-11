import unittest
from pathlib import Path


class TestProjectFoundation(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent

    def test_directory_structure(self):
        expected_dirs = [
            self.base_dir / "data" / "raw",
            self.base_dir / "data" / "sample",
            self.base_dir / "data" / "golden",
            self.base_dir / "src" / "analysis",
            self.base_dir / "src" / "data",
            self.base_dir / "src" / "classification",
            self.base_dir / "src" / "retrieval",
            self.base_dir / "src" / "generation",
            self.base_dir / "src" / "escalation",
            self.base_dir / "src" / "evaluation",
            self.base_dir / "reports" / "results",
            self.base_dir / "tests",
        ]
        for d in expected_dirs:
            self.assertTrue(d.exists(), f"Expected directory does not exist: {d}")
            self.assertTrue(d.is_dir(), f"Path is not a directory: {d}")

    def test_required_files(self):
        expected_files = [
            self.base_dir / ".gitignore",
            self.base_dir / ".env.example",
            self.base_dir / "requirements.txt",
            self.base_dir / "README.md",
            self.base_dir / "data" / "raw" / "README.md",
        ]
        for f in expected_files:
            self.assertTrue(f.exists(), f"Expected file does not exist: {f}")
            self.assertTrue(f.is_file(), f"Path is not a file: {f}")

    def test_gitignore_rules(self):
        gitignore_path = self.base_dir / ".gitignore"
        content = gitignore_path.read_text(encoding="utf-8")
        self.assertIn("data/raw/twcs.csv", content)
        self.assertIn(".env", content)
        self.assertIn("*.faiss", content)
        self.assertIn("*.log", content)

    def test_src_imports(self):
        import sys
        if str(self.base_dir) not in sys.path:
            sys.path.insert(0, str(self.base_dir))

        import src
        import src.analysis
        import src.classification
        import src.data
        import src.escalation
        import src.evaluation
        import src.generation
        import src.retrieval

        self.assertEqual(src.__version__, "0.1.0")


if __name__ == "__main__":
    unittest.main()
