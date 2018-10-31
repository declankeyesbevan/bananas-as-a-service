"""
Abstraction object for accessing YAML files.
"""

# pylint: disable=too-few-public-methods

import yaml

from yaml.error import YAMLError

from bananas_as_a_service.error_handler import GeneralError


class YAMLDAO:
    """
    Data Access Object for opening and parsing YAML files.
    """

    @classmethod
    def load_yaml_file(cls, input_file):
        """
        Attempt to load and parse a YAML file.

        :param input_file: PAth to YAML file
        :type input_file: :class: `str`
        :return: Parsed data
        :rtype: :class: `list`
        """

        try:
            with open(input_file) as yaml_file:
                data = yaml.load(yaml_file)
                if not data:
                    raise GeneralError("YAML file is empty")
        except (IOError, FileNotFoundError):
            raise GeneralError(f"Failed to open YAML file {data}")
        except YAMLError:
            raise GeneralError(f"Couldn't load data from YAML file {data}")
        else:
            return data
