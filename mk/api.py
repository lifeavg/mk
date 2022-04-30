from __future__ import annotations
import datetime
from typing import Any, Callable
from dataclasses import dataclass

import requests

from mk.settings import Settings
from mk.models import LogNormal, Uniform, FixedDelay


@dataclass
class Response:
    status_code: int = 0
    reason: str = ''
    url: str | None = ''
    data: Any = None
    error: str | None = None

    @staticmethod
    def process_response(request: Callable[...,requests.Response], **kwargs: Any) -> Response:
        result = Response()
        try:
            response = request(**kwargs)
            result.status_code = response.status_code
            result.reason = response.reason
            result.url = response.request.url
            if response.content:
                result.data = response.json()
            return result
        except requests.ConnectTimeout: #  as exception:
            result.error = 'The request timed out while trying to connect to the remote server.'
            return result
        except requests.ReadTimeout: # as exception:
            result.error = 'The server did not send any data in the allotted amount of time.'
            return result
        except requests.Timeout: # as exception:
            result.error = 'The request timed out.'
            return result
        except requests.TooManyRedirects: # as exception:
            result.error = 'Too many redirects.'
            return result
        except requests.URLRequired: # as exception:
            result.error = 'A valid URL is required to make a request.'
            return result
        except requests.HTTPError: # as exception:
            result.error = 'An HTTP error occurred.'
            return result
        except requests.ConnectionError: # as exception:
            result.error = 'A Connection error occurred.'
            return result
        except requests.RequestException: # as exception:
            result.error = 'There was an ambiguous exception that occurred while handling your request.'
            return result


class ApiBase:

    def __init__(self, settings: Settings) -> None:
        self._settings: Settings = settings
        self._base_url: str = '/__admin'

    def base_url(self) -> str:
        return self._settings.host + self._base_url


