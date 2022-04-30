import pathlib
import unittest
import json
import os

from mk import settings



class TestSettings(unittest.TestCase):

    def test_load(self):
        settings_test, err = settings.Settings.load(pathlib.Path(os.getcwd()).joinpath(
            pathlib.Path("test/resources/test_load_settings.json")))
        self.assertIsNone(err)
        self.assertEqual(settings_test.host, "https://mock.io")
        self.assertEqual(settings_test.api_request_timeout, 20)
        self.assertTrue(settings_test.shutdown_disabled)


class TestSettingsWrite(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.settings_test = settings.Settings("host", 15, False)
        self.file = pathlib.Path(os.getcwd()).joinpath(
            pathlib.Path("test/temp/test_write_settings.json"))

    def test_write(self):
        err = self.settings_test.write(self.file)
        self.assertIsNone(err)
        with self.file.open('rb') as file:
            settings_json = json.load(file)
            self.assertEqual(self.settings_test.host,
                             settings_json['host'])
            self.assertEqual(self.settings_test.api_request_timeout,
                             settings_json['api_request_timeout'])
            self.assertEqual(self.settings_test.shutdown_disabled,
                             settings_json['shutdown_disabled'])

    def tearDown(self):
        self.file.unlink(missing_ok=True)
