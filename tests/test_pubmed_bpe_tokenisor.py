import os
import tempfile
from unittest import TestCase

from pubmed_bpe_tokeniser import PubmedBPETokenisor


class TestPubmedBPETokenisor(TestCase):

    def test_train(self):
        # Arrange
        data_file = os.path.join(os.path.dirname(__file__), "data", "sample_pubmed.json")
        sut = PubmedBPETokenisor(vocab_size=300)
        tempdir = tempfile.mkdtemp()
        output_file_json = os.path.join(tempdir, "vocab.json")

        # Act
        sut.train([data_file], output_file_json)

        # Assert
        self.assertTrue(os.path.getsize(output_file_json) > 100,
                        "Expected the vocab file size {} to be greater than 100")
