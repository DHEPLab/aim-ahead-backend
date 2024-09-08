import logging
import random
from typing import NamedTuple, Optional

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

    def __init__(
        self,
        user_repository: UserRepository,
        task_repository: TaskRepository,
        visit_occurrence_repository: VisitOccurrenceRepository,
    ):
        self.user_repository = user_repository
        self.task_repository = task_repository
        self.visit_occurrence_repository = visit_occurrence_repository
        self.logger = logging.getLogger(__name__)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise Exception("TaskManager must be initialized before use")
        return cls._instance

    def get_or_create_user_task(self, user_email: str) -> UserTaskResult:
        user = self.user_repository.get_user_by_email(user_email)
        if not user:
            raise BusinessException(BusinessExceptionEnum.UserNotInPilot)

        uncompleted_task = self.task_repository.get_uncompleted_task_for_user(
            user_email
        )
        print("uncompleted_task", uncompleted_task)
        if uncompleted_task:
            return UserTaskResult(task=uncompleted_task, is_new_assignment=False)

        new_task = self._random_assign_task(user_email)
        return UserTaskResult(task=new_task, is_new_assignment=bool(new_task))

    def _random_assign_task(self, user_email: str) -> Optional[Task]:
        all_visit_ids = set(
            self.visit_occurrence_repository.get_all_visit_occurrence_ids()
        )
        assigned_case_ids = set(
            self.task_repository.get_assigned_case_ids_for_user(user_email)
        )
        available_visits = list(all_visit_ids - assigned_case_ids)

        if not available_visits:
            self.logger.info(f"No available visits for user {user_email}")
            return None

        selected_visit = random.choice(available_visits)
        task = Task(user_email=user_email, case_id=selected_visit)

        try:
            created_task = self.task_repository.create_task(task)
            self.logger.info(
                f"New task for visit {selected_visit} assigned to user {user_email}"
            )
            return created_task
        except Exception as e:
            self.logger.error(
                f"Error creating task for user {user_email}, case {selected_visit}: {str(e)}"
            )
            raise e
