import sys
from typing import List

from httpx import HTTPStatusError
from nsdotpy.session import NSSession

from mainsail_tasks import CommandTask
from template_handler import template_handler


class CommandHandler:
    def __init__(self, commands: List[CommandTask]):
        self.commands = commands

    def scan_rmb(self, client: NSSession):
        try:
            messages = client.api_request('region', target=client.region, shard='messages')
        except HTTPStatusError:
            print('Unable to get RMB, commands not processed!', file=sys.stderr)
            return

        messages = messages['messages']['post']
        messages = [messages] if isinstance(messages, dict) else messages

        # only scan posts after bot's latest message to prevent doubleposting
        if client.nation.lower().replace(' ', '_') in [x['nation'] for x in messages]:
            self_post_index = [i for i, n in enumerate(messages) if n['nation'] == client.nation.lower().replace(' ', '_')][-1]
            messages = messages[self_post_index:]

        for message in messages:
            if message['status'] != '0' or message['nation'] == client.nation.lower().replace(' ', '_'):
                continue
            for command in self.commands:
                if template_handler(message['message'], client) == command.respond_to:
                    try:
                        client.api_rmb(client.nation, client.region, command.content.replace('[user]', f'[nation]{message["nation"]}[/nation]'), client.password)
                    except HTTPStatusError:
                        print(f'Executing command {command.name} failed!', file=sys.stderr)
