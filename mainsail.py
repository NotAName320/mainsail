import json
import os
import sys

from httpx import HTTPStatusError
from nsdotpy.session import NSSession


SCRIPT_NAME = 'mainsail'  # working title for now
AUTHOR = 'Notanam'
VERSION = '0.0.1'  # increment every release
SOURCE_LINK = 'https://github.com/NotAName320/mainsail'

SETTINGS_TO_CHECK_FOR = ['main_nation', 'bot_username', 'bot_password']


def main():
    print(f'Welcome to {SCRIPT_NAME} v{VERSION}!')

    if not os.path.isfile('./config.json'):
        new_config = dict(zip(SETTINGS_TO_CHECK_FOR, ['' for _ in SETTINGS_TO_CHECK_FOR]))  # generate blank value for each setting

        with open('config.json', 'w') as file:
            json.dump(new_config, file, indent=4)

        print('No config.json detected!\nOne has been created for you. Please fill the values out and rerun.', file=sys.stderr)

        exit(1)

    with open('config.json', 'r') as file:
        config: dict = json.load(file)

    if not set(SETTINGS_TO_CHECK_FOR).issubset(config.keys()):
        not_in_config = set(SETTINGS_TO_CHECK_FOR).difference(config.keys())

        for setting in not_in_config:
            config[setting] = ''

        with open('config.json', 'w') as file:
            json.dump(config, file, indent=4)

        print(f'config.json was missing these values:\n{not_in_config}\nPlease fill them out.', file=sys.stderr)

        exit(1)

    print(f'User agent set to {config["main_nation"]}')

    client = NSSession(SCRIPT_NAME, VERSION, AUTHOR, config['main_nation'], link_to_src='')

    try:
        client.api_request('nation', target=config['bot_username'], shard='ping', password=config['bot_password'])
    except HTTPStatusError:
        print(f'Unable to log in to {config["bot_username"]}. Please check passsword in config.', file=sys.stderr)

        exit(1)


if __name__ == '__main__':
    main()
