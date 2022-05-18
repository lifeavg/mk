from __future__ import annotations
import pathlib
import json
from typing import Any
from dataclasses import asdict, dataclass


def get_config_path(platform: str) -> tuple[pathlib.Path, str | None]:
    return (pathlib.Path(__file__).parent.joinpath(pathlib.Path("settings.json")), None)


@dataclass(frozen=True)
class Settings:
    host: str = ''
    api_request_timeout: int = 0
    shutdown_disabled: bool = False

    @staticmethod
    def load(settings_file: pathlib.Path) -> tuple[Settings, str | None]:
        err = None
        new_settings = Settings()
        try:
            with settings_file.open('rb') as settings:
                json_settings: dict[str, Any] = json.load(settings)
                new_settings = Settings.generate(**json_settings)
                if not new_settings.host:
                    err = f'Default host not set in {settings_file}'
                if not new_settings.api_request_timeout:
                    err = f'api_request_timeout not set in {settings_file}'
                if new_settings.shutdown_disabled is None:
                    err = f'shutdown_disabled not set in {settings_file}'
        except json.JSONDecodeError as exception:
            err = f'JSON decode error. {exception.msg}: line {exception.lineno} ' \
                f'column {exception.colno} (char {exception.pos}). File {settings_file}'
        except FileNotFoundError as exception:
            err = f'{exception.errno} No such file {settings_file}'
        except IsADirectoryError as exception:
            err = f'{exception.errno} {settings_file} is a directory'
        except PermissionError as exception:
            err = f'{exception.errno} Unable to read, permission denied {settings_file}'
        except BlockingIOError  as exception:
            err = f'{exception.errno} Unable to read, file in use by another app {settings_file}'
        return new_settings, err

    def write(self, settings_file: pathlib.Path) -> None | str:
        err = None
        try:
            with settings_file.open('w', encoding='utf-8') as settings:
                settings.writelines(json.dumps(asdict(self), indent=4))
                return err
        except IsADirectoryError as exception:
            err = f'{exception.errno} {settings_file} is a directory'
        except PermissionError as exception:
            err = f'{exception.errno} Unable to write, permission denied {settings_file}'
        except BlockingIOError  as exception:
            err = f'{exception.errno} Unable to write, file in use by another app {settings_file}'
        return err

    @staticmethod
    def generate(host: str,
                 api_request_timeout: int,
                 shutdown_disabled: bool) -> Settings:
        return Settings(host=host,
                        api_request_timeout=api_request_timeout,
                        shutdown_disabled=shutdown_disabled)
