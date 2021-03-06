"""Abstraction object for accessing lexical data about words from Oxford Dictionaries API."""

# pylint: disable=logging-fstring-interpolation, too-few-public-methods

from threading import Thread

import dpath
import requests

from requests.exceptions import RequestException

from bananas_as_a_service.app_logger import Logger
from bananas_as_a_service.aws import get_from_parameter_store
from bananas_as_a_service.error_handler import GeneralError


class OxfordDAO:
    """Data Access Object for making requests to the Oxford Dictionaries API."""

    # TODO: investigate data classes
    _BASE_URL = 'https://od-api.oxforddictionaries.com:443/api/v1/inflections/en/'
    _TO_PARSE = {
        'categories': 'lexicalCategory',
        'features': 'grammaticalFeatures',
        'inflection': 'inflectionOf',
    }
    _HTTP_OK = 200
    _HTTP_FORBIDDEN = 403

    def __init__(self):
        self._logger = Logger().get_logger()
        self._results = None
        self._words_not_found = 0
        self._app_id = None
        self._app_key = None
        self._load_credentials()

    def classify(self, tokens):
        """
        Request and parse lexical categories, grammatical features and inflections of words.

        As we are hitting an external API for every single word to classify, and calls to that API
        take about a second each, and each of these calls is I/O bound, and none of those calls can
        cause a race condition, let's go ahead and get all multi-threaded all up in this hizzle.

        Big shout out to these two MT-spirational peeps:
        https://www.shanelynn.ie/using-python-threading-for-multiple-results-queue/
        https://www.amazon.com/Core-Python-Applications-Programming-3rd/dp/0132678209

        :param tokens: Words to be classified
        :type tokens: :class: `list`
        :return: Lexical information about words
        :rtype: :class: `list`
        """
        self._logger.info(f"Classifying tokens: {tokens}")
        # TODO: use `Queue` for batching to prevent error and to make event driven

        app_id, app_key = self._load_credentials()
        self._results = [{} for _ in tokens]
        threads = []
        for index, token in enumerate(tokens):
            if isinstance(token, int):
                self._results[index] = {token: {'categories': ['number']}}
            else:
                thread = Thread(target=self._request_from_api, args=(token, index, app_id, app_key))
                thread.start()
                threads.append(thread)

        for thread in threads:
            thread.join()

        if self._words_not_found:
            self._logger.info(f"Number of word(s) not found: {self._words_not_found}")

        if not self._results:
            raise GeneralError("Exiting due to no words matched")

        self._logger.info(f"Word(s) processed from OxfordDAO: {len(self._results)}")
        return [result for result in self._results if result]

    @classmethod
    def _load_credentials(cls):
        ssm_parameters = get_from_parameter_store(['app_id', 'app_key'])
        return ssm_parameters['app_id'], ssm_parameters['app_key']

    def _request_from_api(self, token, index, app_id, app_key):
        word = {}
        try:
            response = requests.get(
                f'{self._BASE_URL}{token.lower()}',
                headers={'app_id': app_id, 'app_key': app_key}
            )
            if response.status_code == self._HTTP_FORBIDDEN:
                raise GeneralError("Incorrect app credentials")
            if response.status_code != self._HTTP_OK:
                self._words_not_found += 1
                raise RequestException
        except RequestException as exc:
            self._logger.error(
                f"Unable to get word: '{token}' from API due to: {exc}", exc_info=True)
            self._results[index] = {}
        else:
            word = self._categorise(response, word)
            self._results[index] = {token: word}
        return True

    def _categorise(self, response, word):
        for key, value in self._TO_PARSE.items():
            parsed = [
                category.get(value) for category in
                dpath.values(response.json(), '**/lexicalEntries/*')
            ]
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
