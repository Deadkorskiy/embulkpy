import os
from typing import Union, List, Type, Callable
import chardet
import pandas as pd
import pathlib
from . import detect_delimiter, Column


class TblFileUtil(object):

    DEFAULT_BYTES_BATCH_SIZE = 512000   # 512 kbytes

    def __init__(
            self,
            fp: str,
            columns: List[Column] = None,
            header_index: int = None,    # индекс строки заголовка
            encoding: str = None,
            newline: str = '\n',
            delimiter: str = None,
            bytes_batch_size: int = None,
            sheet_name: Union[str, int] = 0
    ):

        if not os.path.isfile(fp):
            raise Exception('File error. "{}" is it file?'.format(str(fp)))
        self.fp = fp
        self.newline = newline
        self.__encoding = encoding
        self.__delimiter = delimiter
        self.__columns = columns
        self.header_index = header_index
        self.sheet_name = sheet_name
        bytes_batch_size = bytes_batch_size or self.DEFAULT_BYTES_BATCH_SIZE
        self.bytes_batch_size = bytes_batch_size if bytes_batch_size < self.size else self.size

    @property
    def size(self) -> int:
        return os.path.getsize(self.fp)

    @property
    def extension(self) -> str:
        """
        :return: Ex: 'yml', 'js', ...
        """
        return pathlib.Path(self.fp).suffix.replace('.', '').lower()

    @property
    def encoding(self) -> str:
        if self.__encoding:
            return self.__encoding
        data = self.get_bytes(self.bytes_batch_size)
        encoding = chardet.detect(data) # {'encoding': 'windows-1251', 'confidence': 0.9155623761125045, 'language': 'Russian'}

        if isinstance(encoding, list) and encoding:
            encoding = encoding[0]
        self.__encoding = encoding['encoding']
        return self.encoding

    @property
    def delimiter(self) -> str:
        if self.__delimiter:
            return self.__delimiter

        bytes_batch_size_line_count = self.bytes_batch_size_line_count
        line_count = 5 if 5 <= bytes_batch_size_line_count else bytes_batch_size_line_count

        stings = self.get_lines_smart(line_count)
        delimiters = [detect_delimiter(s) for s in stings]

        count = 0
        for delimiter in delimiters:
            duplicate_count = delimiters.count(delimiter)
            if duplicate_count == len(delimiters):
                self.__delimiter = delimiter
                return self.delimiter
            if count < duplicate_count:
                count = duplicate_count
                self.__delimiter = delimiter
        return self.delimiter

    def get_bytes(self, count: int = -1) -> bytes:
        with open(self.fp, 'rb') as f:
            b = f.read(count)
        return b

    def get_lines(self, count: int = -1) -> List[str]:
        with open(self.fp, 'r', encoding=self.encoding, newline=self.newline) as f:
            return f.readlines(count)

    def get_lines_smart(self, count: int = -1, start: int = 10, stop: int = 10000, step: int = 100) -> List[str]:
        """
        Если у файла "кривой" newline - иногда требуется сделать count 1000 чтобы получить 5 строк ¯\_(ツ)_/¯
        """
        if count == -1:
            return self.get_lines(count)
        for row in range(start, stop, step):
            lines = self.get_lines(row)
            if len(lines) >= count:
                return lines[:count]

    @property
    def bytes_batch_size_line_count(self) -> int:
        """Сколько строк в bytes_batch_size"""
        return self.get_bytes(self.bytes_batch_size).count(self.newline.encode())

    def load(self, skiprows: int = 0, nrows: int = None, header: int = 0) -> pd.DataFrame:
        if self.extension == 'csv':
            df = pd.read_csv(
                self.fp,
                encoding=self.encoding,
                delimiter=self.delimiter,
                skiprows=skiprows,
                nrows=nrows,
                header=header
            )
            return df
        elif self.extension in ['xls', 'xlsx']:
            if self.size > 10000000:  # 10 Mb
                raise Exception('File is to large')
            df = pd.read_excel(
                self.fp,
                sheet_name=self.sheet_name,
                header=header,
                skiprows=skiprows,
                nrows=nrows
            )
            return df
        else:
            raise Exception('Unsupported file .{}'.format(self.extension))

    @property
    def columns(self) -> List[Column]:
        if self.__columns:
            return self.__columns

        if self.size > 10000000 and self.extension in ['xls', 'xlsx']: # 10 Mb
            raise Exception('File is to large to load columns, provide it through constructor')

        df = self.load(skiprows=0, nrows=2, header=self.header_index)

        columns = []
        for index, col_name in enumerate(df.columns.values):
            col_type_name = str(df.dtypes[col_name]).lower()

            py_type = str
            if 'int' in col_type_name:
                py_type = int
            if 'float' in col_type_name:
                py_type = float

            columns.append(
                Column(
                    name=col_name if self.header_index is not None else 'Unnamed_{}'.format(str(index)),
                    index=index,
                    py_type=py_type
                )
            )
        self.__columns = columns
        return self.columns
