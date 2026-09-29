import unittest

from typer.testing import CliRunner

from cli.main import app


class CliContractTests(unittest.TestCase):
    def test_analyze_is_an_explicit_command(self):
        result = CliRunner().invoke(app, ["--help"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("analyze", result.output)

    def test_documented_command_accepts_repo_argument(self):
        result = CliRunner().invoke(app, ["analyze", "missing-repository"])
        self.assertNotIn("Got unexpected extra argument", result.output)


if __name__ == "__main__":
    unittest.main()
