import os
import subprocess
import uuid
import logging
from .plugin import EmbulkPlugin


class Embulk(object):
    # https://github.com/embulk/embulk

    def __init__(
            self,
            embulk_path: str = 'embulk',
            config_dir: str = None,
            JAVA_HOME: str = None,
            ensure_plugin_installed: bool = False
    ):
        self.embulk_path = embulk_path
        self.JAVA_HOME = JAVA_HOME
        self.ensure_plugin_installed = ensure_plugin_installed
        self.config_dir = config_dir if config_dir else os.path.join(os.path.dirname(__file__), 'configs')

    def exec(
            self,
            in_plug: EmbulkPlugin,
            out_plug: EmbulkPlugin,
            config_name: str = None,
            timeout: int = None,
            remove_config: bool = True
    ) -> None:
        config_fp = config_name or str(uuid.uuid4())
        config_fp = config_fp.lower().replace('.yml', '') + '.yml'
        config_fp = os.path.join(self.config_dir, config_fp)

        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)

        if self.ensure_plugin_installed:
            self.__insure_plugin_installed(in_plug)
            self.__insure_plugin_installed(out_plug)

        try:
            config = ''.join([in_plug.config, out_plug.config])
            with open(config_fp, 'wt') as f:
                f.write(config)

            cmd = '{} {} {} {}'.format(
                'JAVA_HOME="{}"'.format(self.JAVA_HOME) if self.JAVA_HOME else '',
                self.embulk_path,
                'run',
                config_fp
            )
            self.__shell(cmd, timeout=timeout)
        except Exception:
            raise
        finally:
            if os.path.isfile(config_fp) and remove_config:
                os.remove(config_fp)

    def __insure_plugin_installed(self, plugin: EmbulkPlugin) -> None:
        cmd = '{} {} {}'.format(
            'JAVA_HOME="{}"'.format(self.JAVA_HOME) if self.JAVA_HOME else '',
            self.embulk_path,
            'gem list'
        )
        installed_plugins = self.__shell(cmd)
        if plugin.plugin_name not in installed_plugins:
            cmd = '{} {} {} {}'.format(
                'JAVA_HOME="{}"'.format(self.JAVA_HOME) if self.JAVA_HOME else '',
                self.embulk_path,
                'gem install',
                plugin.plugin_name
            )
            self.__shell(cmd)

    def __shell(self, cmd: str, timeout: int = None) -> str:
        p = subprocess.Popen(
            ["sh"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=0)

        logging.debug('PID: {}, CMD: {}'.format(str(p.pid), str(cmd)))

        stdout, stderr = p.communicate(cmd, timeout)

        logging.debug('PID: {}, CMD: {}, RETURN CODE: {}, STDOUT: {}, STDERR: {}'.format(
            str(p.pid), str(cmd), str(p.returncode), str(stdout), str(stderr))
        )

        if stderr:
            raise Exception('shell return stderr: {}'.format(str(stderr)))
        if p.returncode != 0:
            raise Exception('shell return code is not 0: {}'.format(str(p.returncode)))
        p.kill()
        return stdout
