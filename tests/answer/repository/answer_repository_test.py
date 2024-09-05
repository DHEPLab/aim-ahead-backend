import pytest

from src.answer.model.answer import Answer
from src.answer.repository.answer_repository import AnswerRepository


@pytest.fixture
def answer_repository(session):
    return AnswerRepository(session)


def test_add_answer(answer_repository):
    answer = Answer(
        task_id='123',
        case_id=1,
    )

    answer_repository.add_answer(answer)

    assert answer.id is not None

