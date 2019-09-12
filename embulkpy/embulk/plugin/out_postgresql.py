from . import EmbulkPlugin
import yaml


class PostgreSQLInEmbulkPlugin(EmbulkPlugin):
    # https://github.com/embulk/embulk-output-jdbc/tree/master/embulk-output-postgresql

    # Some times you may need to create role and test database:
    # CREATE ROLE pg  WITH SUPERUSER CREATEDB CREATEROLE LOGIN;
    # CREATE DATABASE test;

    class Mode(object):
        INSERT = 'insert'
        INSERT_DIRECT = 'insert_direct'
        TRUNCATE_INSERT = 'truncate_insert'
        REPLACE = 'replace'
        MERGE = 'merge'
        MERGE_DIRECT = 'merge_direct'

    def __init__(
            self,
            host: str,
            user: str,
            password: str,
            database: str,
            table: str,
            port: int = 5432,
            mode: str = Mode.INSERT,
            schema: str = 'public',
            *args, **kwargs):

        super().__init__(self.PluginType.OUT, 'embulk-output-postgresql', *args, **kwargs)
        self.type = 'postgresql'
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.table = table
        self.schema = schema
        self.port = port
        self.mode = mode

    @property
    def config(self) -> str:
        config = {
            self.plugin_type: {
                'type': self.type,
                'host': self.host,
                'user': self.user,
                'port': self.port,
                'password': self.password,
                'database': self.database,
                'table': self.table,
                'schema': self.schema,
                'mode': self.mode
            }
        }
        return yaml.dump(config)

