import pytest

from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from src.task.task_manager import TaskManager, UserTaskResult
from src.user.model.user import User
from src.task.model.task import Task
from src.task.repository.task_repository import TaskRepository
from src.user.repository.user_repository import UserRepository
from src.cases.repository.visit_occurrence_repository import VisitOccurrenceRepository
from tests.cases.case_fixture import input_case


@pytest.fixture(scope="function")
def setup_database(session):
    user1 = User(email="user1@example.com")
    user2 = User(email="user2@example.com")
    session.add(user1)
    session.add(user2)
    input_case(session, num_cases=5)
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def task_manager(setup_database):
    user_repo = UserRepository(setup_database)
    task_repo = TaskRepository(setup_database)
    visit_repo = VisitOccurrenceRepository(setup_database)
    return TaskManager(user_repo, task_repo, visit_repo)


def test_singleton_instance(setup_database):
    user_repo = UserRepository(setup_database)
    task_repo = TaskRepository(setup_database)
    visit_repo = VisitOccurrenceRepository(setup_database)
    TaskManager.initialize(user_repo, task_repo, visit_repo)
    instance1 = TaskManager.get_instance()
    instance2 = TaskManager.get_instance()
    assert instance1 is instance2


def test_get_instance_before_initialization():
    TaskManager._instance = None
    with pytest.raises(Exception, match="TaskManager must be initialized before use"):
        TaskManager.get_instance()


def test_user_not_found(task_manager):
    with pytest.raises(BusinessException) as exc_info:
        task_manager.get_or_create_user_task("nonexistent@example.com")
    assert exc_info.value.error == BusinessExceptionEnum.UserNotInPilot


def test_successful_new_task_assignment(task_manager, setup_database):
    result = task_manager.get_or_create_user_task("user1@example.com")
    assert isinstance(result, UserTaskResult)
    print(result)
    assert result.is_new_assignment == True
    assert isinstance(result.task, Task)

    tasks = setup_database.query(Task).filter_by(user_email="user1@example.com").all()
    assert len(tasks) == 1
    assert tasks[0].case_id in range(1, 9999)


def test_return_existing_uncompleted_task(task_manager, setup_database):
    first_result = task_manager.get_or_create_user_task("user1@example.com")
    assert first_result.is_new_assignment == True

    second_result = task_manager.get_or_create_user_task("user1@example.com")
    assert second_result.is_new_assignment == False
    assert second_result.task.id == first_result.task.id


def test_no_available_visits(task_manager, setup_database):
    for _ in range(5):
        result = task_manager.get_or_create_user_task("user1@example.com")
        assert result.task is not None and result.is_new_assignment
        setup_database.query(Task).filter_by(id=result.task.id).update({"completed": True})
        setup_database.flush()

    result = task_manager.get_or_create_user_task("user1@example.com")
    assert result.task is None
    assert result.is_new_assignment == False


def test_error_creating_task(task_manager, mocker):
    with mocker.patch('src.task.repository.task_repository.TaskRepository.create_task', side_effect=Exception("Database error")):
        with pytest.raises(Exception) as exc_info:
            task_manager.get_or_create_user_task("user1@example.com")
        assert str(exc_info.value) == "Database error"