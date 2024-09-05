from datetime import datetime
import re
import uuid
import pytest
from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from src.configration.model.answer_config import AnswerConfig
from src.configration.repository.answer_config_repository import AnswerConfigurationRepository
from src.answer.repository.answer_repository import AnswerRepository
from src.answer.service.answer_service import AnswerService
from src.task.model.task import Task
from src.task.repository.task_repository import TaskRepository


@pytest.fixture
def task_id():
    return '1'


@pytest.fixture
def user_email():
    return 'user@test.com'


@pytest.fixture
def dict_data():
    return {
        "answerConfigId": uuid.uuid4(),
        "answer": {"question": "answer", "question2": "answer2"}
    }


@pytest.fixture()
def mock_answer_repo(mocker):
    return mocker.Mock(AnswerRepository)


@pytest.fixture()
def mock_task_repo(mocker):
    return mocker.Mock(TaskRepository)


@pytest.fixture()
def mock_answer_config_repo(mocker):
    return mocker.Mock(AnswerConfigurationRepository)


@pytest.fixture(autouse=True)
def before_each_tests(mocker, user_email):
    mocker.patch('src.user.utils.auth_utils.get_user_email_from_jwt', return_value=user_email)


def test_add_answer_response(
        task_id,
        user_email,
        dict_data,
        mock_answer_repo,
        mock_task_repo,
        mock_answer_config_repo
):
    task = Task(path_config=[], user_email=user_email, case_id=1)
    mock_task_repo.get_task.return_value = task
    mock_answer_config_repo.get_answer_config.return_value = AnswerConfig(
        id=dict_data["answerConfigId"],
        config=[{"type": "Text", "title": "title"}],
        created_timestamp=datetime.now()
    )
    answer_service = AnswerService(mock_answer_repo, mock_answer_config_repo, mock_task_repo)

    answer_service.add_answer_response(task_id, dict_data)

    assert mock_answer_repo.add_answer.called
    assert task.completed


def test_add_answer_response_failed_when_user_and_case_not_match(
        task_id,
        dict_data,
        mock_answer_repo,
        mock_task_repo,
        mock_answer_config_repo
):
    mock_task_repo.get_task.return_value = Task(
        path_config=[],
        user_email="user-not-match@test.com",
        case_id=1
    )

    answer_service = AnswerService(mock_answer_repo, mock_answer_config_repo, mock_task_repo)

    with pytest.raises(BusinessException, match=re.compile(BusinessExceptionEnum.NoAccessToCaseReview.name)):
        answer_service.add_answer_response(task_id, dict_data)


def test_add_answer_response_failed_with_no_answer_config(
        task_id,
        user_email,
        dict_data,
        mock_answer_repo,
        mock_task_repo,
        mock_answer_config_repo
):
    mock_task_repo.get_task.return_value = Task(path_config=[], user_email=user_email, case_id=1)
    mock_answer_config_repo.get_answer_config.return_value = None

    answer_service = AnswerService(mock_answer_repo, mock_answer_config_repo, mock_task_repo)

    with pytest.raises(BusinessException, match=re.compile(BusinessExceptionEnum.NoAnswerConfigAvailable.name)):
        answer_service.add_answer_response(task_id, dict_data)
