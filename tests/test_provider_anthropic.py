import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rpapercodeaudit.llm import LLMClient, LLMConfig


class AnthropicProviderTests(unittest.TestCase):
    def test_anthropic_shape_is_supported_and_key_is_not_logged(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = LLMClient(
                LLMConfig("anthropic", "https://example.invalid", "secret-key", "model"),
                cache_dir=Path(tmp) / "cache",
                log_path=Path(tmp) / "calls.jsonl",
            )
            with patch("urllib.request.urlopen") as mocked:
                response = mocked.return_value.__enter__.return_value
                response.read.return_value = json.dumps(
                    {"content": [{"type": "text", "text": json.dumps({"ok": True})}]}
                ).encode()
                self.assertEqual(client.complete_json("prompt", purpose="test"), {"ok": True})
            self.assertNotIn("secret-key", (Path(tmp) / "calls.jsonl").read_text())


if __name__ == "__main__":
    unittest.main()
