"""
Abstraction object for accessing user data.
"""

# pylint: disable=too-few-public-methods

import argparse


class UserDAO:
    """
    Data Access Object for users.
    """

    @classmethod
    def parse_args(cls):
        """
        Defines and parses command line arguments.

        :return: Parsed arguments
        :rtype: :class: `sys.argv`
        """

        parser = argparse.ArgumentParser(
            description=(
                'Pass in your friend\'s favourite phrases and get back some '
                'magical, definitely AI, remixed phrasal goodness. Probably.'
            )
        )
        parser.add_argument(
            '-b', '--bananas', required=True, help='YAML file containing phrases to "machine learn"'
        )
        return parser.parse_args()
