import re

import pytest

from src.cases.controller.response.case_summary import CaseSummary
from src.cases.model.case import Case
from src.cases.model.case import TreeNode
from src.cases.model.case_prediction import CasePrediction
from src.cases.repository.case_prediction_repository import CasePredictionRepository
from src.cases.repository.concept_repository import ConceptRepository
from src.cases.repository.drug_exposure_repository import \
    DrugExposureRepository
from src.cases.repository.measurement_repository import MeasurementRepository
from src.cases.repository.observation_repository import ObservationRepository
from src.cases.repository.person_repository import PersonRepository
from src.cases.repository.visit_occurrence_repository import \
    VisitOccurrenceRepository
from src.cases.service.case_service import (CaseService, add_if_value_present,
                                            attach_style, get_age,
                                            get_value_of_rows, group_by,
                                            is_leaf_node)
from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from src.common.model.system_config import SystemConfig
from src.common.repository.system_config_repository import \
    SystemConfigRepository
from src.task.model.task import Task
from src.task.repository.task_repository import TaskRepository
from src.user.model.display_config import DisplayConfig
from src.user.repository.display_config_repository import \
    DisplayConfigRepository
from src.task.task_manager import UserTaskResult
from tests.cases.case_fixture import (concept_fixture, measurement_fixture,
                                      observation_fixture, person_fixture,
                                      visit_occurrence_fixture)
from src.user.repository.user_repository import UserRepository


class TestGroupBy:
    def test_group_by(self):
        source_list = [
            {"concept_id": 1, "value": "row1"},
            {"concept_id": 1, "value": "row2"},
            {"concept_id": 2, "value": "row"},
        ]

        target_list = group_by(source_list, lambda item: item["concept_id"])

        assert target_list[1] == [
            {"concept_id": 1, "value": "row1"},
            {"concept_id": 1, "value": "row2"},
        ]
        assert target_list[2] == [{"concept_id": 2, "value": "row"}]


class TestGetValueOfRows:
    def test_get_str_when_one_row(self):
        rows = [{"value": "text"}]

        value_of_rows = get_value_of_rows(rows, lambda item: item["value"])

        assert value_of_rows == "text"

    def test_get_list_str_when_many_rows(self):
        rows = [{"value": "text"}, {"value": "text"}]

        value_of_rows = get_value_of_rows(rows, lambda item: item["value"])

        assert value_of_rows == ["text", "text"]


class TestIsLeafNode:
    def test_is_leaf_when_config_is_list(self):
        config = [123]

        assert is_leaf_node(config) is True

    def test_is_leaf_when_config_is_a_number(self):
        config = 123

        assert is_leaf_node(config) is True


class TestGetAge:
    def test_get_age(self):
        person = person_fixture()
        visit = visit_occurrence_fixture()

        assert get_age(person, visit) == "36"


class TestAddIfPresent:
    def test_add_if_value_present(self):
        node_with_values = TreeNode("key", ["value"])
        node_without_values = TreeNode("key", None)

        data = []
        add_if_value_present(data, node_with_values)
        assert len(data) == 1

        data = []
        add_if_value_present(data, node_without_values)
        assert len(data) == 0


