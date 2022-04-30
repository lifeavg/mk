import json
import pathlib
from datetime import datetime
from typing import Any

from mk import api
from mk import settings
from mk.models import LogNormal, Uniform, FixedDelay



def give_response(response: api.Response,
                  success_codes: tuple[int, ...]) -> tuple[Any | None, str | None]:
    err = None
    if response.status_code not in success_codes:
        err = f'Expected one of {success_codes} HTTP codes, got {response.status_code}'
    return response.data, err


def load_json_string(data: str) -> tuple[dict[str, Any], str | None]:
    err = None
    try:
        json_data: dict[str, Any] | float | int | list[Any] = json.loads(data)
        if isinstance(json_data, dict):
            return json_data, err
        err = 'Unsupported JSON format'
    except json.decoder.JSONDecodeError as exception:
        err = f'JSON decode error. {exception.msg}: line {exception.lineno} ' \
              f'column {exception.colno} (char {exception.pos})'
    return {}, err


def load_json_file(file: pathlib.Path) -> tuple[dict[str, Any], str | None]:
    err = None
    try:
        with file.open('rb') as fle:
            json_data: dict[str, Any] | float| int | list[Any] = json.load(fle)
            if isinstance(json_data, dict):
                return json_data, err
            err = f'Unsupported JSON format in {file}'
    except json.decoder.JSONDecodeError as exception:
        err = f'JSON decode error. {exception.msg}: line {exception.lineno} ' \
              f'column {exception.colno} (char {exception.pos}). File {file}'
    except FileNotFoundError as exception:
        err = f'{exception.errno} No such file {file}'
    return {}, err

def load_json_data(data: str) -> tuple[dict[str, Any], str | None]:
    data = str(data).strip()
    if pathlib.Path(data).is_file():
        return load_json_file(pathlib.Path(data))
    return load_json_string(data)


class Service:

    def __init__(self, cur_settings: settings.Settings) -> None:
        self.api = api.Service(cur_settings)

    def set_delay_fixed(self, delay: int) -> tuple[Any | None, str | None]:
        """
        Set fixed global delay.
        """
        return give_response(
            response=self.api.update_settings(FixedDelay(delay)),
            success_codes=(200, ))

    def set_delay_log_normal(self, median: int, sigma: float) -> tuple[Any | None, str | None]:
        """
        Set log normal global delay.
        """
        return give_response(
            response=self.api.update_settings(LogNormal(median, sigma)),
            success_codes=(200, ))

    def set_delay_uniform(self, lower: int, upper: int) -> tuple[Any | None, str | None]:
        """
        Set uniform global delay.
        """
        return give_response(
            response=self.api.update_settings(Uniform(lower, upper)),
            success_codes=(200, ))

    def reset(self) -> tuple[Any | None, str | None]:
        """
        Reset mappings to the default state and reset the request journal.
        """
        return give_response(
            response=self.api.reset(),
            success_codes=(200, ))

    def shutdown(self) -> tuple[Any | None, str | None]:
        """
        Shutdown the server.
        """
        return give_response(
            response=self.api.shutdown(),
            success_codes=(200, ))

