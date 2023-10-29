import os
from collections.abc import Iterable

__all__ = ["BaseConfiguration"]


"""
BaseConfiguration module/class is base level attributes of both
shared types of configuration usage Single/Multiple. Adding
file extensions to BaseConfiguration attribute 'configFileTypes'
more file extensions can be loaded & read.
"""


class BaseConfiguration:
    workingDir = None
    sections = []
    content = {}
    configFileTypes = ["ini", "cnf", "conf"]

    def _check_config_path(self, path) -> bool:
        """Check for config file in path"""
        return any(fileType in path for fileType in self.configFileTypes)

    @staticmethod
    def check_iterator(item) -> bool:
        """Check if object is iterable"""
        return isinstance(item, Iterable) and not isinstance(item, str)

    def get_working_dir(self) -> None:
        """Get current working directory"""
        self.workingDir = os.path.abspath(os.curdir)

    @staticmethod
    def parse_list_content(newContent) -> list:
        """Parse loaded content into list starting with '**'"""
        return [item.strip() for item in newContent.strip("**").split(",")]

    @staticmethod
    def prepare_content(newContent) -> tuple:
        """Parse Key from Dict to set Section name of config.ini"""
        # Check if the input is a dictionary.
        if isinstance(newContent, dict):
            sectionName = list(newContent.keys())[0]
            sectionContent = newContent[sectionName]
            return sectionName, sectionContent
        # Return None if it's not a dictionary.
        return None, None

    @staticmethod
    def parse_value(value: str):
        """Parse value based on type annotations."""
        if value.startswith("int:"):
            return int(value.split(":", 1)[1])
        elif value.startswith("str:"):
            return value.split(":", 1)[1]
        elif value.startswith("hex:"):
            return bytes.fromhex(value.split(":", 1)[1])
        elif value.startswith("bool:"):
            return bool(value.split(":", 1)[1])
        elif value.startswith("float:"):
            return float(value.split(":", 1)[1])
        else:
            return value
