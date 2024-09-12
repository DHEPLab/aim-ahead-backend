import logging
from logging.config import fileConfig

from flask import current_app
from src.user.model import user
from src.user.model import display_config, reset_password_token
from alembic import context

# clinical data
from src.cases.model.clinical_data.person import condition_occurrence
from src.cases.model.clinical_data.person import death
from src.cases.model.clinical_data.person import device_exposure
from src.cases.model.clinical_data.person import drug_exposure
from src.cases.model.clinical_data.person import measurement
from src.cases.model.clinical_data.person import note
from src.cases.model.clinical_data.person import observation
from src.cases.model.clinical_data.person import observation_period
from src.cases.model.clinical_data.person import person
from src.cases.model.clinical_data.person import procedure_occurrence
from src.cases.model.clinical_data.person import specimen
from src.cases.model.clinical_data.person import visit_detail
from src.cases.model.clinical_data.person import visit_occurrence
from src.cases.model.clinical_data import fact_relationship
# health system
from src.cases.model.health_system import care_site
from src.cases.model.health_system import location
from src.cases.model.health_system import provider

# vocabularies

from src.cases.model.vocabularies import concept
from src.cases.model.vocabularies import concept_ancestor
from src.cases.model.vocabularies import concept_class
from src.cases.model.vocabularies import concept_relationship
from src.cases.model.vocabularies import concept_synonym
from src.cases.model.vocabularies import domain
from src.cases.model.vocabularies import drug_strength
from src.cases.model.vocabularies import relationship
from src.cases.model.vocabularies import source_to_concept_map
from src.cases.model.vocabularies import vocabulary

from src.common.model.system_config import SystemConfig

# answer
from src.answer.model.answer import Answer

# config 
from src.configration.model import answer_config

# task
from src.task.model import task

from src.cases.model.case_prediction import CasePrediction

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_metadata():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
