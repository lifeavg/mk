import pathlib
import unittest
from os import getcwd

from mk.api import Response
from mk.handlers import (give_response, load_json_data, load_json_file,
                         load_json_string)


class TestGiveResponse(unittest.TestCase):

    def test_give_response_no_data(self):
        response = Response(200, 'OK', 'https://www.google.com/')
        data, err = give_response(response, (200, ))
        self.assertIsNone(data)
        self.assertIsNone(err)

    def test_give_response_data(self):
        response = Response(200, 'OK', 'https://www.google.com/', "test_data")
        data, err = give_response(response, (200, ))
        self.assertEqual(data, "test_data")
        self.assertIsNone(err)

    def test_give_response_error_code(self):
        response = Response(200, 'OK', 'https://www.google.com/', "test_data")
        data, err = give_response(response, (201, ))
        self.assertEqual(data, "test_data")
        self.assertEqual(err, 'Expected one of (201,) HTTP codes, got 200')


class TestLoadJSONFile(unittest.TestCase):

    def test_load_json_file(self):
        file = pathlib.Path(getcwd()).joinpath(
            pathlib.Path("test/resources/test_load_json_file.json"))
        data, err = load_json_file(file)
        self.assertEqual(data, {"test": "data"})
        self.assertIsNone(err)

    def test_load_json_file_int(self):
        file = pathlib.Path(getcwd()).joinpath(
            pathlib.Path("test/resources/test_load_json_file_int.json"))
        data, err = load_json_file(file)
        self.assertEqual(data, {})
        self.assertEqual(err, f'Unsupported JSON format in {file}')
            

    def test_load_json_file_list(self):
        file = pathlib.Path(getcwd()).joinpath(
            pathlib.Path("test/resources/test_load_json_file_list.json"))
        data, err = load_json_file(file)
        self.assertEqual(data, {})
        self.assertEqual(err, f'Unsupported JSON format in {file}')


class TestLoadJSONString(unittest.TestCase):

    def test_load_json_string(self):
        json_string = '{"test":"data"}'
        data, err = load_json_string(json_string)
        self.assertEqual(data, {"test": "data"})
        self.assertIsNone(err)

    def test_load_json_string_int(self):
        json_string = '12345'
        data, err = load_json_string(json_string)
        self.assertEqual(data, {})
        self.assertEqual(err, 'Unsupported JSON format')


    def test_load_json_string_list(self):
        json_string = '[{"test":"data_one"},{"test":"data_two"}]'
        data, err = load_json_string(json_string)
        self.assertEqual(data, {})
        self.assertEqual(err, 'Unsupported JSON format')


class TestLoadJSONData(unittest.TestCase):

    def test_load_json_data_string(self):
        json_string = '     {"test":"data"}      '
        data, err = load_json_data(json_string)
        self.assertEqual(data, {"test": "data"})
        self.assertIsNone(err)

    def test_load_json_data_file(self):
        file = pathlib.Path(getcwd()).joinpath(
            pathlib.Path("test/resources/test_load_json_file.json"))
        data, err = load_json_data(str(file))
        self.assertEqual(data, {"test": "data"})
        self.assertIsNone(err)

    def test_load_json_data_not_json(self):
        file = pathlib.Path(getcwd()).joinpath(
            pathlib.Path("test/temp/no_file.json"))
        data, err = load_json_data(str(file))
        self.assertEqual(data, {})
        self.assertIsInstance(err, str)
        self.assertEqual(str(err)[:19], 'JSON decode error. ')
