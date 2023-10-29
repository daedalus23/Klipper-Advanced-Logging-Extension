from configparser import SafeConfigParser, ConfigParser
from .baseconfiguration import BaseConfiguration
import os

__all__ = ["Multiple"]


"""
Multiple module/class parses & loads configuration file sections,
content from a given directory. Takes file directory & will load
dict format data into 'multiContent' attribute named as file name
in directory.
"""


class Multiple(BaseConfiguration):
    def __init__(self):
        super().__init__()
        self._ConfigObj = ConfigParser()
        self._multiDirectory = None
        self._fileObject = None
        self._dirList = []
        self.multiContent = {}
        self._numConfigs = 0

    def add_multi_content(self, newContent, fileName) -> None:
        """Adds new section & content to configObj"""
        for configFile in self._dirList:
            if fileName == configFile["fileName"]:
                self._fileObject = configFile
                self._multi_load_content()
        sectionName, sectionContent = self.prepare_content(newContent)
        if sectionName and sectionContent:
            self._ConfigObj[sectionName.lower()] = sectionContent
            self._multi_write_file()

    def clear_multi_cache(self) -> None:
        """Clear & reset cache for next configuration file to be loaded"""
        self._ConfigObj = ConfigParser()
        self.sections = []
        self.content = {}

    @staticmethod
    def create_config_dict(file, path) -> dict:
        """Create config file structure of file information"""
        tempfileName, tempfileExt = file.split(".")
        tempFile = {
            "fileName": tempfileName,
            "fileExt": tempfileExt,
            "fullFileName": file,
            "filePath": rf"{path}\{file}"
        }
        return tempFile

    def _create_multi_dict(self) -> None:
        """Check if path is directory of configuration files"""
        for file in os.listdir(self._multiDirectory):
            for fileType in Multiple.configFileTypes:
                if fileType in file.split(".")[1]:
                    self._numConfigs += 1
                    self._dirList.append(
                        self.create_config_dict(file, self._multiDirectory)
                    )

    def load_multi(self, path) -> None:
        """Load directory of config files"""
        self._multiDirectory = path
        self._create_multi_dict()
        for configFile in self._dirList:
            self._fileObject = configFile
            self._multi_load_content()
            self.clear_multi_cache()

    def _multi_load_content(self) -> None:
        """Load content from config file & return dict."""
        self._multi_load_sections()
        parser = SafeConfigParser()
        parser.optionxform = str
        found = parser.read(rf"{self.workingDir}\{self._fileObject['filePath']}")
        if not found:
            raise ValueError('No config file found!')
        for name in self.sections:
            self.content[f"{name}"] = {key: self.parse_value(val) for key, val in parser.items(name)}
        self.multiContent[self._fileObject["fileName"]] = self.content

    def _multi_load_sections(self) -> None:
        """Load all sections of ini file into class sections list."""
        self._multi_read_file()
        self.sections = self._ConfigObj.sections()

    def _multi_read_file(self) -> None:
        """Read file from path and return content."""
        with open(rf"{self.workingDir}\{self._fileObject['filePath']}", "r") as file:
            self._ConfigObj.read_file(file)

    def _multi_write_file(self) -> None:
        """Writes ConfigObj to class INI file"""
        with open(rf"{self.workingDir}\{self._fileObject['filePath']}", "w") as file:
            self._ConfigObj.write(file)
