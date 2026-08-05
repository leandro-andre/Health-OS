from dataclasses import dataclass
from uuid import UUID, uuid4

from health_os.shared.domain import DomainEvent, Entity


@dataclass(frozen=True, slots=True)
class SomethingHappened(DomainEvent):
    name: str = "example"


def test_entity_exposes_its_id() -> None:
    entity_id = uuid4()
    entity = Entity[UUID](entity_id)

    assert entity.id == entity_id


def test_entity_starts_without_domain_events() -> None:
    entity = Entity[str]("entity-1")

    assert entity.domain_events == ()


def test_entity_registers_domain_events_in_order() -> None:
    entity = Entity[str]("entity-1")
    first_event = SomethingHappened(name="first")
    second_event = SomethingHappened(name="second")

    entity.register_domain_event(first_event)
    entity.register_domain_event(second_event)

    assert entity.domain_events == (first_event, second_event)


def test_entity_does_not_expose_mutable_domain_events_collection() -> None:
    entity = Entity[str]("entity-1")
    event = SomethingHappened()

    entity.register_domain_event(event)
    exposed_events = entity.domain_events

    assert exposed_events == (event,)
    assert isinstance(exposed_events, tuple)


def test_entity_clears_domain_events() -> None:
    entity = Entity[str]("entity-1")
    entity.register_domain_event(SomethingHappened())

    entity.clear_domain_events()

    assert entity.domain_events == ()


def test_entity_pulls_and_clears_domain_events() -> None:
    entity = Entity[str]("entity-1")
    event = SomethingHappened()
    entity.register_domain_event(event)

    pulled_events = entity.pull_domain_events()

    assert pulled_events == (event,)
    assert entity.domain_events == ()
