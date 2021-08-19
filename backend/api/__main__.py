#!/usr/bin/env python
import asyncio

import typer
import uvicorn  # type: ignore
from funcy import set_in, update_in  # type: ignore

from api import postgres
from api.config import get_config

cli = typer.Typer()


@cli.command()
def serve() -> None:
    log_config = uvicorn.config.LOGGING_CONFIG

    for logger in ["api", "urllib3"]:
        log_config = set_in(
            log_config,
            ["loggers", logger],
            {"handlers": ["default"], "level": "DEBUG"},
        )

    for logger in ["uvicorn.error"]:
        log_config = set_in(
            log_config,
            ["loggers", logger],
            {"handlers": ["default"], "level": "INFO"},
        )

    # Disable propagation for everything we explicitly allow
    # to prevent duplicate loggers.
    for logger_name in log_config["loggers"]:
        log_config = update_in(
            log_config,
            ["loggers", logger_name],
            lambda cfg: {**cfg, "propagate": False},
        )

    log_config["formatters"]["root"] = {
        "()": "uvicorn.logging.DefaultFormatter",
        "fmt": "[%(name)s] %(levelprefix)s %(message)s",
        "use_colors": None,
    }
    log_config["handlers"]["root"] = {
        "formatter": "root",
        "class": "logging.StreamHandler",
        "stream": "ext://sys.stderr",
    }
    log_config["root"] = {
        "handlers": ["root"],
        "level": "DEBUG",
    }

    uvicorn.run(
        "api.app:create_app",
        reload=True,
        factory=True,
        log_config=log_config,
    )


@cli.command()
def migrate() -> None:
    config = get_config()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(postgres.connect_and_migrate(config.postgres))


if __name__ == "__main__":
    cli()
