from typing import List

from sqlalchemy import false

from src.task.model.task import Task


class TaskRepository:
    def __init__(self, session):
        self.session = session

    def create_task(self, task: Task):
        self.session.add(task)
        self.session.flush()
        return task

    def get_task(self, task_id: str) -> Task:
        return self.session.get(Task, task_id)

    def get_task_by_user(self, user_email: str) -> Task:
        return (
            self.session.query(Task)
            .filter(Task.user_email == user_email, Task.completed == false())
            .first()
        )

    def get_assigned_case_ids_for_user(self, user_email: str) -> List[int]:
        return [
            task.case_id
            for task in self.session.query(Task.case_id)
            .filter(Task.user_email == user_email)
            .distinct()
        ]

    def get_uncompleted_task_for_user(self, user_email: str) -> Task:
        return (
            self.session.query(Task)
            .filter(Task.user_email == user_email, Task.completed == false())
            .first()
        )
