from datetime import date, timedelta
import random

from src.cases.model.clinical_data.person.drug_exposure import DrugExposure
from src.cases.model.clinical_data.person.measurement import Measurement
from src.cases.model.clinical_data.person.observation import Observation
from src.cases.model.clinical_data.person.person import Person
from src.cases.model.clinical_data.person.visit_occurrence import VisitOccurrence
from src.cases.model.vocabularies.concept import Concept
from src.cases.model.vocabularies.concept_relationship import ConceptRelationship
from src.cases.model.vocabularies.relationship import Relationship


def concept_fixture(concept_id=1, concept_name="test"):
    return Concept(
        concept_id=concept_id,
        concept_name=concept_name,
        domain_id="1",
        vocabulary_id="1",
        concept_class_id="1",
        concept_code="code",
        valid_start_date=date(2024, 1, 1),
        valid_end_date=date(2024, 1, 1),
    )


def concept_relationship_fixture(concept_id_1, concept_id_2, relationship_id):
    return ConceptRelationship(
        concept_id_1=concept_id_1,
        concept_id_2=concept_id_2,
        relationship_id=relationship_id,
        valid_start_date=date(2024, 1, 1),
        valid_end_date=date(2024, 1, 1),
    )


def relationship_fixture(relationship_concept_id, relationship_id="Subsumes"):
    return Relationship(
        relationship_id=relationship_id,
        relationship_name=relationship_id,
        is_hierarchical="1",
        defines_ancestry="1",
        reverse_relationship_id="Is a",
        relationship_concept_id=relationship_concept_id,
    )


def person_fixture(person_id=1, gender_concept_id=2, race_concept_id=3):
    return Person(
        person_id=person_id,
        gender_concept_id=gender_concept_id,
        year_of_birth=1988,
        month_of_birth=1,
        day_of_birth=1,
        race_concept_id=race_concept_id,
        ethnicity_concept_id=12,
        person_source_value='sunwukong'
    )


def visit_occurrence_fixture(
        visit_occurrence_id=1, person_id=1, visit_concept_id=10, visit_type_concept_id=11
):
    return VisitOccurrence(
        visit_occurrence_id=visit_occurrence_id,
        person_id=person_id,
        visit_concept_id=visit_concept_id,
        visit_start_date=date(2024, 1, 1),
        visit_end_date=date(2024, 1, 1),
        visit_type_concept_id=visit_type_concept_id,
    )


def drug_fixture(concept_id, drug_exposure_id=1, person_id=1, visit_id=1):
    return DrugExposure(
        drug_exposure_id=drug_exposure_id,
        person_id=person_id,
        drug_concept_id=concept_id,
        drug_exposure_start_date=date(2024, 1, 1),
        drug_exposure_end_date=date(2024, 1, 1),
        drug_type_concept_id=0,
        quantity=10,
        days_supply=100,
        visit_occurrence_id=visit_id,
    )


def observation_fixture(
        concept_id,
        value_as_string=None,
        value_as_number=None,
        value_as_concept_id=None,
        qualifier_concept_id=None,
        unit_concept_id=None,
        unit_source_value=None,
        observation_type_concept_id=0,
        observation_id=1,
        person_id=1,
        visit_id=1,
):
    return Observation(
        observation_id=observation_id,
        person_id=person_id,
        observation_concept_id=concept_id,
        observation_date=date(2024, 1, 1),
        observation_type_concept_id=observation_type_concept_id,
        value_as_number=value_as_number,
        value_as_string=value_as_string,
        value_as_concept_id=value_as_concept_id,
        qualifier_concept_id=qualifier_concept_id,
        unit_concept_id=unit_concept_id,
        unit_source_value=unit_source_value,
        visit_occurrence_id=visit_id,
    )


def measurement_fixture(
        concept_id,
        operator_concept_id=None,
        value_as_number=None,
        value_as_concept_id=None,
        unit_concept_id=None,
        unit_source_value=None,
        measurement_id=1,
        person_id=1,
        visit_id=1,
):
    return Measurement(
        measurement_id=measurement_id,
        person_id=person_id,
        measurement_concept_id=concept_id,
        measurement_date=date(2024, 1, 1),
        measurement_type_concept_id=0,
        operator_concept_id=operator_concept_id,
        value_as_number=value_as_number,
        value_as_concept_id=value_as_concept_id,
        unit_concept_id=unit_concept_id,
        unit_source_value=unit_source_value,
        visit_occurrence_id=visit_id,
    )


def generate_random_person(case_num):
    return Person(
        person_id=case_num + 1,
        gender_concept_id=random.choice([8507, 8532]),
        year_of_birth=random.randint(1940, 2010),
        month_of_birth=random.randint(1, 12),
        day_of_birth=random.randint(1, 28),
        race_concept_id=random.randint(1, 5),
        ethnicity_concept_id=random.randint(1, 3),
        person_source_value=f'person_{case_num + 1}'
    )


