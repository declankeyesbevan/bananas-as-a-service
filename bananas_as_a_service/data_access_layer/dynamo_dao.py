import os

import dpath

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from num2words import num2words
from word2number import w2n

from bananas_as_a_service.aws import connect_to_aws_resource
from bananas_as_a_service.log import Logger
from error_handler import GeneralError


# FIXME: all this flipping of words to numbers and back seems pretty hackish
# TODO: add a blacklist Dynamo table of nonsense words not found that will never be found
class DynamoDAO:

    def __init__(self, words):
        self._logger = Logger().get_logger()
        self._words = words
        self._found = []
        self._not_found = []
        self._resource = connect_to_aws_resource('dynamodb')
        self._table = self._get_table()
        self._partition_key = self._get_partition_key()

    @property
    def found(self):
        return self._found

    @property
    def not_found(self):
        return self._not_found

    # TODO: multi-thread this lookup
    def check_storage(self):
        """
        Looks up DynamoDB for metadata about word.

        The DynamoDB schema is defined as a String Partition Key but users may enter stringy ints.
        We definitely don't want to store or lookup ints as PKs so we do some hackery on the lookup
        side. Numbers to words and vice versa. This is because the OxfordDAO is well equipped to
        handle both kinds of "numbers" and DynamoDB is just for storage and retrieval purposes. Keep
        the AI tamed to a single place, lest we unleash the Machine Apocalypse.
        """
        for word in self._words:
            is_number, word = self._is_a_number(word)

            response = self._query_item(self._partition_key, word)
            if response.get('Count'):
                word = dpath.get(response, 'Items/*/word')
                self._logger.info(f"Word found in DynamoDB: {word}")
                item = {word: dpath.get(response, 'Items/*')}

                if is_number:
                    value = item.get(word)
                    word = w2n.word_to_num(word)
                    item = {word: value}

                self._found.append(item)
            else:
                self._logger.info(f"Word not found in DynamoDB: {word}")

                if is_number:
                    word = w2n.word_to_num(word)

                self._not_found.append(word)

    # TODO: multi-thread this put
    def update_storage(self, oxford_classifications):
        """
        Stores Oxford provided classifications to DynamoDB.

        See docstring for check_storage(): why we do all this string to int and back again madness.

        :param oxford_classifications:
        :type oxford_classifications: :class: list
        """
        for classification in oxford_classifications:
            word, *_ = list(classification)
            is_number, word = self._is_a_number(word)
            item = {self._partition_key: word}

            if is_number:
                word = w2n.word_to_num(word)

            item.update(classification.get(word))
            try:
                self._table.put_item(Item=item)
            except ClientError as exc:
                raise GeneralError(f"ClientError with DynamoDB put: {exc}")
            else:
                if is_number:
                    word = num2words(word)
                self._logger.info(f"Updated DynamoDB with word: {word}")

    def _get_table(self):
        try:
            table = self._resource.Table(os.environ['TABLE_NAME'])
        except KeyError:
            raise GeneralError("Missing DynamoDB table name environment variable")
        else:
            return table

    @classmethod
    def _get_partition_key(cls):
        try:
            partition_key = os.environ['PARTITION_KEY']
        except KeyError:
            raise GeneralError("Missing DynamoDB partition key environment variable")
        else:
            return partition_key

    def _query_item(self, key_name, key_value):
        try:
            response = self._table.query(KeyConditionExpression=Key(key_name).eq(key_value))
        except ClientError as exc:
            raise GeneralError(f"ClientError with DynamoDB query: {exc}")
        else:
            return response

    @classmethod
    def _is_a_number(cls, word):
        return (True, num2words(word)) if isinstance(word, int) else (False, word)
