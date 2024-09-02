import pytest

from src.task.model.task import Task
from src.task.repository.task_repository import TaskRepository


@pytest.fixture(scope="session")
def task_repository(session):
    return TaskRepository(session)


def test_create_task(task_repository: TaskRepository):
    task = Task(case_id=1, user_email="goodbye@sunwukong.com")

    task_repository.create_task(task)

    created = task_repository.get_task(task.id)
    assert created.case_id == task.case_id
    assert created.id is not None


def test_get_task(task_repository: TaskRepository):
    task = Task(case_id=1, user_email="goodbye@sunwukong.com")
    task_repository.create_task(task)

    found = task_repository.get_task(task.id)

    assert found is not None


def test_get_task_by_user_email(task_repository: TaskRepository):
    task = Task(case_id=1, user_email="goodbye@sunwukong.com")
    task_repository.create_task(task)

    found = task_repository.get_task_by_user(task.user_email)

    assert found is not None
    assert found is task


def test_not_get_task_by_user_email_when_task_is_completed(task_repository: TaskRepository):
    task = Task(case_id=1, user_email="goodbye@sunwukong.com", completed=True)
    task_repository.create_task(task)

    found = task_repository.get_task_by_user(task.user_email)

    assert found is None


def test_get_first_task_when_user_have_many_tasks(task_repository: TaskRepository):
    task = Task(case_id=1, user_email="goodbye@sunwukong.com")
    another_task = Task(case_id=2, user_email="goodbye@sunwukong.com")
    task_repository.create_task(task)
    task_repository.create_task(another_task)

    found = task_repository.get_task_by_user(task.user_email)

    assert found is task
