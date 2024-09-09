import random
from collections import defaultdict
from datetime import datetime
from operator import itemgetter

from src.cases.controller.response.case_summary import CaseSummary
from src.cases.model.case import Case, TreeNode
from src.cases.repository.concept_repository import ConceptRepository
from src.cases.repository.drug_exposure_repository import \
    DrugExposureRepository
from src.cases.repository.measurement_repository import MeasurementRepository
from src.cases.repository.observation_repository import ObservationRepository
from src.cases.repository.person_repository import PersonRepository
from src.cases.repository.visit_occurrence_repository import \
    VisitOccurrenceRepository
from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)
from src.common.repository.system_config_repository import \
    SystemConfigRepository
from src.task.repository.task_repository import TaskRepository
from src.task.task_manager import TaskManager
from src.user.repository.display_config_repository import \
    DisplayConfigRepository
from src.user.repository.user_repository import UserRepository
from src.user.utils.auth_utils import get_user_email_from_jwt


def group_by(source_list, key_selector):
    target_list = defaultdict(list)
    for item in source_list:
        target_list[key_selector(item)].append(item)
    return target_list


def get_value_of_rows(rows: list, get_func) -> str | None | list:
    if len(rows) == 1:
        return get_func(rows[0])
    result = []
    for row in rows:
        value = get_func(row)
        if value:
            result.append(value)
    return result


def is_leaf_node(config):
    return isinstance(config, list) | isinstance(config, int)


def get_age(person, visit_occurrence):
    return str(visit_occurrence.visit_start_date.year - person.year_of_birth)


def attach_style(display_configuration, case_details, important_infos):
    paths = display_configuration["path"].split(".")
    level = 0
    nodes = case_details
    while level < len(paths):
        found = False
        for node in nodes:
            if node.key == paths[level]:
                nodes = node.values
                level = level + 1
                found = True
                if level == len(paths):
                    node.style = display_configuration["style"]
                    if node.style.get("top") is not None:
                        important_infos.append(
                            {
                                "key": "ignore" if level == 2 else node.key,
                                "values": node.values,
                                "weight": node.style["top"],
                            }
                        )
                break
        if not found:
            break


def add_if_value_present(data, node):
    if node.values:
        data.append(node)


