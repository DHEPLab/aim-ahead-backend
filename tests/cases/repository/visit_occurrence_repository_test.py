from datetime import datetime, timedelta

import pytest

from src.cases.model.clinical_data.person.visit_occurrence import VisitOccurrence
from src.cases.repository.visit_occurrence_repository import \
    VisitOccurrenceRepository
from tests.cases.case_fixture import input_case


@pytest.fixture(scope="session")
def visit_occurrence_repository(session):
    return VisitOccurrenceRepository(session)


def test_get_visit_occurrence(visit_occurrence_repository: VisitOccurrenceRepository, session):
    input_case(session)

    visit = visit_occurrence_repository.get_visit_occurrence(1)

    assert visit is not None
    assert visit.person_id == 1


def test_get_all_visit_occurrence_ids(visit_occurrence_repository: VisitOccurrenceRepository, session):
    input_case(session, num_cases=3)

    all_visit_ids = visit_occurrence_repository.get_all_visit_occurrence_ids()
    assert len(all_visit_ids) == 3
