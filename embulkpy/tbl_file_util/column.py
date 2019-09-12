from typing import Type, Callable


class Column(object):

    def __init__(
            self,
            name: str = None,
            index: int = None,
            py_type: Type = None,
            convertor: Callable[[object, dict], object] = None  # convertor(value, **kwargs) -> converted_value
    ):
        self.name = name
        self.index = index
        self.convertor = convertor
        self.py_type = py_type

