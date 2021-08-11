import os
import logging
from datetime import datetime


# datetime.strptime and datetime.strftime in one go
def strpstrf(dt, strp="%Y%m%d", strf="%Y-%m-%d"):
    dt = str(dt)  # Ensure string
    return datetime.strftime(datetime.strptime(dt, strp), strf)


def project_root():
    return os.environ.get("SCOVID_PROJECT_ROOT", "/home/code/scovid19")


def env():
    return os.environ.get("SCOVID_ENV", "prod")


def get_logger(name="app", level=logging.INFO):
    logger = logging.getLogger(name)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
