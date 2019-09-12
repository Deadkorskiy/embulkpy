class EmbulkPlugin(object):

    class PluginType:
        IN = 'in'
        OUT = 'out'

    def __init__(self, plugin_type: str, plugin_name: str, *args, **kwargs):
        self.plugin_type = plugin_type
        self.plugin_name = plugin_name
        self._args = args
        self._kwargs = kwargs

    @property
    def config(self) -> str:
        raise NotImplementedError()