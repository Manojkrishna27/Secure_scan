"""Alembic migration environment."""
import logging
from configparser import ConfigParser
from logging.config import fileConfig

from alembic import context
from flask import current_app

config = context.config

# Flask-Migrate may pass a partial config; only apply fileConfig when logging sections exist.
if config.config_file_name is not None:
    _logging_cfg = ConfigParser()
    _logging_cfg.read(config.config_file_name)
    if _logging_cfg.has_section("formatters"):
        fileConfig(config.config_file_name)
    else:
        logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("alembic.env")


def get_engine():
    return current_app.extensions["migrate"].db.get_engine()


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace("%", "%%")
    except AttributeError:
        return str(get_engine().url).replace("%", "%%")


config.set_main_option("sqlalchemy.url", get_engine_url())
target_db = current_app.extensions["migrate"].db


def get_metadata():
    if hasattr(target_db, "metadatas"):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    conf_args = current_app.extensions["migrate"].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
