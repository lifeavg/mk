import platform
from mk.settings import get_config_path
from mk import cli

def main() -> None:
    path, err = get_config_path(platform.system())
    if err is not None:
        print(err)
        return
    app = cli.Cli(path)
    err = app.load()
    if err is not None:
        print(err)
    app.run()

if __name__ == '__main__':
    main()
