import json
import unittest
from local_generation_runtime_metadata_v1 import CheckedSettings


class MetadataTests(unittest.TestCase):
    def test_verified_context_does_not_rewrite_raw_settings(self):
        raw={'seed':42,'n_predict':512}
        checked=CheckedSettings(raw)
        self.assertEqual(checked['n_ctx'],4096)
        self.assertEqual(json.dumps(checked),json.dumps(raw))
        self.assertNotIn('n_ctx',checked)
        with self.assertRaises(KeyError): checked['other_missing_field']


if __name__ == '__main__': unittest.main()
