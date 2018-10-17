"""
Abstraction object for accessing lexical data about words from Oxford Dictionaries API.
"""

# pylint: disable=logging-fstring-interpolation, too-few-public-methods

import os

import dpath
import requests

from requests.exceptions import RequestException

from error_handler import GeneralError
from log import Logger


class OxfordDAO:
    """
    Data Access Object for making requests to the Oxford Dictionaries API.
    """

    # TODO: investigate data classes
    _APP_ID = os.environ.get('APP_ID')
    _APP_KEY = os.environ.get('APP_KEY')
    _BASE_URL = 'https://od-api.oxforddictionaries.com:443/api/v1/inflections/en/'
    _TO_PARSE = {
        'categories': 'lexicalCategory',
        'features': 'grammaticalFeatures',
        'inflection': 'inflectionOf',
    }
    _HTTP_SUCCESS = 200

    def __init__(self):
        self._logger = Logger().get_logger()
        self._words_not_found = 0

    def classify(self, tokens):
        """
        Request and parse lexical categories, grammatical features and inflections of words.

        :param tokens: Words to be classified
        :type tokens: :class: `list`
        :return: Lexical information about words
        :rtype: :class: `list`
        """
        self._logger.info(f"Classifying tokens: {tokens}")
        # TODO: think about handling downstream missing data from exceptions
        # FIXME: far too nested

        all_classifications = []
        for token in tokens:
            word = {}
            if isinstance(token, int):
                word.update({'categories': ['number']})
            else:
                try:
                    response = requests.get(
                        f'{self._BASE_URL}{token.lower()}',
                        headers={'app_id': self._APP_ID, 'app_key': self._APP_KEY})
                    if response.status_code != self._HTTP_SUCCESS:
                        self._words_not_found += 1
                        raise RequestException
                except RequestException as exc:
                    self._logger.error(
                        f"Unable to get word: '{token}' from API due to: {exc}", exc_info=True)
                else:
                    word = self._categorise(response, word)

            all_classifications.append({token: word})

        if self._words_not_found:
            self._logger.error(f"Number of word(s) not found: {self._words_not_found}")

        if not all_classifications:
            raise GeneralError("Exiting due to no words matched")

        self._logger.info(f"Number of word(s) processed: {len(all_classifications)}")

        return all_classifications

    def _categorise(self, response, word):
        for key, value in self._TO_PARSE.items():
            parsed = [
                category.get(value) for category in
                dpath.values(response.json(), '**/lexicalEntries/*')]
            word.update({key: self._to_lower(parsed)})
        return word

    @classmethod
    def _to_lower(cls, parsed):
        for index, item in enumerate(parsed):
            if isinstance(item, str):
                parsed[index] = item.lower()
            elif isinstance(item, list):
                for feature in item:
                    for key, value in feature.items():
                        feature.update({key: value.lower()})
        return parsed
