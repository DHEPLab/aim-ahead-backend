from src.cases.model.case_prediction import CasePrediction


class CasePredictionRepository:
    def __init__(self, session):
        self.session = session

    def get_prediction_by_case_id(self, case_id: int) -> CasePrediction:
        return (
            self.session.query(CasePrediction)
            .filter(
                CasePrediction.visit_occurrence_id == case_id,
            )
            .one_or_none()
        )