def generate_random_visit(person_id):
    start_date = date(2023, 1, 1) + timedelta(days=random.randint(0, 365))
    end_date = start_date + timedelta(days=random.randint(1, 30))
    return VisitOccurrence(
        visit_occurrence_id=random.randint(1000, 9999),
        person_id=person_id,
        visit_concept_id=random.choice([9201, 9202, 9203]),
        visit_start_date=start_date,
        visit_end_date=end_date,
        visit_type_concept_id=random.randint(1, 5)
    )


def generate_random_drugs(session, person_id, visit_id):
    for _ in range(random.randint(1, 5)):
        drug = drug_fixture(
            concept_id=random.randint(1000, 2000),
            drug_exposure_id=random.randint(10000, 99999),
            person_id=person_id,
            visit_id=visit_id
        )
        session.add(drug)


def generate_random_observations(session, person_id, visit_id):
    for _ in range(random.randint(1, 10)):
        observation = observation_fixture(
            concept_id=random.randint(3000, 4000),
            value_as_string=random.choice([None, "Random Observation"]),
            value_as_number=random.choice([None, random.uniform(0, 100)]),
            value_as_concept_id=random.choice([None, random.randint(1, 100)]),
            observation_id=random.randint(100000, 999999),
            person_id=person_id,
            visit_id=visit_id
        )
        session.add(observation)


def generate_random_measurements(session, person_id, visit_id):
    for _ in range(random.randint(1, 8)):
        measurement = measurement_fixture(
            concept_id=random.randint(5000, 6000),
            value_as_number=random.uniform(0, 200),
            unit_concept_id=random.randint(1, 10),
            measurement_id=random.randint(1000000, 9999999),
            person_id=person_id,
            visit_id=visit_id
        )
        session.add(measurement)