class CaseService:
    def __init__(
        self,
        visit_occurrence_repository: VisitOccurrenceRepository,
        concept_repository: ConceptRepository,
        measurement_repository: MeasurementRepository,
        observation_repository: ObservationRepository,
        person_repository: PersonRepository,
        drug_exposure_repository: DrugExposureRepository,
        configuration_repository: DisplayConfigRepository,
        system_config_repository: SystemConfigRepository,
        task_repository: TaskRepository,
        user_repository: UserRepository,
    ):
        self.user_repository = None
        self.person = None
        self.visit_occurrence_repository = visit_occurrence_repository
        self.concept_repository = concept_repository
        self.measurement_repository = measurement_repository
        self.observation_repository = observation_repository
        self.person_repository = person_repository
        self.drug_exposure_repository = drug_exposure_repository
        self.configuration_repository = configuration_repository
        self.system_config_repository = system_config_repository
        self.task_repository = task_repository
        self.user_repository = user_repository
        TaskManager.initialize(
            user_repository, task_repository, visit_occurrence_repository
        )

    def get_case_detail(self, case_id):
        page_config = self.get_page_configuration()
        title_resolvers = {
            "BACKGROUND": self.get_nodes_of_background,
            "PATIENT COMPLAINT": self.get_nodes_of_observation,
            "PHYSICAL EXAMINATION": self.get_nodes_of_measurement,
        }
        data: list[TreeNode] = []
        for key, title_config in page_config.items():
            add_if_value_present(
                data, TreeNode(key, title_resolvers[key](case_id, title_config))
            )
        return data

    def get_nodes_of_measurement(self, case_id, title_config):
        data: list[TreeNode] = []
        for key, title_concept_ids in title_config.items():
            section_name = self.get_concept_name(title_concept_ids[0])
            parent_measurements = self.measurement_repository.get_measurements(
                case_id, title_concept_ids
            )
            if parent_measurements:
                data.append(
                    TreeNode(
                        section_name,
                        get_value_of_rows(
                            parent_measurements, self.get_value_of_measurement
                        ),
                    )
                )
            else:
                children_measurements = (
                    self.measurement_repository.get_measurements_of_parents(
                        case_id, title_concept_ids
                    )
                )
                parent_node = TreeNode(section_name, [])
                measurements_by_concept = group_by(
                    children_measurements, lambda m: m.measurement_concept_id
                )
                for concept_id, rows in measurements_by_concept.items():
                    parent_node.add_node(
                        TreeNode(
                            self.get_concept_name(concept_id),
                            get_value_of_rows(rows, self.get_value_of_measurement),
                        )
                    )
                add_if_value_present(data, parent_node)
        return data

    def get_value_of_measurement(self, measurement) -> str | None:
        value = None
        if measurement.value_as_number:
            value = str(measurement.value_as_number)
        elif measurement.value_as_concept_id:
            value = self.get_concept_name(measurement.value_as_concept_id)
        elif measurement.unit_source_value:
            value = measurement.unit_source_value
        if value and measurement.unit_concept_id:
            value = value + " " + self.get_concept_name(measurement.unit_concept_id)
        if value and measurement.operator_concept_id:
            value = self.get_concept_name(measurement.operator_concept_id) + " " + value
        return value

    def get_nodes_of_observation(self, case_id, title_config):
        data: list[TreeNode] = []
        for key, concept_type_ids in title_config.items():
            parent_node = TreeNode(key, [])
            observations = self.observation_repository.get_observations_by_type(
                case_id, concept_type_ids
            )
            observations_by_concept = group_by(
                observations, lambda o: o.observation_concept_id
            )
            for concept_id, rows in observations_by_concept.items():
                parent_node.add_node(
                    TreeNode(
                        self.get_concept_name(concept_id),
                        get_value_of_rows(rows, self.get_value_of_observation),
                    )
                )
            add_if_value_present(data, parent_node)
        return data

    def get_value_of_observation(self, observation) -> str | None:
        value = None
        if observation.value_as_string:
            value = observation.value_as_string
        elif observation.value_as_number:
            value = str(observation.value_as_number)
        elif observation.value_as_concept_id:
            value = self.get_concept_name(observation.value_as_concept_id)
        elif observation.unit_source_value:
            value = observation.unit_source_value
        if value and observation.unit_concept_id:
            value = value + " " + self.get_concept_name(observation.unit_concept_id)
        if value and observation.qualifier_concept_id:
            value = (
                self.get_concept_name(observation.qualifier_concept_id) + " : " + value
            )
        return value

    def get_nodes_of_background(self, case_id, title_config):
        data: list[TreeNode] = [
            self.get_nodes_of_patient(case_id),
        ]
        for key, config in title_config.items():
            node = TreeNode(key, self.get_nodes_of_nested_fields(case_id, config))
            add_if_value_present(data, node)
        return data

    def get_nodes_of_patient(self, case_id):
        visit_occurrence = self.visit_occurrence_repository.get_visit_occurrence(
            case_id
        )
        person = self.person_repository.get_person(visit_occurrence.person_id)
        age = get_age(person, visit_occurrence)
        gender = self.get_concept_name(person.gender_concept_id)
        self.person = person
        return TreeNode(
            "Patient Demographics", [TreeNode("Age", age), TreeNode("Gender", gender)]
        )

    def get_nodes_of_nested_fields(self, case_id, config):
        if is_leaf_node(config):
            observations = self.observation_repository.get_observations_by_concept(
                case_id, config
            )
            return get_value_of_rows(observations, self.get_value_of_observation)
        data: list[TreeNode] = []
        for key, nested_config in config.items():
            node = TreeNode(
                key, self.get_nodes_of_nested_fields(case_id, nested_config)
            )
            add_if_value_present(data, node)
        return data

    def get_concept_name(self, concept_id):
        return self.concept_repository.get_concept(concept_id).concept_name

    def get_page_configuration(self):
        return self.system_config_repository.get_config_by_id("page_config").json_config

    def get_case_review(self, task_id):
        task = self.random_assign_display(task_id)

        current_user = get_user_email_from_jwt()
        if not task or task.user_email != current_user:
            raise BusinessException(BusinessExceptionEnum.NoAccessToCaseReview)

        case_details = self.get_case_detail(task.case_id)

        important_infos = []
        if task.path_config:
            for item in task.path_config:
                if item.get("style"):
                    attach_style(item, case_details, important_infos)

        important_infos.sort(key=itemgetter("weight"))
        sorted_important_infos = map(
            lambda e: TreeNode(e["key"], e["values"]), important_infos
        )

        return Case(
            self.person.person_source_value,
            str(task.case_id),
            case_details,
            list(sorted_important_infos),
        )

    def get_cases_by_user(self, user_email) -> list[CaseSummary]:
        task_manager = TaskManager.get_instance()
        task_result = task_manager.get_or_create_user_task(user_email)

        if not task_result.task:
            return []
        else:
            task = task_result.task

        cases_summary_list = []
        page_config = self.get_page_configuration()
        chief_complaint_concept_ids = page_config["PATIENT COMPLAINT"][
            "Chief Complaint"
        ]

        visit_occurrence = self.visit_occurrence_repository.get_visit_occurrence(
            task.case_id
        )

        person = self.person_repository.get_person(visit_occurrence.person_id)
        age = get_age(person, visit_occurrence)
        gender = self.get_concept_name(person.gender_concept_id)
        observations = self.observation_repository.get_observations_by_type(
            task.case_id, chief_complaint_concept_ids
        )
        patient_chief_complaint = []
        for obs in observations:
            concept_name = self.get_concept_name(obs.observation_concept_id)
            if concept_name and concept_name not in patient_chief_complaint:
                patient_chief_complaint.append(concept_name)

        case_summary = CaseSummary(
            task_id=task.id,
            case_id=task.case_id,
            age=age,
            gender=gender,
            patient_chief_complaint=", ".join(patient_chief_complaint),
        )
        cases_summary_list.append(case_summary)

        return cases_summary_list

    def random_assign_display(self, task_id):
        task = self.task_repository.get_task(task_id)
        if task is not None and task.path_config is None:
            all_display_configurations = (
                self.configuration_repository.get_all_configurations()
            )
            if all_display_configurations:
                chosen_display = random.choice(all_display_configurations)
                task.path_config = chosen_display.path_config
            else:
                task.path_config = []
            task.review_started_timestamp = datetime.utcnow()
        return task