class Mappings:

    def __init__(self, cur_settings: settings.Settings) -> None:
        self.api = api.Mappings(cur_settings)

    def get(self, limit: int | None = None,
            offset: int | None = None) -> tuple[dict[str, Any], str | None]:
        """
        Get all stub mappings.
        """
        return give_response(
            response=self.api.get(limit, offset),
            success_codes=(200, ))

    def create(self, mapping: str) -> tuple[dict[str, Any] | None, str | None]:
        """
        Create a new stub mapping.
        """
        data, err = load_json_data(mapping)
        if not err:
            return give_response(
                response=self.api.create(data),
                success_codes=(201, ))
        return None, err

    def delete(self) -> tuple[Any | None, str | None]:
        """
        Delete all stub mappings.
        """
        return give_response(
            response=self.api.delete(),
            success_codes=(200, ))

    def reset(self) -> tuple[Any | None, str | None]:
        """
        Restores stub mappings to the defaults defined back in the backing store.
        """
        return give_response(
            response=self.api.reset(),
            success_codes=(200, ))

    def persist(self) -> tuple[Any | None, str | None]:
        """
        Save all persistent stub mappings to the backing store.
        """
        return give_response(
            response=self.api.persist(),
            success_codes=(200, ))

    def find_by_metadata(self, metadata: str) -> tuple[dict[str, Any] | None, str | None]:
        """
        Find stubs by matching on their metadata.
        """
        data, err = load_json_data(metadata)
        if not err:
            return give_response(
                response=self.api.find_by_metadata(data),
                success_codes=(200, ))
        return None, err

    def delete_by_metadata(self, metadata: str) -> tuple[Any | None, str | None]:
        """
        Delete stub mappings matching metadata.
        """
        data, err = load_json_data(metadata)
        if not err:
            return give_response(
                response=self.api.delete_by_metadata(data),
                success_codes=(200, ))
        return None, err

    def get_by_id(self, mapping_id: str) -> tuple[Any | None, str | None]:
        """
        Get stub mapping by ID.
        """
        response = self.api.get_by_id(mapping_id)
        err = None
        if not response.error:
            if response.status_code == 404:
                err = f'No mapping with such id on service {response.url}'
            if response.status_code != 200:
                err = f'Unexpected response status code ' \
                      f'{response.status_code} {response.reason} from {response.url}'
        else:
            err = response.error
        return response.data, err

    def update_by_id(self, mapping_id: str, mapping: str) -> tuple[Any | None, str | None]:
        """
        Update a stub mapping.
        """
        data, err = load_json_data(mapping)
        if not err:
            response = self.api.update_by_id(mapping_id, data)
            if not response.error:
                if response.status_code == 404:
                    err = f'No mapping with such id on service {response.url}'
                if response.status_code != 200:
                    err = f'Unexpected response status code ' \
                        f'{response.status_code} {response.reason} from {response.url}'
            else:
                err = response.error
            return response.data, err
        return None, err

    def delete_by_id(self, mapping_id: str) -> tuple[Any | None, str | None]:
        """
        Delete a stub mapping.
        """
        return give_response(
            response=self.api.delete_by_id(mapping_id),
            success_codes=(200, ))

class Journal:

    def __init__(self, cur_settings: settings.Settings) -> None:
        self.api = api.Journal(cur_settings)

    def get_by_id(self, request_id: str) -> tuple[Any | None, str | None]:
        """
        Get request by ID.
        """
        response = self.api.get_by_id(request_id)
        err = None
        if not response.error:
            if response.status_code == 404:
                err = f'No request with such id in Journal service {response.url}'
            if response.status_code != 200:
                err = f'Unexpected response status code ' \
                      f'{response.status_code} {response.reason} from {response.url}'
        else:
            err = response.error
        return response.data, err

    def delete_by_id(self, request_id: str) -> tuple[Any | None, str | None]:
        """
        Delete request by ID.
        """
        return give_response(
            response=self.api.delete_by_id(request_id),
            success_codes=(200, ))

    def get_unmatched(self) -> tuple[dict[str, Any] | None, str | None]:
        """
        Get details of logged requests that weren't matched by any stub mapping.
        """
        return give_response(
            response=self.api.get_unmatched(),
            success_codes=(200,))

    def get_unmatched_near_misses(self) -> tuple[dict[str, Any] | None, str | None]:
        """
        Retrieve near-misses for all unmatched requests.
        """
        return give_response(
            response=self.api.get_unmatched_near_misses(),
            success_codes=(200,))

    def get(self, limit: int | None = None,
            since: datetime | None = None) -> tuple[dict[str, Any] | None, str | None]:
        """
        Get all requests in journal.
        """
        return give_response(
            response=self.api.get(limit, since),
            success_codes=(200,))

    def delete(self) -> tuple[Any | None, str | None]:
        """
        Delete all requests in journal.
        """
        return give_response(
            response=self.api.delete(),
            success_codes=(200,))

    def reset(self) -> tuple[Any | None, str | None]:
        """
        Empty the request journal.
        """
        return give_response(
            response=self.api.reset(),
            success_codes=(200,))

    def count_by_criteria(self, criteria: str) -> tuple[int | None, str | None]:
        """
        Count requests logged in the journal matching the specified criteria.
        """
        data, err = load_json_data(criteria)
        if not err:
            return give_response(
                response=self.api.count_by_criteria(data),
                success_codes=(200,))
        return None, err

    def delete_by_criteria(self, criteria: str) -> tuple[dict[str, Any] | None, str | None]:
        """
        Remove requests logged in the journal matching the specified criteria.
        """
        data, err = load_json_data(criteria)
        if not err:
            return give_response(
                response=self.api.delete_by_criteria(data),
                success_codes=(200,))
        return None, err

    def delete_by_metadata(self, metadata: str) -> tuple[dict[str, Any] | None, str | None]:
        """
        Delete requests mappings matching metadata.
        """
        data, err = load_json_data(metadata)
        if not err:
            return give_response(
                response=self.api.delete_by_metadata(data),
                success_codes=(200,))
        return None, err

    def find_by_criteria(self, criteria: str) -> tuple[dict[str, Any] | None, str | None]:
        """
        Retrieve details of requests logged in the journal matching the specified criteria.
        """
        data, err = load_json_data(criteria)
        if not err:
            return give_response(
                response=self.api.find_by_criteria(data),
                success_codes=(200,))
        return None, err

    def get_near_misses_by_request(self, request: str) -> tuple[dict[str, Any] | None, str | None]:
        """
        Find at most 3 near misses for closest stub mappings to the specified request.
        """
        data, err = load_json_data(request)
        if not err:
            return give_response(
                response=self.api.get_near_misses_by_request(data),
                success_codes=(200,))
        return None, err

    def get_near_misses_by_pattern(self, pattern: str) -> tuple[dict[str, Any] | None, str | None]:
        """
        Find at most 3 near misses for closest logged requests to the specified request pattern.
        """
        data, err = load_json_data(pattern)
        if not err:
            return give_response(
                response=self.api.get_near_misses_by_pattern(data),
                success_codes=(200,))
        return None, err


