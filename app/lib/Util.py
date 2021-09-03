import os
import logging
from datetime import datetime


# datetime.strptime and datetime.strftime in one go
def strpstrf(dt, strp="%Y%m%d", strf="%Y-%m-%d", rev=False):
    """
    Parse and format a datetime string in one go

    Default parse format is %Y%m%d (The format the OpenData uses) and out is %Y-%m-%d (ISO-8601)
    This can be easily swapped by setting `rev` as True
    """
    dt = str(dt)  # Ensure string

    if rev:
        strp, strf = strf, strp

    return datetime.strftime(datetime.strptime(dt, strp), strf)


def project_root():
    return os.environ.get("SCOVID_PROJECT_ROOT", "/home/app/scovid19")


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
