# src/tasks/task_assignment_service.py

import random

from src.cases.repository.visit_occurrence_repository import \
    VisitOccurrenceRepository
from src.task.model.task import Task
from src.task.repository.task_repository import TaskRepository
from src.user.repository.user_repository import UserRepository


class AssignTask:
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

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise Exception("AssignTask must be initialized before use")
        return cls._instance

    def __init__(
        self,
        user_repository: UserRepository,
        task_repository: TaskRepository,
        visit_occurrence_repository: VisitOccurrenceRepository,
    ):
        self.user_repository = user_repository
        self.task_repository = task_repository
        self.visit_occurrence_repository = visit_occurrence_repository

    def random_assign_task_to_user(self, user_email: str) -> bool:
        user = self.user_repository.get_user_by_email(user_email)
        if not user:
            print(f"User {user_email} not found")
            return False

        all_visit_ids = set(
            self.visit_occurrence_repository.get_all_visit_occurrence_ids()
        )
        assigned_case_ids = set(
            self.task_repository.get_assigned_case_ids_for_user(user_email)
        )
        available_visits = list(all_visit_ids - assigned_case_ids)

        if not available_visits:
            print(f"No available tasks for user: {user_email}")
            return False

        selected_visit = random.choice(available_visits)
        task = Task(user_email=user_email, case_id=selected_visit)
        try:
            self.task_repository.create_task(task)
            print(f"Task for visit {selected_visit} assigned to user {user_email}")
            return True
        except Exception as e:
            print(
                f"Error creating task for user {user_email}, case {selected_visit}: {str(e)}"
            )
            return False