def generate_single_case(session):
    person = person_fixture()
    concept_of_person_gender = concept_fixture(person.gender_concept_id, "M")
    concept_of_person_race = concept_fixture(person.race_concept_id, "race")

    visit = visit_occurrence_fixture(person_id=person.person_id)
    concept_of_visit = concept_fixture(visit.visit_concept_id, "visit")
    concept_of_visit_type = concept_fixture(visit.visit_type_concept_id, "visit_type")

    drug_1 = drug_fixture(
        drug_exposure_id=1,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
        concept_id=20,
    )
    drug_2 = drug_fixture(
        drug_exposure_id=2,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
        concept_id=21,
    )
    concept_of_drug_1 = concept_fixture(drug_1.drug_concept_id, "drug_1")
    concept_of_drug_2 = concept_fixture(drug_2.drug_concept_id, "drug_2")

    observation_family_history_with_string = observation_fixture(
        concept_id=4167217,
        value_as_string="family history",
        observation_type_concept_id=0,
        observation_id=1,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
    )
    observation_family_history_with_number = observation_fixture(
        concept_id=4167217,
        value_as_number=10,
        observation_type_concept_id=0,
        observation_id=2,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
    )
    observation_family_history_with_concept = observation_fixture(
        concept_id=4167217,
        value_as_concept_id=31,
        observation_type_concept_id=0,
        observation_id=3,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
    )
    observation_family_history_with_unit = observation_fixture(
        concept_id=4167217,
        value_as_number=10,
        unit_concept_id=32,
        observation_type_concept_id=0,
        observation_id=4,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
    )
    observation_family_history_with_qualifier = observation_fixture(
        concept_id=4167217,
        value_as_number=10,
        qualifier_concept_id=33,
        observation_type_concept_id=0,
        observation_id=5,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
    )
    concept_of_observation_family_history = concept_fixture(4167217, "family history")
    concept_of_observation_value = concept_fixture(
        observation_family_history_with_concept.value_as_concept_id, "value"
    )
    concept_of_observation_unit = concept_fixture(
        observation_family_history_with_unit.unit_concept_id, "per day"
    )
    concept_of_observation_qualifier = concept_fixture(
        observation_family_history_with_qualifier.qualifier_concept_id, "qualifier"
    )

    observation_social_history_smoke = observation_fixture(
        concept_id=4041306,
        value_as_string="nosmoke",
        observation_type_concept_id=0,
        observation_id=6,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
    )
    concept_of_observation_social_history_smoke = concept_fixture(4041306, "Smoke")

    observation_chief_complaint = observation_fixture(
        concept_id=36,
        value_as_string="duration",
        observation_type_concept_id=38000282,
        observation_id=7,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
    )
    concept_of_observation_type_chief_complaint = concept_fixture(
        38000282, "Chief complaint"
    )
    concept_of_observation_complaint = concept_fixture(
        observation_chief_complaint.observation_concept_id, "Nested of Chief complaint"
    )

    observation_current_symptom_1 = observation_fixture(
        concept_id=34,
        value_as_string="duration",
        observation_type_concept_id=4034855,
        observation_id=8,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
    )
    observation_current_symptom_2 = observation_fixture(
        concept_id=35,
        value_as_string="duration",
        observation_type_concept_id=4034855,
        observation_id=9,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
    )
    concept_of_observation_type_current_symptom = concept_fixture(
        4034855, "Current symptoms"
    )
    concept_of_observation_symptom_1 = concept_fixture(
        observation_current_symptom_1.observation_concept_id, "1 of Current symptoms"
    )
    concept_of_observation_symptom_2 = concept_fixture(
        observation_current_symptom_2.observation_concept_id, "2 of Current symptoms"
    )

    measurement_vital_signs_pulse_rate_with_number = measurement_fixture(
        concept_id=40,
        value_as_number=10,
        operator_concept_id=41,
        unit_concept_id=42,
        measurement_id=1,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
    )
    measurement_vital_signs_bp_with_concept = measurement_fixture(
        concept_id=43,
        value_as_concept_id=44,
        operator_concept_id=41,
        unit_concept_id=42,
        measurement_id=2,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
    )
    concept_of_measurement_pulse_rate = concept_fixture(
        measurement_vital_signs_pulse_rate_with_number.measurement_concept_id,
        "Pulse rate",
    )
    concept_of_measurement_bp = concept_fixture(
        measurement_vital_signs_bp_with_concept.measurement_concept_id, "BP"
    )
    concept_of_measurement_vital_signs = concept_fixture(4263222, "Vital signs")
    concept_of_measurement_unit = concept_fixture(
        measurement_vital_signs_pulse_rate_with_number.unit_concept_id, "unit"
    )
    concept_of_measurement_operator = concept_fixture(
        measurement_vital_signs_pulse_rate_with_number.operator_concept_id, "operator"
    )
    concept_of_measurement_value = concept_fixture(
        measurement_vital_signs_bp_with_concept.value_as_concept_id, "value"
    )
    relationship = relationship_fixture(relationship_concept_id=50)
    concept_of_relationship = concept_fixture(
        relationship.relationship_concept_id, "Relation"
    )
    concept_relationship_pulse_to_vital = concept_relationship_fixture(
        concept_id_1=concept_of_measurement_vital_signs.concept_id,
        concept_id_2=concept_of_measurement_pulse_rate.concept_id,
        relationship_id=relationship.relationship_id,
    )
    concept_relationship_bp_to_vital = concept_relationship_fixture(
        concept_id_1=concept_of_measurement_vital_signs.concept_id,
        concept_id_2=concept_of_measurement_bp.concept_id,
        relationship_id=relationship.relationship_id,
    )

    measurement_abdominal = measurement_fixture(
        concept_id=4152368,
        value_as_number=10,
        measurement_id=3,
        person_id=person.person_id,
        visit_id=visit.visit_occurrence_id,
    )
    concept_of_measurement_abdominal = concept_fixture(
        measurement_abdominal.measurement_concept_id, "Abdominal"
    )

    session.add_all(
        (
            concept_of_person_gender,
            concept_of_person_race,
            concept_of_visit,
            concept_of_visit_type,
            concept_of_drug_1,
            concept_of_drug_2,
            concept_of_observation_family_history,
            concept_of_observation_value,
            concept_of_observation_unit,
            concept_of_observation_qualifier,
            concept_of_observation_social_history_smoke,
            concept_of_observation_type_chief_complaint,
            concept_of_observation_complaint,
            concept_of_observation_type_current_symptom,
            concept_of_observation_symptom_1,
            concept_of_observation_symptom_2,
            concept_of_measurement_pulse_rate,
            concept_of_measurement_bp,
            concept_of_measurement_vital_signs,
            concept_of_measurement_unit,
            concept_of_measurement_operator,
            concept_of_measurement_value,
            concept_of_relationship,
            concept_of_measurement_abdominal,
        )
    )
    session.flush()

    session.add(relationship)
    session.flush()

    session.add_all(
        (concept_relationship_pulse_to_vital, concept_relationship_bp_to_vital)
    )
    session.flush()

    session.add(person)
    session.add(visit)
    session.flush()

    session.add_all((drug_1, drug_2))
    session.add_all(
        (
            observation_family_history_with_string,
            observation_family_history_with_number,
            observation_family_history_with_concept,
            observation_family_history_with_unit,
            observation_family_history_with_qualifier,
            observation_social_history_smoke,
            observation_chief_complaint,
            observation_current_symptom_1,
            observation_current_symptom_2,
        )
    )
    session.add_all(
        (
            measurement_vital_signs_pulse_rate_with_number,
            measurement_vital_signs_bp_with_concept,
            measurement_abdominal,
        )
    )
    session.flush()


def generate_random_case(session, case_num):
    person = generate_random_person(case_num)
    session.add(person)
    session.flush()

    visit = generate_random_visit(person.person_id)
    session.add(visit)
    session.flush()

    generate_random_drugs(session, person.person_id, visit.visit_occurrence_id)
    generate_random_observations(session, person.person_id, visit.visit_occurrence_id)
    generate_random_measurements(session, person.person_id, visit.visit_occurrence_id)

    session.flush()


def input_case(session, num_cases=1):
    for case_num in range(num_cases):
        if case_num == 0:
            generate_single_case(session)
        else:
            generate_random_case(session, case_num)


