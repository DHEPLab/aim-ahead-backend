from src.answer.model.answer import Answer
from src.answer.repository.answer_repository import AnswerRepository
from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)
from src.configration.repository.answer_config_repository import \
    AnswerConfigurationRepository
from src.task.repository.task_repository import TaskRepository
from src.user.utils import auth_utils


class AnswerService:
    def __init__(
        self,
        answer_repository: AnswerRepository,
        answer_config_repository: AnswerConfigurationRepository,
        task_repository: TaskRepository,
    ):
        self.answer_repository = answer_repository
        self.answer_config_repository = answer_config_repository
        self.task_repository = task_repository

    def add_answer_response(self, task_id: str, data: dict):
        user_email = auth_utils.get_user_email_from_jwt()
        answer = data["answer"]
        answer_config_id = data["answerConfigId"]

        task = self.task_repository.get_task(task_id)
        if not task or task.user_email != user_email:
            raise BusinessException(BusinessExceptionEnum.NoAccessToCaseReview)

        answer_config = self.answer_config_repository.get_answer_config(
            answer_config_id
        )
        if answer_config is None:
            raise BusinessException(BusinessExceptionEnum.NoAnswerConfigAvailable)

        answer_saved = self.answer_repository.add_answer(
            Answer(
                task_id=task_id,
                answer_config_id=answer_config.id,
                answer=answer,
            )
        )
        task.completed = True

        return answer_saved
