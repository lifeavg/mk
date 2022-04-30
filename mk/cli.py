import argparse
from datetime import datetime
import pathlib
from typing import Any, Callable
import json

from mk import handlers


def print_if_resp(data: Any | None, err: str | None) -> None:
    if err is not None:
        print(err)
    match data:
        case dict():
            print(json.dumps(data, indent=4))
        case None:
            pass
        case _:
            print(data)



def iterate_request(function: Callable[...,tuple[Any | None, str | None]],
                    args: Any) -> tuple[Any | None, str | None]:
    result_data = ""
    result_err = ""
    for request_id in args:
        data, err = function(request_id)
        if data is not None:
            result_data += json.dumps(data, indent=4) + '\n'
        if err is not None:
            result_err += f'{request_id}: {err}\n'
    return result_data, None if not result_err else result_err


class Cli(handlers.App):

    def __init__(self, settings_file: pathlib.Path) -> None:
        super().__init__(settings_file)
        self.arguments = argparse.ArgumentParser(
            prog='wmk',
            description='Mock API handler.')

        subparsers = self.arguments.add_subparsers(
            dest='command', required=True)

        service_subparser = subparsers.add_parser(
            'service', help='Global operations.')
        service = service_subparser.add_mutually_exclusive_group(required=True)
        service.add_argument('-delay', metavar='NUM', nargs='+',
                             help="Set global delay. INT -> fixed; "
                             "INT INT -> uniform; INT FLOAT -> log normal.")
        service.add_argument('-reset', action='store_true',
                             help="Reset mappings to the default state and "
                             "reset the request journal.")
        service.add_argument('-stop', action='store_true',
                             help="Shutdown the server. Disabled in config"
                             " by default in safety purposes.")

        mapping_subparser = subparsers.add_parser(
            'mapping', help='Operations on stub mappings.')
        mapping = mapping_subparser.add_mutually_exclusive_group(required=True)
        mapping.add_argument('-get', metavar='ARG', nargs='*',
                             help="Get mappings list. "
                             "No arguments -> get all mappings. "
                             "INT INT -> get Limit Offset list from all mappings. "
                             "[ID...] -> by id.")
        mapping.add_argument('-get-meta', metavar='METADATA', nargs=1, type=str,
                             help="Get mappings list matching metadata. "
                             "FILE -> from JSON from file. "
                             "STR -> from JSON string. ")
        mapping.add_argument('-create', metavar='MAPPING', type=str, nargs=1,
                             help="Create mapping from JSON string or file.")
        mapping.add_argument('-delete', metavar='ID', type=str, nargs='*',
                             help="Delete mappings. "
                             "No arguments -> all mappings. "
                             "[ID...] -> by id.")
        mapping.add_argument('-delete-meta', metavar='CRITERIA', type=str, nargs=1,
                             help="Delete mappings matching metadata. "
                             "FILE -> from JSON file. "
                             "STR -> from JSON string.")
        mapping.add_argument('-reset', action='store_true',
                             help="Reset stub mappings (without reseting journal).")
        mapping.add_argument('-persist', action='store_true',
                             help="Save all persistent stub mappings to the backing store.")
        mapping.add_argument('-update', metavar='ARG', type=str, nargs=2,
                             help="Update mapping by id from JSON: "
                             "ID FILE(MAPPING); ID STR(MAPPING)")

        journal_subparser = subparsers.add_parser(
            'journal', help="Logged requests and responses received by the mock service.")
        journal = journal_subparser.add_mutually_exclusive_group(required=True)
        journal.add_argument('-get', metavar='ARG', nargs='*',
                             help="Get requests from journal. "
                             "[ID...] -> by id. "
                             "INT DATE -> get Limit requests starting from Date. "
                             "No arguments -> all requests.")
        journal.add_argument('-get-critaria', metavar='CRITARIA', nargs=1, type=str,
                             help="Get requests from journal. "
                             "FILE -> JSON from file. "
                             "STR -> JSON from string.")
        journal.add_argument('-delete', metavar='ARG', nargs='*',
                             help="Delete request from journal. "
                             "[ID...] -> matching id. "
                             "No arguments -> all requests.")
        journal.add_argument('-delete-critaria', metavar='CRITARIA', nargs=1, type=str,
                             help="Delete request from journal matching critaria. "
                             "FILE -> JSON from file. "
                             "STR -> JSON from string.")
        journal.add_argument('-delete-metadata', metavar='METADATA', nargs=1, type=str,
                             help="Delete request from journal matching metadata. "
                             "FILE -> JSON from file. "
                             "STR -> JSON from string.")
        journal.add_argument('-unmatched', action='store_true',
                             help="Get details of logged requests that weren't "
                             "matched by any stub mapping.")
        journal.add_argument('-miss', action='store_true',
                             help="Get near-misses for all unmatched requests.")
        journal.add_argument('-miss-request', metavar='REQUEST', nargs=1, type=str,
                             help="Get near-misses for unmatched requests by request. "
                             "STR -> matching JSON string. "
                             "FILE -> mathing JSON file.")
        journal.add_argument('-miss-pattern', metavar='PATTERN', nargs=1, type=str,
                             help="Get near-misses for unmatched requests by pattern. "
                             "STR -> matching JSON string. "
                             "FILE -> mathing JSON file.")
        journal.add_argument('-reset', action='store_true',
                             help="Reset (empty) request journal.")
        journal.add_argument('-count', metavar='CRITARIA', nargs=1, type=str,
                             help="Count requests in journal matching critaria from "
                             "JSON: FILE or STR.")

        recordings_subparser = subparsers.add_parser(
            'record', help="Stub mapping record and snapshot functions.")
        recordings = recordings_subparser.add_mutually_exclusive_group(
            required=True)
        recordings.add_argument('-start', metavar='SETTINGS', nargs=1, type=str,
                                help="Begin recording stub mappings with "
                                "settings from JSON: FILE or STR.")
        recordings.add_argument('-stop', action='store_true',
                                help="End recording of stub mappings.")
        recordings.add_argument('-status', action='store_true',
                                help="Get recording status.")
        recordings.add_argument('-snapshot', metavar='SETTINGS', nargs=1, type=str,
                                help="Take a snapshot recording with "
                                "settings from JSON: FILE or STR.")

        scenarios_subparser = subparsers.add_parser(
            'scenario', help="Scenarios support modelling of stateful behavior.")
        scenarios = scenarios_subparser.add_mutually_exclusive_group(
            required=True)
        scenarios.add_argument('-get', action='store_true',
                               help="Get all scenarios.")
        scenarios.add_argument('-reset', action='store_true',
                               help="Reset the state of all scenarios.")

        settings_subparser = subparsers.add_parser(
            'settings', help="App settings and configuration.")
        settings = settings_subparser.add_mutually_exclusive_group(
            required=True)
        settings.add_argument('-gen', metavar='S', nargs=3,
                              help="Generate new settings as HOST, TIMEOUT, SHUTDOWN.")
        settings.add_argument('-host', metavar='HOST',
                              nargs=1, type=str, help="Set new host.")
        settings.add_argument('-timeout', metavar='TIMEOUT', nargs=1,
                              type=int, help="Set max API request timeout in seconds.")
        settings.add_argument('-shutdown-enable', action='store_true',
                              help="Allow to shutdown service by request.")
        settings.add_argument('-shutdown-disable', action='store_true',
                              help="Disallow to shutdown service by request.")

    def run(self, cli_args: list[str] | None = None) -> None:
        args = self.arguments.parse_args(cli_args)
        match args.command:
            case 'service':
                print_if_resp(*self._process_service(args))
            case 'mapping':
                print_if_resp(*self._process_mappings(args))
            case 'journal':
                print_if_resp(*self._process_journal(args))
            case 'record':
                print_if_resp(*self._process_recordings(args))
            case 'scenario':
                print_if_resp(*self._process_scenarios(args))
            case 'settings':
                print_if_resp(*self._process_settings(args))
            case _:
                print("Error during handling arguments. Use -h to get halp.")

    def _process_service(self, args: argparse.Namespace) -> tuple[Any | None, str | None]:
        if args.delay:
            return self._service_delay(args.delay)
        if args.reset:
            return self.service.reset()
        if args.stop:
            return self.service.shutdown()
        return None, None

    def _service_delay(self, args: Any) -> tuple[Any | None, str | None]:
        if len(args) == 1:
            try:
                return self.service.set_delay_fixed(int(args[0]))
            except ValueError:
                return None, "Expected to get single integer value, 'service -h' for more info."
        elif len(args) == 2:
            try:
                return self.service.set_delay_uniform(int(args[0]), int(args[1]))
            except ValueError:
                try:
                    return self.service.set_delay_log_normal(int(args[0]), float(args[1]))
                except ValueError:
                    return None, ("Unexpected argument types. Expected: "
                                  "INT -> fixed; INT INT -> uniform; INT FLOAT -> log normal "
                                  "'service -h' for more info.")
        else:
            return None, f"Unexpected number of arguments {len(args)}. Expected from 1 to 2"

    def _process_mappings(self, args: argparse.Namespace) -> tuple[Any | None, str | None]:
        if args.get is not None:
            return self._mappings_get(args.get)
        if args.get_meta:
            return self.mappings.find_by_metadata(args.get_meta[0])
        if args.create:
            return self.mappings.create(args.create[0])
        if args.delete is not None:
            return self._mappings_delete(args.delete)
        if args.delete_meta:
            return self.mappings.delete_by_metadata(args.delete_meta[0])
        if args.reset:
            return self.mappings.reset()
        if args.persist:
            return self.mappings.persist()
        if args.update:
            return self.mappings.update_by_id(args.update[0], args.update[1])
        return None, None

    def _mappings_delete(self, args: Any) -> tuple[Any | None, str | None]:
        if len(args) == 0:
            return self.mappings.delete()
        if len(args) > 0:
            return iterate_request(self.mappings.delete_by_id, args)
        return None, None

    def _mappings_get(self, args: Any) -> tuple[Any | None, str | None]:
        if len(args) == 0:
            return self.mappings.get()
        elif len(args) == 2:
            try:
                return self.mappings.get(int(args[0]), int(args[1]))
            except ValueError:
                return iterate_request(self.mappings.get_by_id, args)
        else:
            return iterate_request(self.mappings.get_by_id, args)

    def _process_journal(self, args: argparse.Namespace) -> tuple[Any | None, str | None]:
        if args.get is not None:
            return self._journal_get(args.get)
        if args.get_critaria:
            return self.journal.find_by_criteria(args.get_critaria[0])
        if args.delete is not None:
            return self._journal_delete(args.delete)
        if args.delete_critaria:
            return self.journal.delete_by_criteria(args.delete_critaria[0])
        if args.delete_metedata:
            return self.journal.delete_by_metadata(args.delete_metadata[0])
        if args.unmatched:
            return self.journal.get_unmatched()
        if args.miss:
            return self.journal.get_unmatched_near_misses()
        if args.miss_request:
            return self.journal.get_near_misses_by_request(args.miss_request[0])
        if args.miss_pattern:
            return self.journal.get_near_misses_by_pattern(args.miss_pattern[0])
        if args.reset:
            return self.journal.reset()
        if args.count:
            return self.journal.count_by_criteria(args.count[0])
        return None, None

    def _journal_get(self, args: Any) -> tuple[Any | None, str | None]:
        if len(args) == 0:
            return self.journal.get()
        elif len(args.get) == 2:
            try:
                return self.journal.get(int(args[0]), datetime.fromisoformat(args[1]))
            except ValueError:
                return iterate_request(self.journal.get_by_id, args)
        else:
            return iterate_request(self.journal.get_by_id, args)

    def _journal_delete(self, args: Any) -> tuple[Any | None, str | None]:
        if len(args) == 0:
            return self.journal.delete()
        if len(args) > 0:
            return iterate_request(self.journal.delete_by_id, args)
        return None, None

    def _process_recordings(self, args: argparse.Namespace) -> tuple[Any | None, str | None]:
        if args.start:
            return self.recordings.start(args.start[0])
        if args.stop:
            return self.recordings.stop()
        if args.status:
            return self.recordings.status()
        if args.snapshot:
            return self.recordings.snapshot(args.snapshot[0])
        return None, None

    def _process_scenarios(self, args: argparse.Namespace) -> tuple[Any | None, str | None]:
        if args.get:
            return self.scenarios.get()
        if args.reset:
            return self.scenarios.reset()
        return None, None

    def _process_settings(self, args: argparse.Namespace) -> tuple[Any | None, str | None]:
        if args.gen:
            return None, self.settings.generate(args.gen[0], int(
                                          args.gen[1]), bool(args.gen[3]))
        if args.host:
            return None, self.settings.change_host(args.host[0])
        if args.timeout:
            return None, self.settings.change_api_request_timeout(args.timeout[0])
        if args.shutdown_enable:
            return None, self.settings.enable_shutdown()
        if args.shutdown_disable:
            return None, self.settings.disable_shutdown()
        return None, None
