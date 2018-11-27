"""Parsing command line arguments."""

import argparse


def parse_args():
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
    parser.add_argument('-p', '--performance', required=False, help='Log performance metrics')
    return parser.parse_args()
