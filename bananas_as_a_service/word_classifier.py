"""
API for accessing lexical data about words. Currently only uses the OxfordDAO, with future storage
and caching this will be a defined public interface that will hide this implementation.
"""

# pylint: disable=too-few-public-methods

from data_access_layer.oxford_dao import OxfordDAO
from log import Logger


class WordClassifier:
    """
    API to hide implementation of where lexical data about words comes from.
    """

    def __init__(self):
        self._logger = Logger().get_logger()

    def classify(self, words):
        """
        Returns lexical data about passed words.

        Currently only accesses Oxford Dictionaries API directly.

        :param words: Words to be classified
        :type words: :class: `list`
        :return: Lexical information about words
        :rtype: :class: `list`
        """
        self._logger.info("Looking up lexical data in Oxford Dictionaries API")

        return OxfordDAO().classify(words)
