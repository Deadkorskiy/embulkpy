from typing import Union, Type, List
from . import EmbulkPlugin
import yaml
from ...tbl_file_util import TblFileUtil


class ExcelInEmbulkPlugin(EmbulkPlugin):
    # https://github.com/hishidama/embulk-parser-poi_excel

    class Column(object):

        def __init__(
                self,
                name: str,
                col_type: Union[Type, str]
        ):
            self.col_type = col_type if isinstance(col_type, str) else self.get_java_type_by_python(col_type)
            self.name = name

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
            sheets: List[str] = None,
            skip_header_lines: int = 0,
            *args, **kwargs):
        super().__init__(self.PluginType.IN, 'embulk-parser-poi_excel', *args, **kwargs)
        self.parser_type = 'poi_excel'
        self.path_prefix = path_prefix
        self.type = 'file'
        self.sheets = sheets or ['*']
        self.skip_header_lines = skip_header_lines
        self.columns = columns

    @property
    def config(self) -> str:
        config = {
            self.plugin_type: {
                'type': self.type,
                'path_prefix': self.path_prefix,
                'parser': {
                    'type': self.parser_type,
                    'sheets': self.sheets,
                    'skip_header_lines': self.skip_header_lines,
                    'columns': [{'name': x.name, 'type': x.col_type} for x in self.columns]
                }
            }
        }
        return yaml.dump(config)

    @classmethod
    def build(cls, f: TblFileUtil) -> 'ExcelInEmbulkPlugin':
        return cls(
            path_prefix=f.fp,
            columns=[cls.Column(name=col.name, col_type=col.py_type) for col in f.columns],
            sheets=[str(f.sheet_name)] if f.sheet_name is not None else ['*'],
            skip_header_lines=f.header_index if f.header_index is not None else 0
        )
