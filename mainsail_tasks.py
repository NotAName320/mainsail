from typing import Union

from pytimeparse.timeparse import timeparse


class _Task:
    def __init__(self, name, description, enabled, content):
        self.name: str = name
        self.description: str = description
        self.enabled: bool = enabled
        self.content: str = content


class CommandTask(_Task):
    def __init__(self, data: dict):
        self.ros_only: bool = data.pop('ros_only')
        self.respond_to: str = data.pop('respond_to')
        super().__init__(**data)


class ScheduleTask(_Task):
    def __init__(self, data: dict):
        self.interval: int = timeparse(data.pop('interval'))
        self.execute_on_start: bool = data.pop('execute_on_start')
        target = data.pop('target')
        self.target: Union[str | int] = target if target == 'rmb' else int(target)
        super().__init__(**data)
