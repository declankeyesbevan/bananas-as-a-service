"""
Abstraction object for accessing lexical data about words from Oxford Dictionaries API.
"""

# pylint: disable=logging-fstring-interpolation, too-few-public-methods

import os

import dpath
import requests

from requests.exceptions import RequestException

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

    def __init__(self):
        self._logger = Logger().get_logger()

    def classify(self, tokens):
        """
        Request and parse lexical categories, grammatical features and inflections of words.

        :param tokens: Words to be classified
        :type tokens: :class: `list`
        :return: Lexical information about words
        :rtype: :class: `list`
        """
        self._logger.info(f"Classifying tokens: {tokens}")

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
                except RequestException as exc:
                    # TODO: think about handling this for downstream missing data
                    self._logger.exception(f"Unable to get word from API: {exc}")
                else:
                    word = self._categorise(response, word)
            all_classifications.append({token: word})
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
