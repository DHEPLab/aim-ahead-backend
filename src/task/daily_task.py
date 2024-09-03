import random

from src import db
from src.cases.repository.visit_occurrence_repository import \
    VisitOccurrenceRepository
from src.task.repository.task_repository import TaskRepository
from user.repository.user_repository import UserRepository

MAX_TASKS = 10


def create_daily_task():
    session = db.session
    visit_occurrence_repo = VisitOccurrenceRepository(session)
    task_repo = TaskRepository(session)
    user_repo = UserRepository(session)

    users = user_repo.get_active_users()
    all_cases_ids = visit_occurrence_repo.get_all_visit_occurrence_ids()

    for user in users:
        existing_tasks_count = task_repo.get_uncompleted_tasks_count_for_user(
            user.email
        )
        if existing_tasks_count < MAX_TASKS:
            assigned_case_ids = task_repo.get_assigned_case_ids_for_user(user.email)
            available_cases = [
                case_id for case_id in all_cases_ids if case_id not in assigned_case_ids
            ]

            num_new_tasks = min(MAX_TASKS - existing_tasks_count, len(available_cases))
            selected_visits = random.sample(available_cases, num_new_tasks)

            for visit_id in selected_visits:
                try:
                    task_repo.create_task(user.email, visit_id)
                except Exception as e:
                    print(
                        f"Error creating task for user {user.email}, case {visit_id}: {str(e)}"
                    )
                    continue