class Recordings:

    def __init__(self, cur_settings: settings.Settings) -> None:
        self.api = api.Recordings(cur_settings)

    def start(self, rec_settings: str) -> tuple[Any | None, str | None]:
        """
        Begin recording stub mappings.
        """
        data, err = load_json_data(rec_settings)
        if not err:
            return give_response(
                response=self.api.start(data),
                success_codes=(200,))
        return None, err

    def stop(self) -> tuple[dict[str, Any] | None, str | None]:
        """
        End recording of stub mappings.
        """
        return give_response(
            response=self.api.stop(),
            success_codes=(200,))

    def status(self) -> tuple[str | None, str | None]:
        """
        Get recording status.
        """
        return give_response(
            response=self.api.status(),
            success_codes=(200,))

    def snapshot(self, rec_settings: str) -> tuple[dict[str, Any] | None, str | None]:
        """
        Take a snapshot recording.
        """
        data, err = load_json_data(rec_settings)
        if not err:
            return give_response(
                response=self.api.snapshot(data),
                success_codes=(200,))
        return None, err


class Scenarios:

    def __init__(self, cur_settings: settings.Settings) -> None:
        self.api = api.Scenarios(cur_settings)

    def get(self) -> tuple[dict[str, Any] | None, str | None]:
        """
        Get all scenarios.
        """
        return give_response(
            response=self.api.get(),
            success_codes=(200,))

    def reset(self) -> tuple[Any | None, str | None]:
        """
        Reset the state of all scenarios.
        """
        return give_response(
            response=self.api.reset(),
            success_codes=(200,))


class Settings:

    def __init__(self, settings_file: pathlib.Path) -> None:
        self.file: pathlib.Path = settings_file
        self.current: settings.Settings
        self.autosave: bool = True

    def load(self) -> None | str:
        new_settings, err = settings.Settings.load(self.file)
        if err is None:
            self.current = new_settings
        return err

    def save(self) -> None | str:
        if self.current:
            return self.current.write(self.file)
        return 'No current settings found to save'

    def _autosaved(self) -> None | str:
        if self.autosave:
            return self.save()

    def generate(self, host: str,
                 api_request_timeout: int,
                 shutdown_disabled: bool) -> None | str:
        self.current = settings.Settings.generate(host, api_request_timeout, shutdown_disabled)
        return self._autosaved()

    def change_host(self, host: str) -> None | str:
        self.current = settings.Settings.generate(host, self.current.api_request_timeout,
                         self.current.shutdown_disabled)
        return self._autosaved()

    def change_api_request_timeout(self, timeout: int) -> None | str:
        self.current = settings.Settings.generate(self.current.host, timeout,
                         self.current.shutdown_disabled)
        return self._autosaved()

    def enable_shutdown(self) -> None | str:
        self.current = settings.Settings.generate(self.current.host,
                                                  self.current.api_request_timeout,
                                                  False)
        return self._autosaved()

    def disable_shutdown(self) -> None | str:
        self.current = settings.Settings.generate(self.current.host,
                                                  self.current.api_request_timeout,
                                                  True)
        return self._autosaved()

class App:

    def __init__(self, settings_file: pathlib.Path) -> None:
        self.settings: Settings = Settings(settings_file)
        self.service: Service
        self.mappings: Mappings
        self.journal: Journal
        self.recordings: Recordings
        self.scenarios: Scenarios

    def reset(self) -> None:
        self.service = Service(self.settings.current)
        self.mappings = Mappings(self.settings.current)
        self.journal = Journal(self.settings.current)
        self.recordings = Recordings(self.settings.current)
        self.scenarios = Scenarios(self.settings.current)

    def load(self) -> None | str:
        err = self.settings.load()
        if err is not None:
            return err
        self.reset()
