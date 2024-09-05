from flask import Blueprint, jsonify, request

from src import db
from src.answer.repository.answer_repository import AnswerRepository
from src.answer.service.answer_service import AnswerService
from src.common.model.ApiResponse import ApiResponse
from src.configration.repository.answer_config_repository import \
    AnswerConfigurationRepository
from src.task.repository.task_repository import TaskRepository
from src.user.utils.auth_utils import jwt_validation_required

answer_blueprint = Blueprint("answer", __name__)

answer_service = AnswerService(
    answer_repository=AnswerRepository(db.session),
    answer_config_repository=AnswerConfigurationRepository(db.session),
    task_repository=TaskRepository(db.session),
)


@answer_blueprint.route("/answer/<string:task_id>", methods=["POST"])
@jwt_validation_required()
def add_answer_response(task_id):
    data = request.get_json()

    answer_response = answer_service.add_answer_response(task_id, data)

    return jsonify(ApiResponse.success({"id": answer_response.id})), 200
