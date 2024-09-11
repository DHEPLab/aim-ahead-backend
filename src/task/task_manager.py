import random
from typing import NamedTuple, Optional

from sqlalchemy.exc import IntegrityError

from src.cases.repository.visit_occurrence_repository import \
    VisitOccurrenceRepository
from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)
from src.task.model.task import Task
from src.task.repository.task_repository import TaskRepository
from src.user.repository.user_repository import UserRepository


class UserTaskResult(NamedTuple):
    task: Optional[Task]
    is_new_assignment: bool


class TaskManager:
    _instance = None

    @classmethod
    def initialize(
        cls,
        user_repository: UserRepository,
        task_repository: TaskRepository,
        visit_occurrence_repository: VisitOccurrenceRepository,
    ):
        if cls._instance is None:
            cls._instance = cls(
                user_repository, task_repository, visit_occurrence_repository
            )
        print("TaskManager initialized")

    def __init__(
        self,
        user_repository: UserRepository,
        task_repository: TaskRepository,
        visit_occurrence_repository: VisitOccurrenceRepository,
    ):
        self.user_repository = user_repository
        self.task_repository = task_repository
        self.visit_occurrence_repository = visit_occurrence_repository
        print(
            f"TaskManager instance created with repositories:"
            f" {user_repository}, {task_repository}, {visit_occurrence_repository}"
        )

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("ERROR: TaskManager must be initialized before use")
            raise Exception("TaskManager must be initialized before use")
        return cls._instance

    def get_or_create_user_task(self, user_email: str) -> UserTaskResult:
        print(f"Attempting to get or create task for user: {user_email}")
        user = self.user_repository.get_user_by_email(user_email)
        if not user:
            print(f"User not found in pilot: {user_email}")
            raise BusinessException(BusinessExceptionEnum.UserNotInPilot)

        uncompleted_task = self.task_repository.get_task_by_user(user_email)
        print(f"Uncompleted task for user {user_email}: {uncompleted_task}")
        if uncompleted_task:
            return UserTaskResult(task=uncompleted_task, is_new_assignment=False)

        new_task = self._random_assign_task(user_email)
        return UserTaskResult(task=new_task, is_new_assignment=bool(new_task))

    def _random_assign_task(self, user_email: str) -> Optional[Task]:
        print(f"Attempting to randomly assign task for user: {user_email}")
        all_visit_ids = set(
            self.visit_occurrence_repository.get_all_visit_occurrence_ids()
        )
        assigned_case_ids = set(
            self.task_repository.get_assigned_case_ids_for_user(user_email)
        )
        available_visits = list(all_visit_ids - assigned_case_ids)

        if not available_visits:
            print(f"No available visits for user {user_email}")
            return None

        selected_visit = random.choice(available_visits)
        task = Task(user_email=user_email, case_id=selected_visit)

        try:
            created_task = self.task_repository.create_task(task)
            print(f"New task for visit {selected_visit} assigned to user {user_email}")
            return created_task
        except IntegrityError as e:
            print(
                f"Error: Creating same task for user {user_email}, case {selected_visit}: {str(e)}"
            )
            return None
        except Exception as e:
            print(
                f"Error: Creating task for user {user_email}, case {selected_visit}: {str(e)}"
            )
            raise e
