from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def process(self, request):
        raise NotImplementedError


class ControllerCommand(Command):
    def __init__(self, action) -> None:
        self._action = action

    def process(self, request):
        return self._action(request)
