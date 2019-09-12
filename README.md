# embulkpy

Python wrapper for embulk


Usage example:
```python
from embulkpy.embulk import Embulk 
from embulkpy.tbl_file_util import TblFileUtil
from embulkpy.embulk.plugin import CSVInEmbulkPlugin, PostgreSQLInEmbulkPlugin


embulk = Embulk(
    embulk_path='/home/deadkorskiy/.embulk/bin/embulk',
    JAVA_HOME='/usr/lib/jvm/java-8-openjdk-amd64/jre/'
)

in_plugin = CSVInEmbulkPlugin.build(
    TblFileUtil(
        'file/path.csv',
        header_index=0
    )
)

out_plugin = PostgreSQLInEmbulkPlugin(
    host='127.0.0.1',
    user='postgres',
    password='postgres',
    database='postgres',
    table='my_table'
)

embulk.exec(in_plugin, out_plugin, 'config_name', timeout=60, remove_config=True)

```