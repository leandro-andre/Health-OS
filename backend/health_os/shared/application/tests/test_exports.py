import health_os.shared.application as application


def test_application_exports_event_bus_contracts() -> None:
    assert application.__all__ == [
        "EventBus",
        "EventHandler",
    ]
