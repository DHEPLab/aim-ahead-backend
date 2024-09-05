import pytest
from datetime import datetime
from src.task.repository.task_repository import TaskRepository
from src.task.model.task import Task


@pytest.fixture(scope="session")
def task_repository(session):
    return TaskRepository(session)


def test_get_uncompleted_tasks_count_for_user(task_repository, session):
    user_email = "test@example.com"
    session.add(Task(user_email=user_email, case_id=1, completed=False))
    session.add(Task(user_email=user_email, case_id=2, completed=False))
    session.add(Task(user_email=user_email, case_id=3, completed=True))
    session.add(Task(user_email="other@example.com", case_id=4, completed=False))
    session.flush()

    count = task_repository.get_uncompleted_tasks_count_for_user(user_email)
    assert count == 2


def test_create_task(task_repository):
    user_email = "test@example.com"
    case_id = 1
    path_config = '["config1", "config2"]'
    task=Task(user_email=user_email, case_id=case_id, path_config=path_config,review_started_timestamp=datetime.utcnow()
              )
    task = task_repository.create_task(task)

    assert task.id is not None
    assert task.user_email == user_email
    assert task.case_id == case_id
    assert task.path_config == path_config
    assert task.completed == False
    assert isinstance(task.created_timestamp, datetime)




def test_get_assigned_case_ids_for_user(task_repository, session):
    user_email = "test@example.com"
    session.add(Task(user_email=user_email, case_id=1))
    session.add(Task(user_email=user_email, case_id=2))
    session.add(Task(user_email=user_email, case_id=2))
    session.add(Task(user_email="other@example.com", case_id=3))
    session.flush()

    case_ids = task_repository.get_assigned_case_ids_for_user(user_email)
    assert set(case_ids) == {1, 2}


def test_get_assigned_case_ids_for_user_no_tasks(task_repository):
    user_email = "nonexistent@example.com"
    case_ids = task_repository.get_assigned_case_ids_for_user(user_email)
    assert case_ids == []

