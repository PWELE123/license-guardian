import license_guardian as lg


def test_ping() -> None:
    assert lg.ping() == "pong"
