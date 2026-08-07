from dataclasses import dataclass

import pytest

from health_os.shared.application import EventBus, EventHandler
from health_os.shared.domain import DomainEvent
from health_os.shared.infrastructure import InMemoryEventBus


@dataclass(frozen=True, slots=True)
class UserRegistered(DomainEvent):
    email: str = "user@example.com"


@dataclass(frozen=True, slots=True)
class ProfileUpdated(DomainEvent):
    display_name: str = "Ana"


class RecordingHandler:
    def __init__(self, calls: list[str], name: str) -> None:
        self._calls = calls
        self._name = name

    def handle(self, event: DomainEvent) -> None:
        self._calls.append(f"{self._name}:{type(event).__name__}")


class FailingHandler:
    def handle(self, event: DomainEvent) -> None:
        raise RuntimeError("handler failed")


def test_in_memory_event_bus_implements_event_bus_protocol() -> None:
    event_bus: EventBus = InMemoryEventBus()

    assert isinstance(event_bus, InMemoryEventBus)


def test_recording_handler_implements_event_handler_protocol() -> None:
    calls: list[str] = []
    handler: EventHandler = RecordingHandler(calls, "handler")

    handler.handle(UserRegistered())

    assert calls == ["handler:UserRegistered"]


def test_event_bus_registers_and_publishes_event_to_handler() -> None:
    event_bus = InMemoryEventBus()
    calls: list[str] = []
    handler = RecordingHandler(calls, "handler")

    event_bus.register(UserRegistered, handler)
    event_bus.publish(UserRegistered())

    assert calls == ["handler:UserRegistered"]


def test_event_bus_ignores_handlers_registered_for_other_event_types() -> None:
    event_bus = InMemoryEventBus()
    calls: list[str] = []

    event_bus.register(ProfileUpdated, RecordingHandler(calls, "profile"))
    event_bus.publish(UserRegistered())

    assert calls == []


def test_event_bus_publishes_event_without_handlers() -> None:
    event_bus = InMemoryEventBus()

    event_bus.publish(UserRegistered())


def test_event_bus_publishes_event_to_multiple_handlers() -> None:
    event_bus = InMemoryEventBus()
    calls: list[str] = []

    event_bus.register(UserRegistered, RecordingHandler(calls, "first"))
    event_bus.register(UserRegistered, RecordingHandler(calls, "second"))
    event_bus.publish(UserRegistered())

    assert calls == ["first:UserRegistered", "second:UserRegistered"]


def test_event_bus_executes_handlers_in_registration_order() -> None:
    event_bus = InMemoryEventBus()
    calls: list[str] = []

    event_bus.register(UserRegistered, RecordingHandler(calls, "1"))
    event_bus.register(UserRegistered, RecordingHandler(calls, "2"))
    event_bus.register(UserRegistered, RecordingHandler(calls, "3"))
    event_bus.publish(UserRegistered())

    assert calls == ["1:UserRegistered", "2:UserRegistered", "3:UserRegistered"]


def test_event_bus_propagates_handler_exceptions() -> None:
    event_bus = InMemoryEventBus()

    event_bus.register(UserRegistered, FailingHandler())

    with pytest.raises(RuntimeError, match="handler failed"):
        event_bus.publish(UserRegistered())


def test_event_bus_stops_after_handler_exception() -> None:
    event_bus = InMemoryEventBus()
    calls: list[str] = []

    event_bus.register(UserRegistered, RecordingHandler(calls, "before"))
    event_bus.register(UserRegistered, FailingHandler())
    event_bus.register(UserRegistered, RecordingHandler(calls, "after"))

    with pytest.raises(RuntimeError, match="handler failed"):
        event_bus.publish(UserRegistered())

    assert calls == ["before:UserRegistered"]
