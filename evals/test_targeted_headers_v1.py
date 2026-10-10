"""A subword-cut header must not merge with the original passage body."""
import unittest
from tokenizers import Tokenizer, models, pre_tokenizers
from targeted_retrieval_methods import embedding_views


class HeaderBoundary(unittest.TestCase):
    def test_separator_after_subword_header_cut(self):
        tokenizer = Tokenizer(models.WordPiece({'[UNK]': 0, 'a': 1, '##a': 2}, unk_token='[UNK]'))
        tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
        inputs, _ = embedding_views([{'id': 'synthetic', 'title': 'a' * 40, 'text': 'BODY'}], tokenizer)
        self.assertTrue(inputs[0].endswith('. BODY'), 'Header and body must retain a delimiter')


if __name__ == '__main__':
    unittest.main()
