from src.answer.model.answer import Answer


class AnswerRepository:
    def __init__(self, session):
        self.session = session

    def add_answer(self, answer: Answer):
        self.session.add(answer)
        self.session.flush()
        return answer
