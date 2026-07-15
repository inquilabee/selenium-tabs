from seleniumtabs.session import Session


def test_session_destructor_ignores_missing_driver_after_failed_initialization():
    session = Session.__new__(Session)

    assert session.__del__() is None
