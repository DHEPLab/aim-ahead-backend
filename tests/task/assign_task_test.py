import pytest

from cases.repository.visit_occurrence_repository import VisitOccurrenceRepository
from src.task.assign_task import AssignTask
from src.user.model.user import User
from src.task.model.task import Task
from task.repository.task_repository import TaskRepository
from tests.cases.case_fixture import input_case
from user.repository.user_repository import UserRepository


@pytest.fixture
def setup_database(session):
    user1 = User(email="user1@example.com")
    user2 = User(email="user2@example.com")
    session.add_all([user1, user2])
    session.flush()
    input_case(session, num_cases=5)
    yield session
    session.close()


@pytest.fixture
def task_assignment_service(setup_database):
    user_repo = UserRepository(setup_database)
    task_repo = TaskRepository(setup_database)
    visit_repo = VisitOccurrenceRepository(setup_database)
    return AssignTask(user_repo, task_repo, visit_repo)


def test_user_not_found(task_assignment_service):
    result = task_assignment_service.random_assign_task_to_user("nonexistent@example.com")
    assert result == False


def test_successful_task_assignment(task_assignment_service, setup_database):
    result = task_assignment_service.random_assign_task_to_user("user1@example.com")
    assert result == True

    tasks = setup_database.query(Task).filter_by(user_email="user1@example.com").all()
    assert len(tasks) == 1

    assert tasks[0].case_id in range(1, 9999)


def test_no_available_visits(task_assignment_service, setup_database):
    for _ in range(5):
        task_assignment_service.random_assign_task_to_user("user1@example.com")
        tasks = setup_database.query(Task).filter_by(user_email="user1@example.com").first()
        tasks.completed = True

    result = task_assignment_service.random_assign_task_to_user("user1@example.com")
    assert result == False


def test_multiple_assignments(task_assignment_service, setup_database):
    for _ in range(3):
        result = task_assignment_service.random_assign_task_to_user("user1@example.com")
        assert result == True

    tasks = setup_database.query(Task).filter_by(user_email="user1@example.com").all()
    assert len(tasks) == 3
    assert len(set(task.case_id for task in tasks)) == 3


def test_all_visits_assigned(task_assignment_service, setup_database):
    for _ in range(5):
        result = task_assignment_service.random_assign_task_to_user("user1@example.com")
        assert result == True

    result = task_assignment_service.random_assign_task_to_user("user1@example.com")
    assert result == False


def test_random_distribution(task_assignment_service, setup_database):
    assignments = []
    for _ in range(20):
        setup_database.query(Task).delete()
        setup_database.commit()
        task_assignment_service.random_assign_task_to_user("user1@example.com")
        task = setup_database.query(Task).filter_by(user_email="user1@example.com").first()
        assignments.append(task.case_id)

    assert len(set(assignments)) > 1, "Assignments are not random"

def test_get_instance_before_initialization():
    AssignTask._instance = None
    with pytest.raises(Exception, match="AssignTask must be initialized before use"):
        AssignTask.get_instance()