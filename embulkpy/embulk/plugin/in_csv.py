from typing import Union, Type, List
from . import EmbulkPlugin
import yaml
from ...tbl_file_util import TblFileUtil


class CSVInEmbulkPlugin(EmbulkPlugin):
    # https://github.com/kazup0n/embulk-parser-csv_with_default_value

    class Column(object):

        def __init__(
                self,
                name: str,
                col_type: Union[Type, str],
                col_format: str = None,
                default_type: str = 'null',
                default_value: str = None
        ):
            self.col_type = col_type if isinstance(col_type, str) else self.get_java_type_by_python(col_type)
            self.name = name
            self.col_format = col_format
            self.default_type = default_type
            self.default_value = default_value

        @classmethod
        def get_java_type_by_python(cls, python_type: Type) -> str:
            if python_type == int:
                return 'long'
            if python_type == float:
                return 'double'
            return 'string'

    def __init__(
            self,
            path_prefix: str,
            columns: List[Column],
            delimiter: str = ',',
            header_line: bool = False,
            *args, **kwargs):
        super().__init__(self.PluginType.IN, 'embulk-parser-csv_with_default_value', *args, **kwargs)
        self.parser_type = 'csv_with_default_value'
        self.path_prefix = path_prefix
        self.type = 'file'
        self.delimiter = delimiter
        self.header_line = header_line
        self.columns = columns

    @property
    def config(self) -> str:

        cols = []
        cols_default_values = {}
        for row in self.columns:
            col = {
                'name': row.name,
                'type': row.col_type,
            }
            if row.col_format is not None:
                col.update({'format': row.col_format})
            cols.append(col)

            default_settings = {'default_value': row.default_value or None}
            if row.col_type in ['long', 'double', 'timestamp']:
                default_settings.update({'type': row.default_type})
            cols_default_values.update({row.name: default_settings})

        config = {
            self.plugin_type: {
                'type': self.type,
                'path_prefix': self.path_prefix,
                'parser': {
                    'type': self.parser_type,
                    'delimiter': self.delimiter,
                    'header_line': self.header_line,
                    'columns': cols
                    # 'default_values':cols_default_values
                }
            }
        }
        return yaml.dump(config)

    @classmethod
    def build(cls, f: TblFileUtil) -> 'CSVInEmbulkPlugin':
        return cls(
            delimiter=f.delimiter,
            header_line= True if f.header_index is not None else False,
            columns=[cls.Column(name=col.name, col_type=col.py_type) for col in f.columns],
            path_prefix=f.fp
        )
