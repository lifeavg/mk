import os
import pathlib
import platform
import shutil
import subprocess
import sys

import pkg_resources


def install_windows(update_settings: bool = True) -> None:
    installer_folder = pathlib.Path(os.path.dirname(__file__))
    print(f'Installation found at: {installer_folder}')

    program_files = pathlib.Path(os.environ['ProgramW6432']).joinpath('wmk')
    print(f'Program folder resolved as: {program_files}')

    try:
        shutil.copytree(installer_folder.joinpath(pathlib.Path('mk')),
                        program_files.joinpath(pathlib.Path('mk')),
                        dirs_exist_ok=True)
        print(f'Copied mk module files from {installer_folder} to {program_files}')
        shutil.copy(installer_folder.joinpath(pathlib.Path('main.py')), program_files)
        print(f'Copied main file from {installer_folder} to {program_files}')
        shutil.copytree(installer_folder.joinpath(pathlib.Path('bin')),
                        program_files.joinpath(pathlib.Path('bin')),
                        dirs_exist_ok=True)
        print(f'Copied bin files from {installer_folder} to {program_files}')

    except PermissionError as exception:
        print(f'{exception.strerror}: {exception.filename}. Please run in Administrator mode.')
        return

    home_folder = pathlib.Path.home().joinpath('.wmk')
    print(f'Home folder resolved as: {home_folder}')
    home_folder.mkdir(exist_ok=True)
    print(f'Created home folder at: {home_folder}')
    home_settings = home_folder.joinpath(r"settings.json")
    if not home_settings.exists() or update_settings:
        shutil.copy(installer_folder.joinpath(pathlib.Path(r'resources\settings.json')),
                    home_settings)
        print(f'Copied settings to home folder: {home_settings}')
    else:
        print('Settings were not copied')

    required = {'requests',}
    installed = set(map(lambda i: i.project_name, pkg_resources.working_set))
    missing = required - installed
    if missing:
        print(f'Installing missing packages {missing}')
        python = sys.executable
        subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
    else:
        print('All required packages are installed')
    bin_path = program_files.joinpath(pathlib.Path('bin'))
    print(f'Installation completed. Add {bin_path} to PATH')


def main() -> None:
    match platform.system():
        case 'Windows':
            install_windows(False)
        case _:
            print('Platform is not supported')


if __name__ == '__main__':
    main()
