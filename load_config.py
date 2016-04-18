import configparser

def get_server_port():
    conf = configparser.ConfigParser()
    conf.read('refl_config.ini')
    return int(conf['server']['serverport'])

def get_server_host():
    conf = configparser.ConfigParser()
    conf.read('refl_config.ini')
    return conf['server']['serverhost']
