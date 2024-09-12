import pytest

from src.cases.model.case_prediction import CasePrediction
from src.cases.repository.case_prediction_repository import CasePredictionRepository
from src.cases.repository.visit_occurrence_repository import VisitOccurrenceRepository
from tests.cases.case_fixture import input_case


@pytest.fixture(scope="session")
def visit_occurrence_repository(session):
    return VisitOccurrenceRepository(session)


@pytest.fixture(scope="session")
def case_prediction_repository(session):
    return CasePredictionRepository(session)


def test_get_prediction_by_case_id(session, visit_occurrence_repository, case_prediction_repository):
    input_case(session, 1)
    test_visit = visit_occurrence_repository.get_visit_occurrence(1)
    test_get_prediction = CasePrediction(test_visit.visit_occurrence_id, "free text")

    case_prediction_repository.session.add(test_get_prediction)

    case_prediction = case_prediction_repository.get_prediction_by_case_id(test_visit.visit_occurrence_id)

    assert case_prediction is not None


def test_get_prediction_by_case_id_return_none_if_not_exist(session, case_prediction_repository):
    case_prediction = case_prediction_repository.get_prediction_by_case_id(0)

    assert case_prediction is None

