"""Opening and parsing YAML files."""

# pylint: disable=invalid-name, logging-fstring-interpolation

import yaml

from yaml.error import YAMLError

from cli_tools.cli_logger import get_logger

logger = get_logger()


def load_yaml_file(input_file):
    """
    Attempt to load and parse a YAML file.

    :param input_file: Path to YAML file
    :type input_file: :class: `str`
    :return: Parsed data
    :rtype: :class: `list` or `dict`
    """
    logger.info(f"Loading input file: {input_file}")

    try:
        with open(input_file) as yaml_file:
            data = yaml.load(yaml_file)
            if not data:
                raise RuntimeError()
    except RuntimeError:
        logger.error(f"YAML file is empty: {input_file}")
    except (IOError, FileNotFoundError):
        logger.error(f"Failed to open YAML file {data}")
    except YAMLError:
        logger.error(f"Couldn't load data from YAML file {data}")
    else:
        return data
