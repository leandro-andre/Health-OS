from dataclasses import dataclass
from uuid import UUID, uuid4

from health_os.shared.domain import AggregateRoot, DomainEvent, Entity


@dataclass(frozen=True, slots=True)
class SomethingHappened(DomainEvent):
    name: str = "example"


class SampleEntity(Entity[UUID]):
    pass


class OtherSampleEntity(Entity[UUID]):
    pass


class SampleAggregateRoot(AggregateRoot[UUID]):
    pass


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


def test_entities_of_same_concrete_type_and_id_are_equal() -> None:
    entity_id = uuid4()

    assert SampleEntity(entity_id) == SampleEntity(entity_id)


def test_entities_with_different_ids_are_not_equal() -> None:
    assert SampleEntity(uuid4()) != SampleEntity(uuid4())


def test_entities_of_different_concrete_types_are_not_equal() -> None:
    entity_id = uuid4()

    assert SampleEntity(entity_id) != OtherSampleEntity(entity_id)


def test_entity_can_be_used_in_set() -> None:
    entity_id = uuid4()
    entities = {
        SampleEntity(entity_id),
        SampleEntity(entity_id),
        SampleEntity(uuid4()),
    }

    assert len(entities) == 2


def test_equal_entities_have_same_hash() -> None:
    entity_id = uuid4()

    assert hash(SampleEntity(entity_id)) == hash(SampleEntity(entity_id))


def test_entity_can_be_used_as_dict_key() -> None:
    entity_id = uuid4()
    values = {
        SampleEntity(entity_id): "first",
        SampleEntity(entity_id): "second",
    }

    assert values[SampleEntity(entity_id)] == "second"
    assert len(values) == 1


def test_aggregate_root_preserves_identity_and_domain_events() -> None:
    aggregate_id = uuid4()
    aggregate = SampleAggregateRoot(aggregate_id)
    event = SomethingHappened()

    aggregate.register_domain_event(event)

    assert aggregate.id == aggregate_id
    assert aggregate == SampleAggregateRoot(aggregate_id)
    assert aggregate.domain_events == (event,)
