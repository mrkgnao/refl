import logging
import coloredlogs

DATE_FORMAT = '%H:%M:%S'

LOG_FORMAT_PRE = '%(asctime)s.%(msecs).03d'
LOG_FORMAT_POST = '[%(threadName)s] %(message)s'
LOG_FORMAT = LOG_FORMAT_PRE + " " + LOG_FORMAT_POST
# LOG_FORMAT = '%(asctime)s [%(hostname)s/%(threadName)s] %(message)s'

LEVEL_STYLES = {
    'info': {},
    'critical': {'color': 'red', 'bold': True},
    'error': {'color': 'red'},
    'debug': {'color': 'blue'},
    'warning': {'color': 'yellow'}}

FIELD_STYLES = {
    'hostname': {'color': 'cyan'},
    'programname': {'color': 'cyan'},
    'name': {'color': 'blue'},
    'levelname': {'color': 'black', 'bold': True},
    'asctime': {'color': 'green'},
    'threadname': {'color': 'magenta'}}

logger = logging.getLogger("refl")
coloredlogs.install(
    level='DEBUG',
    fmt=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    level_styles=LEVEL_STYLES,
    field_styles=FIELD_STYLES)

def get_colored_logger(ident=None):
    if True: # ident is None:
        fmt = LOG_FORMAT
    else:
        fmt = "{} {} {}".format(LOG_FORMAT_PRE, ident, LOG_FORMAT_POST)

    logger = logging.getLogger("refl")
    coloredlogs.install(
        level='DEBUG',
        fmt=fmt,
        datefmt=DATE_FORMAT,
        level_styles=LEVEL_STYLES,
        field_styles=FIELD_STYLES)
    return logger
