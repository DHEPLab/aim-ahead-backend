import pytest
from sqlalchemy.exc import IntegrityError

from src.user.repository.user_repository import UserRepository
from src.user.model.user import User


@pytest.fixture(scope="session")
def user_repository(session):
    return UserRepository(session)


def test_create_user(user_repository: UserRepository):
    user = User(name="123", email="goodbye@sunwukong.com")

    user_repository.create_user(user)
    created = user_repository.get_user_by_id(user.id)

    assert created.email == user.email
    assert created.id is not None


def test_create_user_failed_due_to_duplicate_email(user_repository: UserRepository):
    user = User(name="123", email="goodbye@sunwukong.com")
    user_repository.create_user(user)

    user.id = None
    with pytest.raises(IntegrityError):
        user_repository.create_user(user)


def test_get_user_by_id_success(user_repository: UserRepository):
    user = User(name="123", email="goodbye@sunwukong.com")
    user_repository.create_user(user)

    found = user_repository.get_user_by_id(user.id)

    assert found is not None


def test_get_user_by_id_failed(user_repository: UserRepository):
    found = user_repository.get_user_by_id(99999)
    assert found is None


def test_get_user_by_email_success(user_repository: UserRepository):
    user = User(name="123", email="goodbye@sunwukong.com")
    user_repository.create_user(user)

    found = user_repository.get_user_by_email(user.email)

    assert found is not None


def test_get_user_by_email_failed(user_repository):
    found = user_repository.get_user_by_email("nonexistent.email@email.com")

    assert found is None


def test_get_users(user_repository):
    user_1 = User(name="123", email="goodbye@sunwukong.com", position="position",
                  employer="employer", area_of_clinical_ex="area_of_clinical_ex")
    user_2 = User(name="123", email="goodbye2@sunwukong.com", position="position",
                  employer="employer", area_of_clinical_ex="area_of_clinical_ex")
    user_repository.create_user(user_1)
    user_repository.create_user(user_2)

    users = user_repository.get_users()

    assert len(users) == 2
    assert users[0].email == user_1.email
    assert users[1].email == user_2.email


def test_query_user_by_email_success(user_repository: UserRepository):
    user = User(name="john", email="goodbye@sunwukong.com")
    user_repository.create_user(user)

    found = user_repository.query_user_by_email(user.email)

    assert found is not None


def test_query_user_by_email_failed(user_repository):
    found = user_repository.query_user_by_email("nonexistent.email@email.com")

    assert found is None


def test_update_user(user_repository):
    user = User(name="john", email="goodbye@sunwukong.com")
    user_repository.create_user(user)

    inserted_user = user_repository.query_user_by_email(user.email)

    assert inserted_user.active == False

    user_repository.update_user(inserted_user.copy(active=True))
    assert user_repository.query_user_by_email(user.email).active == True


def test_get_active_users(user_repository):
    user_1 = User(name="123", email="tianmingren@heifengshan.com")
    user_2 = User(name="123", email="zhuwujing@gaolaozhuang.com")
    user_repository.create_user(user_1)
    user_repository.create_user(user_2)
    inserted_user = user_repository.query_user_by_email(user_1.email)
    user_repository.update_user(inserted_user.copy(active=True))

    active_users = user_repository.get_active_users()

    assert len(active_users) == 1
    assert active_users[0].email == user_1.email
    assert active_users[0].active == True
