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
This should then be passed to the runner entry point located in the project root directory as a
command line argument e.g.:
python go_bananas.py --bananas phrases.yml

First the phrases will be tokenised i.e. anything that isn't a word or whitespace will be
removed. The result will be lowercased; white-space split; de-duplicated.

Next, if a number is passed as a word or string and it is under a billion it will be converted to an
integer. A billion and over will cause an explosion.

Then the words will be classified i.e. they will be lexically categorised e.g. number, verb. The
non-numbers amongst the words will be classified using the Oxford English Dictionary API. Integers
will be labelled as numbers. Grammatical features and inflections will also be looked up.

Using advanced AI Natural Language Processing technologies the words will be cleaned i.e. if
the lexical category isn't on the super basic list of words, just throw it away. This is how AI
works, I promise. Don't look behind the curtain.

Finally this is where the AI/Matrix/Machines/Terminators really get their AI on. Using the
super-advanced word ordering from above a bunch of sentences are constructed. And they are totes
legit. Finally these are dumped to our friendly neighbourhood `StreamHandler` logger.
"""

# pylint: disable=invalid-name, logging-fstring-interpolation, ungrouped-imports
# pylint: disable=too-few-public-methods

import re

from num2words import num2words
from ordered_set import OrderedSet
from word2number import w2n

from data_access_layer.user_dao import UserDAO
from data_access_layer.yaml_dao import YAMLDAO
from log import Logger
from word_classifier import WordClassifier


class Banana:
    """
    Turns common phrases into new and fun sentences.
    """

    _ORDERING = ['number', 'adverb', 'adjective', 'noun']
    _NUMBERS_AS_WORDS = 10

    def __init__(self):
        self._logger = Logger().get_logger()

    def execute(self):
        """
        Entry point to parse command line argument of file to read of your friend's phrases.

        Procedural style of programming where we fetch what we want, pass it for processing and use
        the returned value for the next process; not a true "object".
        """

        args = UserDAO().parse_args()
        data = YAMLDAO().load_yaml_file(args.bananas)
        tokens = self._tokenise(data)
        words_as_numbers = list(set(self._words_to_numbers(tokens)))
        classified = WordClassifier().classify(words_as_numbers)
        cleaned = self._clean(classified)
        ordered = self._order(cleaned)
        sentenced = self._make_some_sentences(ordered)

        for sentence in sentenced:
            self._logger.info(sentence)

    @classmethod
    def _tokenise(cls, data):
        # Get rid of anything that isn't a word or space, then make them uniformly lower case.
        all_your_token_are_belong_to_us = set()
        for phrase in data:
            youre_not_special = re.sub(r'([^\s\w]|_)+', '', phrase)
            all_your_token_are_belong_to_us.update(set(youre_not_special.lower().split(' ')))
        return list(all_your_token_are_belong_to_us)

    @classmethod
    def _words_to_numbers(cls, tokens):
        for index, token in enumerate(tokens):
            try:
                as_number = w2n.word_to_num(token)
            except ValueError:
                pass  # Ignore other words
            else:
                tokens[index] = as_number
        return tokens

    def _clean(self, classified):
        # This is a very simple sentence generator so throw away categories we don't account for.
        for word in classified:
            for value in word.values():
                for category in value.get('categories'):
                    if category not in self._ORDERING:
                        value.get('categories').remove(category)
        return classified

    def _order(self, cleaned):
        mapped = {}
        for words in cleaned:
            for key, value in words.items():
                for kind in self._ORDERING:
                    if kind in value.get('categories'):
                        mapped.setdefault(kind, []).append(key)

        # Order the words in the sentence using a basic English language syntax.
        sentences = []
        for number in mapped.get('number'):
            for adverb in mapped.get('adverb'):
                for adjective in mapped.get('adjective'):
                    for noun in mapped.get('noun'):
                        sentences.append([number, adverb, adjective, noun])

        duplicates_removed = OrderedSet([tuple(OrderedSet(sentence)) for sentence in sentences])
        no_need_for_numbers = OrderedSet([
            tuple(sentence[1:]) for sentence in duplicates_removed
            if isinstance(self._get_first(sentence), int)
        ])

        return duplicates_removed.union(no_need_for_numbers)

    def _make_some_sentences(self, ordered):
        ordered = list(map(list, ordered))
        for sentence in ordered:
            first_word = self._get_first(sentence)
            self._set_first(first_word, sentence)
        return [f"{' '.join(sentence)}." for sentence in ordered]

    @classmethod
    def _get_first(cls, collection):
        return collection[0]

    def _set_first(self, first_word, sentence):
        # Only use digits for 10 and up, below is words e.g. five. Always capitalise the sentence.
        if isinstance(first_word, int):
            sentence[0] = (
                num2words(first_word).capitalize() if first_word < self._NUMBERS_AS_WORDS
                else str(first_word)
            )
        else:
            sentence[0] = str(first_word).capitalize()