class TestAttachStyle:
    def test_attach_style_to_configuration_when_path_found_in_first_layer(self):
        case_details = [
            TreeNode(
                "levelOne", [TreeNode("levelTwo", [TreeNode("levelTree", "text")])]
            ),
            TreeNode("another", "xxx"),
        ]
        display_config = {"path": "levelOne", "style": {'collapse': True}}

        attach_style(display_config, case_details, [])

        assert case_details[0].style == {'collapse': True}

    def test_attach_style_to_configuration_when_path_found_in_nested_layer(self):
        case_details = [
            TreeNode(
                "levelOne", [TreeNode("levelTwo", [TreeNode("levelTree", "text")])]
            ),
            TreeNode("another", "xxx"),
        ]
        display_config = {"path": "levelOne.levelTwo.levelTree", "style": {'collapse': True}}

        attach_style(display_config, case_details, [])

        assert case_details[0].values[0].values[0].style == {'collapse': True}

    def test_not_attach_style_to_configuration_when_path_not_found(self):
        case_details = [
            TreeNode(
                "levelOne", [TreeNode("levelTwo", [TreeNode("levelTree", "text")])]
            ),
        ]
        display_config = {"path": "levelOne.levelTwo.xxx", "style": {'collapse': True}}

        attach_style(display_config, case_details, [])

        assert case_details[0].style is None
        assert case_details[0].values[0].style is None
        assert case_details[0].values[0].values[0].style is None

    def test_append_import_info_when_config_top_area_at_second_layer(self):
        case_details = [
            TreeNode(
                "levelOne", [TreeNode("levelTwo", [TreeNode("levelTree", "text")])]
            ),
            TreeNode("another", "xxx"),
        ]
        display_config = {"path": "levelOne.levelTwo", "style": {'top': 1}}
        important_infos = []

        attach_style(display_config, case_details, important_infos)

        assert important_infos == [{
            'key': 'ignore',
            'values': [TreeNode("levelTree", "text")],
            'weight': 1
        }]

    def test_append_import_info_when_config_top_area_at_third_layer(self):
        case_details = [
            TreeNode(
                "levelOne", [TreeNode("levelTwo", [TreeNode("levelTree", "text")])]
            ),
            TreeNode("another", "xxx"),
        ]
        display_config = {"path": "levelOne.levelTwo.levelTree", "style": {'top': 1}}
        important_infos = []

        attach_style(display_config, case_details, important_infos)

        assert important_infos == [{
            'key': 'levelTree',
            'values': 'text',
            'weight': 1
        }]


def mock_repos(mocker):
    visit_occurrence_repository = mocker.Mock(VisitOccurrenceRepository)
    measurement_repository = mocker.Mock(MeasurementRepository)
    observation_repository = mocker.Mock(ObservationRepository)
    person_repository = mocker.Mock(PersonRepository)
    drug_exposure_repository = mocker.Mock(DrugExposureRepository)
    configuration_repository = mocker.Mock(DisplayConfigRepository)
    concept_repository = mocker.Mock(ConceptRepository)
    system_config_repository = mocker.Mock(SystemConfigRepository)
    task_repository = mocker.Mock(TaskRepository)
    user_repository = mocker.Mock(UserRepository)
    case_prediction_repository = mocker.Mock(CasePredictionRepository)
    mocker.patch('src.cases.service.case_service.get_user_email_from_jwt', return_value='goodbye@sunwukong.com')

    visit_occurrence_repository.get_visit_occurrence.return_value = (
        visit_occurrence_fixture()
    )
    person_repository.get_person.return_value = person_fixture()
    concept_repository.get_concept.return_value = concept_fixture()
    observation_repository.get_observations_by_concept.return_value = []
    observation_repository.get_observations_by_type.return_value = []
    measurement_repository.get_measurements.return_value = []
    measurement_repository.get_measurements_of_parents.return_value = []
    case_prediction_repository.get_prediction_by_case_id.return_value = None
    system_config_repository.get_config_by_id.return_value = SystemConfig(
        id="page_config",
        json_config={
            "BACKGROUND": {
                "Family History": [4167217],
                "Social History": {
                    "Smoke": [4041306],
                    "Alcohol": [4238768],
                    "Drug use": [4038710],
                    "Sexual behavior": [4283657, 4314454],
                },
            },
            "PATIENT COMPLAINT": {
                "Chief Complaint": [38000282],
                "Current Symptoms": [4034855],
            },
            "PHYSICAL EXAMINATION": {
                "Physical Characteristics": [4086988],
                "Vital Signs": [4263222],
                "Cardiovascular": [36717771],
                "Ophthalmology": [4080843],
                "Respiratory": [4090320],
                "Abdominal": [4152368],
                "Neurological": [4154954],
            },
        },
    )
    return (
        concept_repository,
        configuration_repository,
        drug_exposure_repository,
        measurement_repository,
        observation_repository,
        person_repository,
        visit_occurrence_repository,
        system_config_repository,
        task_repository,
        user_repository,
        case_prediction_repository
    )


def mock_concept_func(concept_id):
    mock_data = {
        4086988: "Physical Characteristics",
        4263222: "Vital Signs",
        36717771: "Cardiovascular",
        4080843: "Ophthalmology",
        4090320: "Abdominal",
        4152368: "Physical Characteristics",
        4154954: "Neurological",
    }
    if mock_data.get(concept_id):
        return concept_fixture(concept_id, mock_data[concept_id])
    return concept_fixture()


