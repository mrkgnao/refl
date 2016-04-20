import configparser

conf = configparser.ConfigParser()
conf.read('refl_config.ini')

def get_server_port():
    return int(conf['server']['serverport'])

def get_server_host():
    return conf['server']['serverhost']

def get_chunk_size():
    return int(conf['general']['chunksize'])

def get_hash_len():
    return int(conf['general']['hashlen'])
