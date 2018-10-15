#!/usr/bin/python

"""
This module is a command line script for parsing your friend's phrases and turning them into
somewhat readable, sorta, kinda English language sentences. It uses advanced Aritifical Intelligence
Machine Learning AKA sentences can generally follow this basic syntax: adverb, adjective, noun. It
also takes into account if your friend has a favourite number, for example five. Numbers go first in
this basic syntax.

Create a YAML file with a list of phrases e.g.:
  - "Cool bananas"
  - "Cool beans"
  - "5 minutes"
  - "Five minutes"
  - "Sick"
  - "Easy"
This should then be passed to this script as a command line argument e.g.:
banana.py --bananas phrases.yml

First the phrases will be tokenised i.e. anything that isn't a word, number or whitespace will be
removed. The result will be lowercased; white-space split; de-duplicated. Next the words will be
classified i.e. they will be lexically categorised e.g. number, verb. If a number is passed as a
word and it is under a billion it will be converted to an integer. A billion and over will cause an
explosion. The non-numbers amongst the words will be classified using the Oxford English Dictionary
API. Using advanced AI Natural Language Processing technologies the words will be cleaned i.e. if
the lexical category isn't on the super basic list of words, just throw it away. This is how AI
works, I promise. Don't look behind the curtain. Finally this is where the
AI/Matrix Machines/Terminators really get their AI on. Using the super-advanced word ordering from
above a bunch of sentences are constructed. And they are totes legit. Finally these are dumped to
our friendly neighbourhood `StreamHandler` logger.
"""

# pylint: disable=invalid-name, logging-fstring-interpolation, ungrouped-imports

import argparse
import logging
import os
import re

import dpath
import requests
import yaml

from num2words import num2words
from ordered_set import OrderedSet
from requests.exceptions import RequestException
from word2number import w2n
from yaml.error import YAMLError

GENERAL_ERROR = 42
ORDERING = ['number', 'adverb', 'adjective', 'noun']
MAX_ADVERB = MAX_ADJECTIVE = 2
MAX_NUMBER = MAX_NOUN = 1
NUMBERS_AS_WORDS = 10
APP_ID = os.environ.get('APP_ID')
APP_KEY = os.environ.get('APP_KEY')
BASE_URL = 'https://od-api.oxforddictionaries.com:443/api/v1/inflections/en/'
TO_PARSE = {
    'categories': 'lexicalCategory',
    'features': 'grammaticalFeatures',
    'inflection': 'inflectionOf',
}


logging.basicConfig(
    format='%(asctime)s %(processName)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
if logger.hasHandlers():
    logger.handlers.clear()


def execute():
    """Entry point to parse command line argument of file to read of your friend's phrases"""

    args = _parse_args()
    data = _load_yaml_file(args.bananas)
    tokens = _tokenise(data)
    words_as_numbers = list(set(_words_to_numbers(tokens)))
    classified = _classify(words_as_numbers)
    cleaned = _clean(classified)
    ordered = _order(cleaned)
    sentenced = _make_some_sentences(ordered)

    for sentence in sentenced:
        logger.info(sentence)


def _parse_args():
    parser = argparse.ArgumentParser(
        description=(
            'Pass in your friend\'s favourite phrases and get back some '
            'magical, definitely AI, remixed phrasal goodness. Probably.'
        )
    )
    parser.add_argument(
        '-b', '--bananas', required=True, help='YAML file containing phrases to "machine learn"')
    return parser.parse_args()


def _load_yaml_file(input_file):
    try:
        with open(input_file) as yaml_file:
            data = yaml.load(yaml_file)
    except (IOError, FileNotFoundError):
        _handle_exception(f"Failed to open YAML file {data}")
    except YAMLError:
        _handle_exception(f"Couldn't load data from YAML file {data}")
    else:
        return data


def _tokenise(data):
    all_your_token_are_belong_to_us = set()
    for phrase in data:
        youre_not_special = re.sub(r'([^\s\w]|_)+', '', phrase)
        all_your_token_are_belong_to_us.update(set(youre_not_special.lower().split(' ')))
    return list(all_your_token_are_belong_to_us)


def _classify(tokens):
    all_classifications = []
    for token in tokens:
        word = {}
        if isinstance(token, int):
            word.update({'categories': ['number']})
        else:
            try:
                response = requests.get(
                    f'{BASE_URL}{token.lower()}', headers={'app_id': APP_ID, 'app_key': APP_KEY})
            except RequestException as exc:
                logger.exception(f"Unable to contact word API: {exc}")
            else:
                word = _categorise(response, word)
        all_classifications.append({token: word})
    return all_classifications


def _categorise(response, word):
    for k, v in TO_PARSE.items():
        parsed = [
            category.get(v) for category in dpath.values(response.json(), '**/lexicalEntries/*')]
        word.update({k: _to_lower(parsed)})
    return word


def _words_to_numbers(tokens):
    for index, token in enumerate(tokens):
        try:
            as_number = w2n.word_to_num(token)
        except ValueError:
            pass  # Ignore other words
        else:
            tokens[index] = as_number
    return tokens


def _to_lower(parsed):
    for index, item in enumerate(parsed):
        if isinstance(item, str):
            parsed[index] = item.lower()
        elif isinstance(item, list):
            for feature in item:
                for k, v in feature.items():
                    feature.update({k: v.lower()})
    return parsed


def _clean(classified):
    for word in classified:
        for value in word.values():
            for category in value.get('categories'):
                if category not in ORDERING:
                    value.get('categories').remove(category)
    return classified


def _order(cleaned):
    numbers, adverbs, adjectives, nouns, sentences = ([] for _ in range(5))
    for words in cleaned:
        for k, v in words.items():
            if 'number' in v.get('categories'):
                numbers.append(k)
            if 'adverb' in v.get('categories'):
                adverbs.append(k)
            if 'adjective' in v.get('categories'):
                adjectives.append(k)
            if 'noun' in v.get('categories'):
                nouns.append(k)

    for number in numbers:
        for adverb in adverbs:
            for adjective in adjectives:
                for noun in nouns:
                    sentences.append([number, adverb, adjective, noun])

    duplicates_removed = OrderedSet([tuple(OrderedSet(sentence)) for sentence in sentences])
    no_need_for_numbers = OrderedSet([
        tuple(sentence[1:]) for sentence in duplicates_removed
        if isinstance(_get_first(sentence), int)
    ])

    return duplicates_removed.union(no_need_for_numbers)


def _make_some_sentences(ordered):
    ordered = list(map(list, ordered))
    for sentence in ordered:
        first_word = _get_first(sentence)
        if isinstance(first_word, int):
            sentence[0] = (
                num2words(first_word).capitalize() if first_word < NUMBERS_AS_WORDS
                else str(first_word)
            )
        else:
            sentence[0] = str(first_word).capitalize()
    return [f"{' '.join(sentence)}." for sentence in ordered]


def _get_first(collection):
    return collection[0]


def _handle_exception(message):
    logger.exception(message)
    exit(GENERAL_ERROR)


if __name__ == '__main__':
    execute()
