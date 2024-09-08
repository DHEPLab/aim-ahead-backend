from typing import List

from sqlalchemy import select

from src.cases.model.clinical_data.person.visit_occurrence import \
    VisitOccurrence


class VisitOccurrenceRepository:
    def __init__(self, session):
        self.session = session

    def get_visit_occurrence(self, visit_id: int):
        return self.session.get(VisitOccurrence, visit_id)

    def get_all_visit_occurrence_ids(self) -> List[int]:
        statement = select(VisitOccurrence.visit_occurrence_id)
        return self.session.execute(statement).scalars().all()
