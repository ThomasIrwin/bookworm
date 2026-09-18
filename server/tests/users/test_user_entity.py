"""Ports UserTest."""

from app.users.entities import User


def test_no_arg_constructor_creates_instance_with_null_fields() -> None:
    user = User()

    assert user.id is None
    assert user.auth0_id is None


def test_constructor_with_parameters_sets_fields_correctly() -> None:
    user = User(auth0_id="auth0|123")

    assert user.auth0_id == "auth0|123"


def test_set_id_get_id_works_correctly() -> None:
    user = User()
    user.id = 42

    assert user.id == 42


def test_set_auth0_id_get_auth0_id_works_correctly() -> None:
    user = User()
    user.auth0_id = "auth0|999"

    assert user.auth0_id == "auth0|999"
