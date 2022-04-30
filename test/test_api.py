import unittest
from datetime import datetime, timezone

from mk import api
from mk.models import FixedDelay
from mk.settings import Settings


class BaseCase(unittest.TestCase):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.default_settings = Settings('https://31164062-5ac5-409f-87e4-534f58745d07.mock.pstmn.io',
                                         20, True)


class TestService(BaseCase):

    def test_update_settings(self):
        service = api.Service(self.default_settings)
        response: api.Response = service.update_settings(FixedDelay(500))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)

    def test_reset(self):
        service = api.Service(self.default_settings)
        response: api.Response = service.reset()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)

    def test_shutdown(self):
        service = api.Service(self.default_settings)
        response: api.Response = service.shutdown()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)


class TestMappings(BaseCase):

    def test_get(self):
        mappings = api.Mappings(self.default_settings)
        response: api.Response = mappings.get(10, 0)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_create(self):
        mappings = api.Mappings(self.default_settings)
        mapping = {
            "request": {
                "method": "GET",
                "url": "/some/thing"
            },
            "response": {
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                },
                "status": 200
            }
        }
        response: api.Response = mappings.create(mapping)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data)

    def test_delete(self):
        mappings = api.Mappings(self.default_settings)
        response: api.Response = mappings.delete()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)

    def test_reset(self):
        mappings = api.Mappings(self.default_settings)
        response: api.Response = mappings.reset()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)

    def test_persist(self):
        mappings = api.Mappings(self.default_settings)
        response: api.Response = mappings.persist()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)

    def test_find_by_metadata(self):
        mappings = api.Mappings(self.default_settings)
        metadata = {
            "matchesJsonPath": {
                "expression": "$.outer",
                "equalToJson": "{ \"inner\": 42 }"
            }
        }
        response: api.Response = mappings.find_by_metadata(metadata)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_delete_by_metadata(self):
        mappings = api.Mappings(self.default_settings)
        metadata = {
            "matchesJsonPath": {
                "expression": "$.outer",
                "equalToJson": "{ \"inner\": 42 }"
            }
        }
        response: api.Response = mappings.delete_by_metadata(metadata)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)

    def test_get_by_id(self):
        mappings = api.Mappings(self.default_settings)
        response: api.Response = mappings.get_by_id(
            "730d3e32-d098-4169-a20c-554c3bedce58")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_update_by_id(self):
        mappings = api.Mappings(self.default_settings)
        mapping = {
            "request": {
                "method": "GET",
                "url": "/some/thing"
            },
            "response": {
                "body": "Hello world!",
                "headers": {
                    "Content-Type": "text/plain"
                },
                "status": 200
            }
        }
        response: api.Response = mappings.update_by_id("730d3e32-d098-4169-a20c-554c3bedce58",
                                                       mapping)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_delete_by_id(self):
        mappings = api.Mappings(self.default_settings)
        response: api.Response = mappings.delete_by_id(
            "730d3e32-d098-4169-a20c-554c3bedce58")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)


