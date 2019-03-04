"""
API for accessing lexical data about words. Currently, first accesses the DynamoDAO and falls back
to the OxfordDAO for missing word. Future implementation will have ElastiCache before DynamoDB.
"""

# pylint: disable=too-few-public-methods, logging-fstring-interpolation

from bananas_as_a_service.data_access_layer.dynamo_dao import DynamoDAO
from bananas_as_a_service.data_access_layer.oxford_dao import OxfordDAO
from bananas_as_a_service.app_logger import Logger


class WordClassifier:
    """API to hide implementation of where lexical data about words comes from."""

    def __init__(self, words):
        """
        :param words: Words to be classified
        :type words: :class: `list`
        """
        self._logger = Logger().get_logger()
        self._dynamo_dao = DynamoDAO(words)
        self._oxford_dao = OxfordDAO()
        self._classified = []

    def classify(self):
        """
        Returns lexical data about passed words.

        First attempts to find data per word in DynamoDB; if that fails those words are queried via
        the Oxford Dictionaries API directly.

        :return: Lexical information about words
        :rtype: :class: `list`
        """
        self._logger.info("Looking up lexical data")

        self._dynamo_dao.check_storage()

        if self._dynamo_dao.found:
            self._classified.extend(self._dynamo_dao.found)
            self._logger.info(f"Word(s) found in DynamoDB: {len(self._dynamo_dao.found)}")
        if self._dynamo_dao.not_found:
            oxford_classifications = self._oxford_dao.classify(self._dynamo_dao.not_found)
            self._classified.extend(oxford_classifications)
            self._dynamo_dao.update_storage(oxford_classifications)
            self._logger.info(f"Word(s) not found in DynamoDB: {len(self._dynamo_dao.not_found)}")

        return self._classified
