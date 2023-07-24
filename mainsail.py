"""
This file is part of mainsail, a regional infrastructure bot for
NationStates (https://github.com/NotAName320/mainsail).
Copyright (c) 2023 NotAName320.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""


import json
import os
from pathlib import Path
import sys
import time
from typing import List

from httpx import HTTPStatusError
from nsdotpy.session import NSSession
import schedule

from command_handler import CommandHandler
from mainsail_tasks import CommandTask, ScheduleTask


SCRIPT_NAME = 'mainsail'  # working title for now
AUTHOR = 'Notanam'
VERSION = '0.0.1'  # increment every release
SOURCE_LINK = 'https://github.com/NotAName320/mainsail'

SETTINGS_TO_CHECK_FOR = ['main_nation', 'bot_username', 'bot_password', 'region']


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

    print(f'User agent set to {config["main_nation"]}...')

    client = NSSession(SCRIPT_NAME, VERSION, AUTHOR, config['main_nation'], link_to_src=SOURCE_LINK)
    client.nation = config['bot_username']
    client.region = config['region']
    client.password = config['bot_password']

    try:
        client.api_request('nation', target=config['bot_username'], shard='ping', password=client.password)
    except HTTPStatusError:
        print(f'Unable to log in to {config["bot_username"]}. Please check passsword in config.', file=sys.stderr)

        exit(1)

    print(f'Logged into {config["bot_username"]}!')

    if not os.path.isdir('./tasks'):
        print(f'Tasks folder not found... creating with examples.', file=sys.stderr)

        os.makedirs('./tasks')

        example_command = {
            'enabled': True,
            'name': 'Ping',
            'description': 'A command that pongs.',
            'content': '[user] pong!',
            'type': 'command',
            'ros_only': False,
            'respond_to': '[bot_nation] ping',
        }

        example_schedule = {
            'enabled': True,
            'name': '24 Hours',
            'description': 'Posts on the RMB every 24 hours.',
            'content': 'It\'s been 24 hours since this bot started!',
            'type': 'schedule',
            'interval': '1d',
            'execute_on_start': False,
            'target': 'rmb'
        }

        with open('./tasks/example_command.json', 'w') as file:
            json.dump(example_command, file, indent=4)

        with open('./tasks/example_schedule.json', 'w') as file:
            json.dump(example_schedule, file, indent=4)

    commands: List[CommandTask] = []
    schedules: List[ScheduleTask] = []
    for file in Path('./tasks').glob('*.json'):
        try:
            with open('./tasks/' + file.name, 'r') as task_file:
                task: dict = json.load(task_file)

                if not task['enabled']:
                    continue

                if task.pop('type') == 'command':
                    commands.append(CommandTask(task))
                    print(f'Successfully loaded command {task["name"]} from file {file.name}!')
                else:
                    schedules.append(ScheduleTask(task))
                    print(f'Successfully loaded schedule {task["name"]} from file {file.name}!')
        except KeyError:
            print(f'Failed to load {file.name} (formatting error)!', file=sys.stderr)
            continue

    command_listener = CommandHandler(commands)

    schedule.every(10).seconds.do(command_listener.scan_rmb, client=client)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping!', file=sys.stderr)

        exit(0)


if __name__ == '__main__':
    main()
