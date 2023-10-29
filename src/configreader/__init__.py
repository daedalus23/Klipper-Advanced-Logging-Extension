from .single import Single
from .multiple import Multiple
import os

class Configuration(Single, Multiple):

    def __init__(self, path) -> None:
        """
        Load single configuration file  or Load directory of config files;
        :param path: --> str: Path given of config file or directory
        """
        self.path = path
        self.get_working_dir()
        if self._is_single_config():
            Single.__init__(self)
            self.load_single(self.path)
        else:
            Multiple.__init__(self)
            self.load_multi(self.path)

    def _is_single_config(self) -> bool:
        """
        Check if path is a single configuration file.
        :return: bool: True if single file, otherwise False
        """
        if os.path.isfile(self.path) and self.path.split(".")[-1] in Single.configFileTypes:
            return True
        return False