class TestJournal(BaseCase):

    def test_get_by_id(self):
        journal = api.Journal(self.default_settings)
        response: api.Response = journal.get_by_id(
            "12fb14bb-600e-4bfa-bd8d-be7f12562c99")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_delete_by_id(self):
        journal = api.Journal(self.default_settings)
        response: api.Response = journal.delete_by_id(
            "12fb14bb-600e-4bfa-bd8d-be7f12562c99")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)

    def test_get_unmatched(self):
        journal = api.Journal(self.default_settings)
        response: api.Response = journal.get_unmatched()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_get_unmatched_near_misses(self):
        journal = api.Journal(self.default_settings)
        response: api.Response = journal.get_unmatched_near_misses()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_get(self):
        journal = api.Journal(self.default_settings)
        response: api.Response = journal.get(
            5, datetime(2016, 10, 5, 12, 33, 1, 0,  timezone.utc))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_delete(self):
        journal = api.Journal(self.default_settings)
        response: api.Response = journal.delete()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)

    def test_reset(self):
        journal = api.Journal(self.default_settings)
        response: api.Response = journal.reset()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)

    def test_count_by_criteria(self):
        journal = api.Journal(self.default_settings)
        criteria = {
            "method": "POST",
            "url": "/resource",
            "headers": {
                "Content-Type": {
                    "matches": ".*/xml"
                }
            }
        }
        response: api.Response = journal.count_by_criteria(criteria)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_delete_by_criteria(self):
        journal = api.Journal(self.default_settings)
        criteria = {
            "method": "POST",
            "url": "/resource",
            "headers": {
                "Content-Type": {
                    "matches": ".*/xml"
                }
            }
        }
        response: api.Response = journal.delete_by_criteria(criteria)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_delete_by_metedata(self):
        journal = api.Journal(self.default_settings)
        metadata = {
            "matchesJsonPath": {
                "expression": "$.outer",
                "equalToJson": "{ \"inner\": 42 }"
            }
        }
        response: api.Response = journal.delete_by_metadata(metadata)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_find_by_criteria(self):
        journal = api.Journal(self.default_settings)
        criteria = {
            "method": "POST",
            "url": "/resource",
            "headers": {
                "Content-Type": {
                    "matches": ".*/xml"
                }
            }
        }
        response: api.Response = journal.find_by_criteria(criteria)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_get_near_misses_by_request(self):
        journal = api.Journal(self.default_settings)
        request = {
            "url": "/actual",
            "absoluteUrl": "http://localhost:8080/actual",
            "method": "GET",
            "clientIp": "0:0:0:0:0:0:0:1",
            "headers": {
                "User-Agent": "curl/7.30.0",
                "Accept": "*/*",
                "Host": "localhost:8080"
            },
            "cookies": {},
            "browserProxyRequest": False,
            "loggedDate": 1467402464520,
            "bodyAsBase64": "",
            "body": "",
            "loggedDateString": "2016-07-01T19:47:44Z"
        }
        response: api.Response = journal.get_near_misses_by_request(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_get_near_misses_by_pattern(self):
        journal = api.Journal(self.default_settings)
        pattern = {
            "method": "POST",
            "url": "/resource",
            "headers": {
                "Content-Type": {
                    "matches": ".*/xml"
                }
            }
        }
        response: api.Response = journal.get_near_misses_by_pattern(pattern)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)


class TestRecordings(BaseCase):

    def test_start(self):
        recordings = api.Recordings(self.default_settings)
        settings = {
            "targetBaseUrl": "http://example.mocklab.io",
            "filters": {
                "urlPathPattern": "/api/.*",
                "method": "GET"
            },
            "captureHeaders": {
                "Accept": {},
                "Content-Type": {
                    "caseInsensitive": True
                }
            },
            "requestBodyPattern": {
                "matcher": "equalToJson",
                "ignoreArrayOrder": False,
                "ignoreExtraElements": True
            },
            "extractBodyCriteria": {
                "textSizeThreshold": "2048",
                "binarySizeThreshold": "10240"
            },
            "persist": False,
            "repeatsAsScenarios": False,
            "transformers": [
                "modify-response-header"
            ],
            "transformerParameters": {
                "headerValue": "123"
            }
        }
        response: api.Response = recordings.start(settings)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)

    def test_stop(self):
        recordings = api.Recordings(self.default_settings)
        response: api.Response = recordings.stop()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_status(self):
        recordings = api.Recordings(self.default_settings)
        response: api.Response = recordings.status()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_snapshot(self):
        recordings = api.Recordings(self.default_settings)
        settings = {
            "targetBaseUrl": "http://example.mocklab.io",
            "filters": {
                "urlPathPattern": "/api/.*",
                "method": "GET"
            },
            "captureHeaders": {
                "Accept": {},
                "Content-Type": {
                    "caseInsensitive": True
                }
            },
            "requestBodyPattern": {
                "matcher": "equalToJson",
                "ignoreArrayOrder": False,
                "ignoreExtraElements": True
            },
            "extractBodyCriteria": {
                "textSizeThreshold": "2048",
                "binarySizeThreshold": "10240"
            },
            "persist": False,
            "repeatsAsScenarios": False,
            "transformers": [
                "modify-response-header"
            ],
            "transformerParameters": {
                "headerValue": "123"
            }
        }
        response: api.Response = recordings.snapshot(settings)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)


class TestScenarios(BaseCase):

    def test_get(self):
        scenarios = api.Scenarios(self.default_settings)
        response: api.Response = scenarios.get()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_reset(self):
        scenarios = api.Scenarios(self.default_settings)
        response: api.Response = scenarios.reset()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data)
