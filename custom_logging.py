import logging
import coloredlogs

CUSTOM_LEVEL_STYLES = {
    'info': {},
    'critical': {'color': 'red', 'bold': True},
    'error': {'color': 'red'},
    'debug': {'color': 'blue'},
    'warning': {'color': 'yellow'}}

CUSTOM_FIELD_STYLES = {
    'hostname': {'color': 'magenta'},
    'programname': {'color': 'cyan'},
    'name': {'color': 'blue'},
    'levelname': {'color': 'black', 'bold': True},
    'asctime': {'color': 'green'},
    'threadname': {'color': 'cyan'}}

def get_colored_logger(ident):
    logger = logging.getLogger(ident)
    coloredlogs.install(
        level='DEBUG',
        fmt='%(asctime)s [%(threadName)s] %(message)s',
        level_styles=CUSTOM_LEVEL_STYLES,
        field_styles=CUSTOM_FIELD_STYLES)
    return logger