class Service(ApiBase):

    def update_settings(self, settings: LogNormal | Uniform | FixedDelay) -> Response:
        """
        Update global settings
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/settings',
                          json=settings.to_dict(),
                          timeout=self._settings.api_request_timeout)

    def reset(self) -> Response:
        """
        Reset mappings to the default state and reset the request journal
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/reset',
                          timeout=self._settings.api_request_timeout)

    def shutdown(self) -> Response:
        """
        Shutdown the Mock server
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/shutdown',
                          timeout=self._settings.api_request_timeout)


class Mappings(ApiBase):

    def get(self, limit: int | None = None, offset: int | None = None) -> Response:
        """
        Get all stub mappings
        """
        # 200 OK
        return Response.process_response(
            requests.get, url=self.base_url() + '/mappings',
                         params={'limit': limit, 'offset': offset},
                         timeout=self._settings.api_request_timeout)

    def create(self, mapping: dict[str, Any]) -> Response:
        """
        Create a new stub mapping
        """
        # 201 Created
        return Response.process_response(
            requests.post, url=self.base_url() + '/mappings',
                          json=mapping,
                          timeout=self._settings.api_request_timeout)

    def delete(self) -> Response:
        """
        Delete all stub mappings
        """
        # 200 OK
        return Response.process_response(
            requests.delete, url=self.base_url() + '/mappings',
                            timeout=self._settings.api_request_timeout)

    def reset(self) -> Response:
        """
        Restores stub mappings to the defaults defined back in the backing store
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/mappings/reset',
                          timeout=self._settings.api_request_timeout)

    def persist(self) -> Response:
        """
        Save all persistent stub mappings to the backing store
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/mappings/save',
                          timeout=self._settings.api_request_timeout)

    def find_by_metadata(self, metadata: dict[str, Any]) -> Response:
        """
        Find stubs by matching on their metadata
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/mappings/find-by-metadata',
                          json=metadata,
                          timeout=self._settings.api_request_timeout)

    def delete_by_metadata(self, metadata: dict[str, Any]) -> Response:
        """
        Delete stub mappings matching metadata
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/mappings/remove-by-metadata',
                          json=metadata,
                          timeout=self._settings.api_request_timeout)

    def get_by_id(self, mapping_id: str) -> Response:
        """
        Get stub mapping by ID
        """
        # 200 OK
        # 404 Not Found
        return Response.process_response(
            requests.get, url=self.base_url() + '/mappings/' + mapping_id,
                         timeout=self._settings.api_request_timeout)

    def update_by_id(self, mapping_id: str, mapping: dict[str, Any]) -> Response:
        """
        Update a stub mapping
        """
        # 200 OK
        # 404 Not Found
        return Response.process_response(
            requests.put, url=self.base_url() + '/mappings/' + mapping_id,
                         json=mapping,
                         timeout=self._settings.api_request_timeout)

    def delete_by_id(self, mapping_id: str) -> Response:
        """
        Delete a stub mapping
        """
        # 200 OK
        # 404 Not Found
        return Response.process_response(
            requests.delete, url=self.base_url() + '/mappings/' + mapping_id,
                            timeout=self._settings.api_request_timeout)


class Journal(ApiBase):

    def get_by_id(self, request_id: str) -> Response:
        """
        Get request by ID
        """
        # 200 OK
        # 404 Not Found
        return Response.process_response(
            requests.get, url=self.base_url() + '/requests/' + request_id,
                         timeout=self._settings.api_request_timeout)

    def delete_by_id(self, request_id: str) -> Response:
        """
        Delete request by ID
        """
        # 200 OK
        return Response.process_response(
            requests.delete, url=self.base_url() + '/requests/' + request_id,
                            timeout=self._settings.api_request_timeout)

    def get_unmatched(self) -> Response:
        """
        Get details of logged requests that weren't matched by any stub mapping
        """
        # 200 OK
        return Response.process_response(
            requests.get, url=self.base_url() + '/requests/unmatched',
                         timeout=self._settings.api_request_timeout)

    def get_unmatched_near_misses(self) -> Response:
        """
        Retrieve near-misses for all unmatched requests
        """
        # 200 OK
        return Response.process_response(
            requests.get, url=self.base_url() + '/requests/unmatched/near-misses',
                         timeout=self._settings.api_request_timeout)

    def get(self, limit: int | None = None, since: datetime.datetime | None = None) -> Response:
        """
        Get all requests in journal
        """
        # 200 OK
        return Response.process_response(
            requests.get, url=self.base_url() + '/requests',
                         params={'limit': limit, 'since': since},
                         timeout=self._settings.api_request_timeout)

    def delete(self) -> Response:
        """
        Delete all requests in journal
        """
        # 200 OK
        return Response.process_response(
            requests.delete, url=self.base_url() + '/requests',
                            timeout=self._settings.api_request_timeout)

    def reset(self) -> Response:
        """
        Empty the request journal
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/requests/reset',
                          timeout=self._settings.api_request_timeout)

    def count_by_criteria(self, criteria: dict[str, Any]) -> Response:
        """
        Count requests logged in the journal matching the specified criteria
        """
        # 200 OK
        result: Response = Response.process_response(requests.post,
                                                     url=self.base_url() + '/requests/count',
                                                    json=criteria,
                                                    timeout=self._settings.api_request_timeout)
        if result.status_code == 200:
            result.data = int(result.data.get('count'))
        return result

    def delete_by_criteria(self, criteria: dict[str, Any]) -> Response:
        """
        Remove requests logged in the journal matching the specified criteria
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/requests/remove',
                          json=criteria,
                          timeout=self._settings.api_request_timeout)

    def delete_by_metadata(self, metadata: dict[str, Any]) -> Response:
        """
        Delete requests mappings matching metadata
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/requests/remove-by-metadata',
                          json=metadata,
                          timeout=self._settings.api_request_timeout)

    def find_by_criteria(self, criteria: dict[str, Any]) -> Response:
        """
        Retrieve details of requests logged in the journal matching the specified criteria
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/requests/find',
                          json=criteria,
                          timeout=self._settings.api_request_timeout)

    def get_near_misses_by_request(self, request: dict[str, Any]) -> Response:
        """
        Find at most 3 near misses for closest stub mappings to the specified request
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/near-misses/request',
                          json=request,
                          timeout=self._settings.api_request_timeout)

    def get_near_misses_by_pattern(self, pattern: dict[str, Any]) -> Response:
        """
        Find at most 3 near misses for closest logged requests to the specified request pattern
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/near-misses/request-pattern',
                          json=pattern,
                          timeout=self._settings.api_request_timeout)


class Recordings(ApiBase):

    def start(self, settings: dict[str, Any]) -> Response:
        """
        Begin recording stub mappings
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/recordings/start',
                          json=settings,
                          timeout=self._settings.api_request_timeout)

    def stop(self) -> Response:
        """
        End recording of stub mappings
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/recordings/stop',
                          timeout=self._settings.api_request_timeout)

    def status(self) -> Response:
        """
        Get recording status
        """
        # 200 OK
        result: Response = Response.process_response(requests.get, 
                                                     url=self.base_url() + '/recordings/status',
                                                     timeout=self._settings.api_request_timeout)
        if result.status_code == 200:
            result.data = result.data.get('status')
        return result

    def snapshot(self, settings: dict[str, Any]) -> Response:
        """
        Take a snapshot recording
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/recordings/snapshot',
                          json=settings,
                          timeout=self._settings.api_request_timeout)


class Scenarios(ApiBase):

    def get(self) -> Response:
        """
        Get all scenarios
        """
        # 200 OK
        return Response.process_response(
            requests.get, url=self.base_url() + '/scenarios',
                         timeout=self._settings.api_request_timeout)

    def reset(self) -> Response:
        """
        Reset the state of all scenarios
        """
        # 200 OK
        return Response.process_response(
            requests.post, url=self.base_url() + '/scenarios/reset',
                          timeout=self._settings.api_request_timeout)
