import health_os.shared.infrastructure as infrastructure


def test_infrastructure_exports_in_memory_event_bus() -> None:
    assert infrastructure.__all__ == [
        "InMemoryEventBus",
    ]
