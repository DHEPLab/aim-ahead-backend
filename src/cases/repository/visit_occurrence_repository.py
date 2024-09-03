from typing import List

from src.cases.model.clinical_data.person.visit_occurrence import \
    VisitOccurrence


class VisitOccurrenceRepository:
    def __init__(self, session):
        self.session = session

    def get_visit_occurrence(self, visit_id: int):
        return self.session.get(VisitOccurrence, visit_id)

    def get_all_visit_occurrence_ids(self) -> List[int]:
        return [
            visit_id
            for (visit_id,) in self.session.query(
                VisitOccurrence.visit_occurrence_id
            ).all()
        ]
