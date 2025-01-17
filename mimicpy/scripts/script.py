"""Module for abstract script class"""

from collections import OrderedDict
from abc import ABC, abstractmethod
from ..utils.errors import ScriptError
from ..utils.file_handler import read


class Script(ABC):
    """stores internal attributes in a dictionary and script parameters in an ordered dictionary"""

    def __init__(self):
        self.__setattr__('__orddict__', OrderedDict())

    @property
    def parameters(self):
        return self.__orddict__
    
    def clear_parameters(self):
        self.__orddict__ = OrderedDict()

    def __setattr__(self, key, value):
        if key.startswith('_') or key == 'has_parameter' or key == 'parameters' or key == 'clear_parameters':
            # Private attributes, and helper functions are stored in __dict__
            self.__dict__[key] = value
        else:
            # All others are script parameters and stored in __orddict__
            self.__orddict__[key.replace(' ', '--').replace('-', '_').lower()] = value

    def __getattr__(self, key):
        key = key.lower()
        if key.startswith('_') or key == 'has_parameter' or key == 'parameters' or key == 'clear_parameters':
            return self.__getattribute__('__dict__')[key]
        try:
            return self.__getattribute__('__orddict__')[key]
        except KeyError:
            raise ScriptError(key)

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return self.__str__()

    def has_parameter(self, key):
        return bool(key in self.__orddict__)

    @classmethod
    @abstractmethod
    def from_string(cls, string):
        pass

    @classmethod
    def from_file(cls, file):
        if isinstance(file, Script):
            return file
        return cls.from_string(read(file, 'r'))
