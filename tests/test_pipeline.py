import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rpapercodeaudit.heuristics import extract_no_api
from rpapercodeaudit.llm import LLMClient, LLMConfig

class PipelineTests(unittest.TestCase):
    def test_no_api_heuristic_returns_valid_claims(self):
        result=extract_no_api("Methods. We use a threshold of 10 counts. This is background.")
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.accepted[0].verbatim_sentence, "We use a threshold of 10 counts.")
    def test_provider_client_is_mockable_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=LLMClient(LLMConfig("openai-compatible","http://example.invalid","key","model"),cache_dir=Path(tmp)/"cache",log_path=Path(tmp)/"calls.jsonl")
            fake={"claims": []}
            with patch("urllib.request.urlopen") as mocked:
                response=mocked.return_value.__enter__.return_value
                response.read.return_value=json.dumps({"choices":[{"message":{"content":json.dumps(fake)}}]}).encode()
                self.assertEqual(client.complete_json("prompt", purpose="test"), fake)
                self.assertTrue(mocked.called)
                log=Path(tmp)/"calls.jsonl"; self.assertNotIn("key", log.read_text())
                self.assertEqual(client.complete_json("prompt", purpose="test"), fake)
                self.assertEqual(mocked.call_count, 1)
if __name__ == "__main__": unittest.main()
