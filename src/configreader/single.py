from configparser import SafeConfigParser, ConfigParser
from .baseconfiguration import BaseConfiguration

__all__ = ["Single"]


"""
Single module/class parses & loads sections, content of one specific
configuration file given. Takes absolute path of configuration file,
will load into content attribute in dict format. New content is
writable to the same configuration file given.
"""


class Single(BaseConfiguration):
    def __init__(self):
        super().__init__()
        self._ConfigObj = ConfigParser()
        self._singleFullPath = None
        self.content = {}

    def load_single(self, path) -> None:
        """Load single configuration file"""
        self._singleFullPath = path
        self._single_load_content()
        self._parse_list_single_content()

    def add_content(self, newContent: dict) -> None:
        """Adds new sections & content to configObj."""
        for sectionName, sectionContent in newContent.items():
            self._ConfigObj[sectionName.lower()] = sectionContent
        self._single_write_file()

    def _single_load_content(self) -> None:
        """Load content from config file & return dict."""
        self._single_load_sections()
        parser = SafeConfigParser()
        parser.optionxform = str
        found = parser.read(rf"{self.workingDir}\{self._singleFullPath}")
        if not found:
            raise ValueError('No config file found!')
        for name in self.sections:
            self.content[name] = {key: parse_value(val) for key, val in parser.items(name)}

    def _single_load_sections(self) -> None:
        """Load all sections of ini file into class sections list."""
        self._single_read_file()
        self.sections = self._ConfigObj.sections()

    def _single_read_file(self) -> None:
        """Read file from path and return content."""
        with open(rf"{self.workingDir}\{self._singleFullPath}", "r") as file:
            self._ConfigObj.read_file(file)

    def _single_write_file(self) -> None:
        """Writes ConfigObj to class INI file"""
        with open(rf"{self.workingDir}\{self._singleFullPath}", "w") as file:
            self._ConfigObj.write(file)

    def _parse_list_single_content(self, delimiter="**") -> None:
        """Parse single file content into list type"""
        for section in self.content:
            for item in self.content[section]:
                if delimiter in self.content[section][item]:
                    self.content[section][item] = self.parse_list_content(self.content[section][item])
