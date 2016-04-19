import logging
import coloredlogs

CUSTOM_STYLES = {'info': {}, 'critical': {'color': 'red', 'bold': True}, 'error': {'color': 'red'}, 'debug': {'color': 'blue'}, 'warning': {'color': 'yellow'}}

def get_colored_logger(ident):
    logger = logging.getLogger(ident)
    coloredlogs.install(level='DEBUG',fmt='[' + ident + '] %(asctime)s %(message)s',level_styles=CUSTOM_STYLES)
    return logger
