from typing import Any
import unittest
import pathlib
from json import load
from os import getcwd
from mk.handlers import Settings


class TestSettingsChangeAutosave(unittest.TestCase):
    
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.file = pathlib.Path(getcwd()).joinpath(
            pathlib.Path("test/resources/test_settings_autosave.json"))

    def write_file(self, data: str) -> None:
        with self.file.open('w', encoding='utf-8') as file:
            file.write(data)

    def tearDown(self) -> None:
        super().tearDown()
        self.file.unlink(missing_ok=True)

    def assertSetting(self, key: str, expected_value: Any) -> None:
        with self.file.open('rb') as file:
            data = load(file)
            self.assertEqual(data.get(key), expected_value)

    def test_change_host_enabled(self):
        self.write_file('{"host": "https://mock.io","api_request_timeout": 20,'
                        '"shutdown_disabled": true}')
        host = 'https://www.google.com'
        settings = Settings(self.file)
        settings.autosave = True
        settings.load()
        settings.change_host(host)
        self.assertEqual(settings.current.host, host)
        self.assertSetting('host', host)

    def test_change_host_disabled(self):
        self.write_file('{"host": "https://mock.io","api_request_timeout": 20,'
                        '"shutdown_disabled": true}')
        host = 'https://www.google.com'
        settings = Settings(self.file)
        settings.autosave = False
        settings.load()
        settings.change_host(host)
        self.assertEqual(settings.current.host, host)
        self.assertSetting('host', 'https://mock.io')

    def test_change_api_request_timeout_enabled(self):
        self.write_file('{"host": "https://mock.io","api_request_timeout": 20,'
                        '"shutdown_disabled": true}')
        api_request_timeout = 40
        settings = Settings(self.file)
        settings.autosave = True
        settings.load()
        settings.change_api_request_timeout(api_request_timeout)
        self.assertEqual(settings.current.api_request_timeout, api_request_timeout)
        self.assertSetting('api_request_timeout', api_request_timeout)

    def test_change_api_request_timeout_disabled(self):
        self.write_file('{"host": "https://mock.io","api_request_timeout": 20,'
                        '"shutdown_disabled": true}')
        api_request_timeout = 40
        settings = Settings(self.file)
        settings.autosave = False
        settings.load()
        settings.change_api_request_timeout(api_request_timeout)
        self.assertEqual(settings.current.api_request_timeout, api_request_timeout)
        self.assertSetting('api_request_timeout', 20)

    def test_enable_shutdown_enabled(self):
        self.write_file('{"host": "https://mock.io","api_request_timeout": 20,'
                        '"shutdown_disabled": true}')
        settings = Settings(self.file)
        settings.autosave = True
        settings.load()
        settings.enable_shutdown()
        self.assertFalse(settings.current.shutdown_disabled)
        self.assertSetting('shutdown_disabled', False)

    def test_enable_shutdown_disabled(self):
        self.write_file('{"host": "https://mock.io","api_request_timeout": 20,'
                        '"shutdown_disabled": true}')
        settings = Settings(self.file)
        settings.autosave = False
        settings.load()
        settings.enable_shutdown()
        self.assertFalse(settings.current.shutdown_disabled)
        self.assertSetting('shutdown_disabled', True)

    def test_disable_shutdown_enabled(self):
        self.write_file('{"host": "https://mock.io","api_request_timeout": 20,'
                        '"shutdown_disabled": false}')
        settings = Settings(self.file)
        settings.autosave = True
        settings.load()
        settings.disable_shutdown()
        self.assertTrue(settings.current.shutdown_disabled)
        self.assertSetting('shutdown_disabled', True)

    def test_disable_shutdown_disabled(self):
        self.write_file('{"host": "https://mock.io","api_request_timeout": 20,'
                        '"shutdown_disabled": false}')
        settings = Settings(self.file)
        settings.autosave = False
        settings.load()
        settings.disable_shutdown()
        self.assertTrue(settings.current.shutdown_disabled)
        self.assertSetting('shutdown_disabled', False)

    def test_generate_enabled(self):
        settings = Settings(self.file)
        settings.autosave = True
        host = 'https://www.google.com'
        api_request_timeout = 40
        shutdown_disabled = True
        settings.generate(host, api_request_timeout, shutdown_disabled)
        self.assertEqual(settings.current.host, host)
        settings.change_api_request_timeout(api_request_timeout)
        self.assertTrue(settings.current.shutdown_disabled)
        self.assertSetting('host', host)
        self.assertSetting('api_request_timeout', api_request_timeout)
        self.assertSetting('shutdown_disabled', True)

    def test_generate_disabled(self):
        settings = Settings(self.file)
        settings.autosave = False
        host = 'https://www.google.com'
        api_request_timeout = 40
        shutdown_disabled = True
        settings.generate(host, api_request_timeout, shutdown_disabled)
        self.assertEqual(settings.current.host, host)
        settings.change_api_request_timeout(api_request_timeout)
        self.assertTrue(settings.current.shutdown_disabled)
        self.assertFalse(self.file.exists())