class TestGetCaseDetail:
    def test_get_patient_in_background(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        # When
        detail = case_service.get_case_detail(1)

        # Then
        assert detail == [
            TreeNode(
                "BACKGROUND",
                [
                    TreeNode(
                        "Patient Demographics",
                        [TreeNode("Age", "36"), TreeNode("Gender", "test")],
                    )
                ],
            )
        ]

    def test_get_nested_fields_in_background(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        observation_repository.get_observations_by_concept.return_value = [
            observation_fixture(concept_id=1, value_as_string="value")
        ]

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        # When
        detail = case_service.get_case_detail(1)

        # Then
        background = detail[0]
        assert background.values[1].key == "Family History"
        assert background.values[2].key == "Social History"
        assert background.values[2].values[0].key == "Smoke"
        assert background.values[2].values[1].key == "Alcohol"
        assert background.values[2].values[2].key == "Drug use"
        assert background.values[2].values[3].key == "Sexual behavior"

    def test_get_node_in_patient_complaint(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        observation_repository.get_observations_by_type.return_value = [
            observation_fixture(concept_id=1, value_as_string="value")
        ]

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        # When
        detail = case_service.get_case_detail(1)

        # Then
        patient_complaint = detail[1]
        assert patient_complaint.key == "PATIENT COMPLAINT"
        assert patient_complaint.values[0].key == "Chief Complaint"
        assert patient_complaint.values[1].key == "Current Symptoms"

    def test_get_physical_examination_when_found_by_concept_itself(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        concept_repository.get_concept.side_effect = mock_concept_func
        measurement_repository.get_measurements.return_value = [
            measurement_fixture(concept_id=1, value_as_number=1)
        ]

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        # When
        detail = case_service.get_case_detail(1)

        # Then
        physical_examination = detail[1]
        assert physical_examination.key == "PHYSICAL EXAMINATION"
        assert physical_examination.values[0].key == "Physical Characteristics"
        assert isinstance(physical_examination.values[0].values, str)
        assert physical_examination.values[1].key == "Vital Signs"
        assert isinstance(physical_examination.values[1].values, str)
        assert physical_examination.values[2].key == "Cardiovascular"
        assert isinstance(physical_examination.values[2].values, str)
        assert physical_examination.values[3].key == "Ophthalmology"
        assert isinstance(physical_examination.values[3].values, str)
        assert physical_examination.values[4].key == "Abdominal"
        assert isinstance(physical_examination.values[4].values, str)
        assert physical_examination.values[5].key == "Physical Characteristics"
        assert isinstance(physical_examination.values[5].values, str)
        assert physical_examination.values[6].key == "Neurological"
        assert isinstance(physical_examination.values[6].values, str)

    def test_get_physical_examination_when_found_by_concept_relationship(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        concept_repository.get_concept.side_effect = mock_concept_func
        measurement_repository.get_measurements_of_parents.return_value = [
            measurement_fixture(concept_id=1, value_as_number=1)
        ]

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        # When
        detail = case_service.get_case_detail(1)

        # Then
        physical_examination = detail[1]
        assert physical_examination.key == "PHYSICAL EXAMINATION"
        assert physical_examination.values[0].key == "Physical Characteristics"
        assert physical_examination.values[0].values == [TreeNode("test", "1")]
        assert physical_examination.values[1].key == "Vital Signs"
        assert physical_examination.values[1].values == [TreeNode("test", "1")]
        assert physical_examination.values[2].key == "Cardiovascular"
        assert physical_examination.values[2].values == [TreeNode("test", "1")]
        assert physical_examination.values[3].key == "Ophthalmology"
        assert physical_examination.values[3].values == [TreeNode("test", "1")]
        assert physical_examination.values[4].key == "Abdominal"
        assert physical_examination.values[4].values == [TreeNode("test", "1")]
        assert physical_examination.values[5].key == "Physical Characteristics"
        assert physical_examination.values[5].values == [TreeNode("test", "1")]
        assert physical_examination.values[6].key == "Neurological"
        assert physical_examination.values[6].values == [TreeNode("test", "1")]

    def test_get_case_prediction(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        case_prediction_repository.get_prediction_by_case_id.return_value = None
        assert case_service.get_case_prediction(1) is None

        case_prediction_repository.get_prediction_by_case_id.return_value = CasePrediction(1, "case prediction free text")
        assert case_service.get_case_prediction(1) is not None


class TestGetValue:
    def test_get_value_of_observation_with_string(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )
        observation_family_history_with_string = observation_fixture(
            concept_id=4167217,
            value_as_string="family history",
            observation_type_concept_id=0,
            observation_id=1,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_observation(
            observation_family_history_with_string
        )

        # then
        assert value == "family history"

    def test_get_value_of_observation_with_number(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )
        observation_family_history_with_number = observation_fixture(
            concept_id=4167217,
            value_as_number=10,
            observation_type_concept_id=0,
            observation_id=2,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_observation(
            observation_family_history_with_number
        )

        # then
        assert value == "10"

    def test_get_value_of_observation_with_concept(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )
        observation_family_history_with_concept = observation_fixture(
            concept_id=4167217,
            value_as_concept_id=31,
            observation_type_concept_id=0,
            observation_id=3,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_observation(
            observation_family_history_with_concept
        )

        # then
        assert value == "test"

    def test_get_value_of_observation_with_unit(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )
        observation_family_history_with_unit = observation_fixture(
            concept_id=4167217,
            value_as_number=10,
            unit_concept_id=32,
            observation_type_concept_id=0,
            observation_id=4,
            person_id=1,
            visit_id=1,
        )

        # When
        value = case_service.get_value_of_observation(
            observation_family_history_with_unit
        )

        # then
        assert value == "10 test"

    def test_get_value_of_observation_with_qualifier(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )
        observation_family_history_with_qualifier = observation_fixture(
            concept_id=4167217,
            value_as_number=10,
            qualifier_concept_id=33,
            observation_type_concept_id=0,
            observation_id=5,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_observation(
            observation_family_history_with_qualifier
        )

        # then
        assert value == "test : 10"

    def test_get_value_of_observation_with_unit_source(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )
        observation_family_history_with_qualifier = observation_fixture(
            concept_id=4167217,
            unit_source_value='10',
            unit_concept_id=32,
            observation_type_concept_id=0,
            observation_id=5,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_observation(
            observation_family_history_with_qualifier
        )

        # then
        assert value == "10 test"

    def test_get_value_of_measurement_with_number(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )
        measurement_vital_signs_pulse_rate_with_number = measurement_fixture(
            concept_id=40,
            value_as_number=10,
            operator_concept_id=41,
            unit_concept_id=42,
            measurement_id=1,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_measurement(
            measurement_vital_signs_pulse_rate_with_number
        )

        # then
        assert value == "test 10 test"

    def test_get_value_of_measurement_with_concept(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )
        measurement_vital_signs_bp_with_concept = measurement_fixture(
            concept_id=43,
            value_as_concept_id=44,
            operator_concept_id=41,
            unit_concept_id=42,
            measurement_id=2,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_measurement(
            measurement_vital_signs_bp_with_concept
        )

        # then
        assert value == "test test test"

    def test_get_value_of_measurement_with_unit_source_value(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )
        measurement_vital_signs_bp_with_concept = measurement_fixture(
            concept_id=43,
            unit_source_value='44',
            operator_concept_id=41,
            unit_concept_id=42,
            measurement_id=2,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_measurement(
            measurement_vital_signs_bp_with_concept
        )

        # then
        assert value == "test 44 test"


class TestGetCaseReview:
    def test_get_case_review_when_assigned_display_before(self, mocker):
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)
        task_repository.get_task.return_value = Task(id='101', case_id=1, user_email='goodbye@sunwukong.com', completed=False, path_config=[
            {
                "path": "BACKGROUND.Patient Demographics",
                "style": {"collapse": True},
            },
            {"path": "no path", "style": {"collapse": True}},
        ])
        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        case_review = case_service.get_case_review(1)

        assert case_review == Case(
            personName='sunwukong',
            caseNumber='1',
            details=[
                TreeNode(
                    "BACKGROUND",
                    [
                        TreeNode(
                            "Patient Demographics",
                            [TreeNode("Age", "36"), TreeNode("Gender", "test")],
                            {"collapse": True},
                        )
                    ],
                )
            ],
            importantInfos=[]
        )

    def test_get_case_review_without_path_config_when_no_display_uploaded(self, mocker):
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)
        task_repository.get_task.return_value = Task(id='101', case_id=1, user_email='goodbye@sunwukong.com', completed=False)
        configuration_repository.get_all_configurations.return_value = []
        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        case_review = case_service.get_case_review(1)

        assert case_review == Case(
            personName='sunwukong',
            caseNumber='1',
            details=[
                TreeNode(
                    "BACKGROUND",
                    [
                        TreeNode(
                            "Patient Demographics",
                            [TreeNode("Age", "36"), TreeNode("Gender", "test")],
                        )
                    ],
                )
            ],
            importantInfos=[]
        )

    def test_get_case_review_when_random_assign_display(self, mocker):
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)
        task_repository.get_task.return_value = Task(id='101', case_id=1, user_email='goodbye@sunwukong.com', completed=False)
        configuration_repository.get_all_configurations.return_value = [DisplayConfig(
            path_config=[
                {
                    "path": "BACKGROUND.Patient Demographics",
                    "style": {"collapse": True},
                },
                {"path": "no path", "style": {"collapse": True}},
            ],
            id=1
        )]
        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        case_review = case_service.get_case_review(1)

        assert case_review == Case(
            personName='sunwukong',
            caseNumber='1',
            details=[
                TreeNode(
                    "BACKGROUND",
                    [
                        TreeNode(
                            "Patient Demographics",
                            [TreeNode("Age", "36"), TreeNode("Gender", "test")],
                            {"collapse": True},
                        )
                    ],
                )
            ],
            importantInfos=[]
        )

    def test_throw_error_when_task_not_found(self, mocker):
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)
        task_repository.get_task.return_value = None
        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        with pytest.raises(BusinessException, match=re.compile(BusinessExceptionEnum.NoAccessToCaseReview.name)):
            case_service.get_case_review(1)

    def test_get_case_review_when_path_config_top_area(self, mocker):
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)
        task_repository.get_task.return_value = Task(id='101', case_id=1, user_email='goodbye@sunwukong.com', completed=False, path_config=[
            {
                "path": "BACKGROUND.Patient Demographics",
                "style": {"collapse": True, "top": 3},
            },
            {
                "path": "BACKGROUND.Patient Demographics.Age",
                "style": {"top": 2},
            },
            {
                "path": "BACKGROUND.Patient Demographics.Gender",
                "style": {"top": 0},
            },
        ])
        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        case_review = case_service.get_case_review(1)

        assert case_review == Case(
            personName='sunwukong',
            caseNumber='1',
            details=[
                TreeNode(
                    "BACKGROUND",
                    [
                        TreeNode(
                            "Patient Demographics",
                            [TreeNode("Age", "36", {"top": 2}), TreeNode("Gender", "test", {"top": 0})],
                            {"collapse": True, "top": 3},
                        )
                    ],
                )
            ],
            importantInfos=[
                TreeNode("Gender", "test"),
                TreeNode("Age", "36"),
                TreeNode(
                    "ignore",
                    [TreeNode("Age", "36", {"top": 2}), TreeNode("Gender", "test", {"top": 0})],
                )
            ]
        )

    def test_get_case_review_when_config_ai_prediction(self, mocker):
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)
        task_repository.get_task.return_value = Task(id='101', case_id=1, user_email='goodbye@sunwukong.com', completed=False, path_config=[
            {
                "path": "BACKGROUND.Patient Demographics",
                "style": {"collapse": True, "top": 3},
            },
            {
                "path": "BACKGROUND.Patient Demographics.Age",
                "style": {"top": 2},
            },
            {
                "path": "BACKGROUND.Patient Demographics.Gender",
                "style": {"top": 0},
            },
            {
                "path": "AI Prediction",
                "style": {"top": 1},
            },
        ])
        case_prediction_repository.get_prediction_by_case_id.return_value = CasePrediction(1, "case prediction free text")
        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        case_review = case_service.get_case_review(1)

        assert case_review == Case(
            personName='sunwukong',
            caseNumber='1',
            details=[
                TreeNode(
                    "BACKGROUND",
                    [
                        TreeNode(
                            "Patient Demographics",
                            [TreeNode("Age", "36", {"top": 2}), TreeNode("Gender", "test", {"top": 0})],
                            {"collapse": True, "top": 3},
                        )
                    ],
                )
            ],
            importantInfos=[
                TreeNode("Gender", "test"),
                TreeNode("ignore", "case prediction free text"),
                TreeNode("Age", "36"),
                TreeNode(
                    "ignore",
                    [TreeNode("Age", "36", {"top": 2}), TreeNode("Gender", "test", {"top": 0})],
                )
            ]
        )


class TestGetCaseSummary:
    def create_side_effect(self, concept_mapping):
        def concept_side_effect(concept_id):
            if concept_id in concept_mapping:
                return concept_fixture(concept_id=concept_id, concept_name=concept_mapping[concept_id])
            return concept_fixture()

        return concept_side_effect

    def create_observation_side_effect(self, observation_mapping):
        def observation_side_effect(case_id, concept_ids):
            results = []
            for concept_id in concept_ids:
                key = (case_id, int(concept_id))
                if key in observation_mapping:
                    results.extend(observation_mapping[key])
            return results

        return observation_side_effect

    def test_get_cases_by_user_no_cases(self, mocker):
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)
        task_repository.get_task_by_user.return_value = []
        visit_occurrence_repository.get_visit_occurrence.return_value = None
        person_repository.get_person.return_value = None
        observation_repository.get_observations_by_type.return_value = []
        mocker.patch('src.cases.service.case_service.TaskManager.get_or_create_user_task', return_value=UserTaskResult(task=None, is_new_assignment=False))

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )

        assert case_service.get_cases_by_user("user@example.com") == []

    def test_get_cases_by_user_single_case(self, mocker):
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)

        concept_mapping = {
            2: 'Male',
            3: 'Headache'
        }
        concept_repository.get_concept.side_effect = self.create_side_effect(concept_mapping)

        visit_occurrence_repository.get_visit_occurrence.return_value = mocker.Mock(person_id=1)
        person_repository.get_person.return_value = mocker.Mock(year_of_birth=1984, gender_concept_id=2)
        observation_mapping = {
            (1, 38000282): [observation_fixture(concept_id=3, observation_type_concept_id=38000282, visit_id=1)],
        }

        observation_repository.get_observations_by_type.side_effect = self.create_observation_side_effect(
            observation_mapping)
        mocker.patch('src.cases.service.case_service.get_age', return_value="36")
        mocker.patch('src.cases.service.case_service.TaskManager.get_or_create_user_task', return_value=UserTaskResult(
            task= Task(id='101', case_id=1, user_email='goodbye@sunwukong.com', completed=False), is_new_assignment=False))

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )
        result = case_service.get_cases_by_user("user@example.com")
        expected = [CaseSummary(task_id="101", case_id=1, age="36", gender='Male', patient_chief_complaint='Headache')]

        assert len(result) == 1
        assert result[0].__dict__ == expected[0].__dict__

    def test_get_case_by_user_with_multiple_chief_complaint(self, mocker):
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
            system_config_repository,
            task_repository,
            user_repository,
            case_prediction_repository
        ) = mock_repos(mocker)
        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
            system_config_repository=system_config_repository,
            task_repository=task_repository,
            user_repository=user_repository,
            case_prediction_repository=case_prediction_repository
        )
        # Setup complex observation data
        observation_mapping = {
            (1, 38000282): [observation_fixture(concept_id=3, observation_type_concept_id=38000282, visit_id=1),
                            observation_fixture(concept_id=4, observation_type_concept_id=38000282, visit_id=1)]
        }
        observation_repository.get_observations_by_type.side_effect = self.create_observation_side_effect(
            observation_mapping)
        case_service.task_repository.get_task_by_user.return_value = Task(id='101', case_id=1, user_email='goodbye@sunwukong.com', completed=False)
        case_service.visit_occurrence_repository.get_visit_occurrence.return_value = mocker.Mock(person_id=1)
        case_service.person_repository.get_person.return_value = mocker.Mock(year_of_birth=1984, gender_concept_id=1)
        concept_mapping = {
            1: 'Male',
            2: 'Female',
            3: 'Cough',
            4: 'Fever'
        }
        concept_repository.get_concept.side_effect = self.create_side_effect(concept_mapping)

        mocker.patch('src.cases.service.case_service.get_age', return_value="36")
        mocker.patch('src.cases.service.case_service.TaskManager.get_or_create_user_task', return_value=UserTaskResult(
            task=Task(id='101', case_id=1, user_email='goodbye@sunwukong.com', completed=False), is_new_assignment=False))

        result = case_service.get_cases_by_user("user@example.com")
        expected_patient_complaint = 'Cough, Fever'

        assert len(result) == 1
        assert result[0].patient_chief_complaint == expected_patient_complaint
