# Public names
__all__ = ['Config', 'AppConfig']

import hashlib
import json
import os
from .logger import *

class _ConfigTemplate(dict):
    """ Test values
    ==================================================
    key - key
    value - value of key
    type_value - type of value
    type_par - additional parameters for test
    """
    _conf = None
    def _init_conf(self, params):
        conf = {}
        for k in params.keys():
            if params[k].get('params'):
                conf[k] = self._init_conf(params[k].get('params'))
            else:
                value = params[k].get('value')
                if value is not None:
                    if type(value).__name__ == 'dict':
                        conf[k] = value.copy()
                    else:
                        conf[k] = value
        return conf

    def __init__(self, *conf_data):
        if not hasattr(self, '_logger'):
            self._logger = Logger()
        if self._conf is None:
            self._conf = self._init_conf(self._params)
        for c in conf_data:
            self.set_config(c)

    # Testing testconf with params data, and update oldconf with data from testconf
    def _set_conf_params(self, oldconf, testconf, params):
        conf = oldconf.copy() if oldconf else {}
        for key in testconf:
            resvalue = None
            param = params.get(key)
            oldvalue = conf.get(key)
            testvalue = testconf.get(key)
            if param is None:
                self._logger.error('Parameter "', key, '" value "', testvalue,
                                   '" type is "', type(testvalue).__name__, '" not found')
            else:
                type_param = param.get('type')
                resvalue = []
                reskeys = []
                if 'anykeys' in type_param:
                    if type(testvalue).__name__ == 'dict':
                        testvalue = testvalue.items()
                    else:
                        self._logger.warning('Parameter "{}" must be "dict" type'.format(key))
                        continue
                elif type(testvalue).__name__ != 'list':
                    testvalue = [testvalue]
                key_testitem = key
                for testitem in testvalue:
                    if 'anykeys' in type_param:
                        key_testitem, testitem = testitem
                    if self._test_value(key_testitem, testitem, param):
                        if 'dict' in type_param:
                            if param.get('params'):
                                res = self._set_conf_params(oldvalue, testitem, param.get('params'))
                                if res is not None:
                                    resvalue.append(res)
                                    reskeys.append(key_testitem)
                        else:
                            resvalue.append(testitem)
                            reskeys.append(key_testitem)
                if 'anykeys' in type_param:
                    resvalue = dict([(reskeys.pop(0),x) for x in resvalue])
                elif 'list' not in type_param:
                    resvalue = list([None] + resvalue).pop()
                if resvalue is not None and 'do' in type_param:
                    if not self._do_type_set(key, resvalue, param):
                        self._logger.warning('Parameter "', key, '" current "', resvalue, '" type is "', type(resvalue).__name__, '" testing failed')
                        resvalue = None
                if resvalue is not None:
                    conf[key] = resvalue
        return conf

    def _test_value(self, key, value, param):
        type_param = param.get('type')
        type_value = [x for x in type_param if x in ['str', 'int', 'bool', 'dict']]
        if type_value:
            if type(value).__name__ not in type_value:
                self._logger.error('Parameter "', key, '" must be ', type_value,' types, current "', value, '" (', type(value).__name__, ')')
                return False
            if 'value' in type_param:
                if value not in param.get('values', []):
                    self._logger.error('Value "', value, '" of key "', key, '" unknown')
                    return False
            if 'dir' in type_param:
                if not os.path.isdir(value):
                    self._logger.error('Path "{}" not present'.format(value))
                    return False
            elif 'file' in type_param:
                if not os.path.isfile(value):
                    self._logger.error('File "{}" not present'.format(value))
                    return False
            return True
        else:
            self._logger.error(
                'Type for testing "{}" unknown'.format(type_value))
            return False

    def set_config(self, conf_data):
        conf = {}
        if type(conf_data).__name__ == 'str':
            try:
                self._logger.debug('Open file ', conf_data)
                f = open(conf_data, 'r')
                json_data = f.read()
                f.close()
                conf = json.loads(json_data)
            except OSError as err:
                self._logger.error("OS error: {0}".format(err))
                pass
            except ValueError as err:
                self._logger.error('JSON format error: {0}'.format(err))
                pass
            except:
                self._logger.error('Load config file failed')
                pass
        elif type(conf).__name__ == 'dict':
            conf = conf_data
        else:
            return False
        self._conf = self._set_conf_params(self._conf, conf, self._params)
        self._logger.debug('Conf=', self._conf)

    def keys(self):
        return self._conf.keys()

    def dump(self):
        return json.dumps(self._conf, sort_keys=True, indent=2)

    def _do_type_set(self, key, value, params):
        self._logger.error('_do_type_set handler is not defined')
        return False

    def hash(self):
        return hashlib.sha1(json.dumps(self._conf, sort_keys=True).encode()).hexdigest()

    def set(self, key, value):
        self._conf[key] = value

    def __setitem__(self, key, value):
        self.set(key, value)

    def get(self, key, default=None):
        return self._conf.get(key, default)

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, item):
        return bool(item in self._conf)

    def __len__(self):
        return self._conf.__len__()

    def __str__(self):
        return self.dump()

    def __repr__(self):
        return self.dump()


class Config(_ConfigTemplate):
    """ Public Config object
    ==================================================
    .set_config(conf_data) - set config data
        Use: conf_data(str type) - path of json config file
             conf_data(dict type) - dict with config
    .set(key,value) - set config key
    .get(key) - get config key
    .update_apps() - update apps config data
    .apps - Dict of AppConfig oblects
    """
    _instance = None
    apps={}
    _params = {
        'marathon': {
            'params': {
                'force': {
                    'value': True,
                    'type': ['bool']
                },
                'host': {
                    'value': 'http://marathon.mesos:8080',
                    'type': ['str']
                },
                'enabled': {
                    'value': False,
                    'type': ['bool']
                },
                'restart': {
                    'value': False,
                    'type': ['bool']
                }
            },
            'type': ['dict']
        },
        'mesos': {
            'params': {
                'domain': {
                    'value': 'marathon.mesos',
                    'type': ['str']
                },
                'enabled': {
                    'value': False,
                    'type': ['bool']
                }
            },
            'type': ['dict']
        },
        'files': {
            'params': {
                'path': {
                    'value': '/var/tmp',
                    'type': ['str', 'dir']
                },
                'enabled': {
                    'value': False,
                    'type': ['bool']
                }
            },
            'type': ['dict']
        },
        'memcached': {
            'params': {
                'enabled': {
                    'value': False,
                    'type': ['bool']
                },
                'discovery': {
                    'params': {
                        'enabled': {
                            'value': False,
                            'type': ['bool']
                        },
                        'service': {
                            'type': ['str']
                        },
                        'group': {
                            'type': ['str']
                        }
                    },
                    'type': ['dict']
                },
                'host': {
                    'type': ['str']
                },
                'hosts': {
                    'type': ['list', 'str']
                }
            },
            'type': ['dict']
        },
        'version': {
            'value': '0.7',
            'type': ['str', 'value'],
            'values': ['0.7', '0.8']
        },
        'confd': {
            'value': '/etc/surok/conf.d',
            'type': ['str', 'dir']
        },
        'modules': {
            'value': '/opt/surok/modules',
            'type': ['str', 'dir']
        },
        'wait_time': {
            'value': 20,
            'type': ['int']
        },
        'lock_dir': {
            'type': ['str', 'dir']
        },
        'default_discovery': {
            'value': 'mesos_dns',
            'type': ['str', 'value'],
            'values': ['mesos_dns', 'marathon_api']
        },
        'loglevel': {
            'value': 'info',
            'type': ['str', 'do'],
            'do': 'set_loglevel'
        },
        'default_store':{
            'value': 'memory',
            'type': ['str', 'value'],
            'values': ['memory', 'files', 'memcached']
        },
        'domain':{
            'type': ['str']
        }
    }

    def __new__(cls, *args):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, *conf_data):
        super().__init__(*conf_data)

    def set_config(self, conf_data):
        super().set_config(conf_data)
        if self.get('version') == '0.7':
            domain = self.get('domain')
            if domain is not None:
                self['mesos'] = {'domain': domain, 'enabled': True}
            path = self.get('lock_dir')
            if path is not None:
                self['files'] = {'path': path, 'enabled': True}
            self['marathon']['restart'] = self['marathon']['enabled']
            self['marathon']['enabled'] = True

    def _do_type_set(self, key, value, param):
        if param.get('do') == 'set_loglevel':
            if self._logger.set_level(value):
                return True
        return False

    def update_apps(self):
        self.apps={}
        for app_conf in sorted([os.path.join(self.get('confd'), f) for f in os.listdir(self.get('confd')) if os.path.isfile(os.path.join(self.get('confd'), f))]):
            app = AppConfig(app_conf)
            self.apps[app['conf_name']] = app



class AppConfig(_ConfigTemplate):
    """ Public AppConfig object
    ==================================================
    .set_config(conf_data) - set config data
        Use: conf_data(str type) - path of json config file
             conf_data(dict type) - dict with config
    .set(key,value) - set config key
    .get(key) - get config key
    """
    _params = {
        'conf_name': {
            'type': ['str']
        },
        'services': {
            'value': [],
            'params': {
                'name': {
                    'type': ['str']
                },
                'ports': {
                    'type': ['list', 'str']
                },
                'tcp': {
                    'type': ['list', 'str']
                },
                'udp': {
                    'type': ['list', 'str']
                },
                'discovery': {
                    'type': ['str']
                },
                'group': {
                    'type': ['str']
                }
            },
            'type': ['list', 'dict']
        },
        'files': {
            'value': {},
            'type': ['anykeys', 'str']
        },
        'environments': {
            'value': {},
            'type': ['anykeys', 'str']
        },
        'reload_cmd': {
            'type': ['str']
        },
        'discovery': {
            'type': ['str']
        },
        'store':{
            'value': 'memory',
            'type': ['str', 'value'],
            'values': ['memory', 'files', 'memcached']
        },
        'group': {
            'type': ['str']
        },
        'template': {
            'type': ['str']
        },
        'dest': {
            'type': ['str']
        }
    }

    def __init__(self, *conf_data):
        if not hasattr(self, '_config'):
            self._config = Config()
        super().__init__(*conf_data)

    def set_config(self, conf_data):
        super().set_config(conf_data)
        self._conf.setdefault('discovery', self._config.get('default_discovery'))
        self._conf.setdefault('store', self._config.get('default_store'))
        if 'group' not in self._conf:
            self._conf['group'] = self._get_default_group()
        if 'dest' in self._conf and 'template' in self._conf:
            self._conf['files'].update({self._conf.get('dest'): '{{ mod.template(mod.from_file(\'' + self._conf.get('template') + '\')) }}'})
        for service in self._conf.get('services',{}):
            if service.get('ports'):
                service.setdefault('tcp',[])
                service['tcp'].extend(service.get('ports'))
        if type(conf_data).__name__ == 'str' and 'conf_name' not in self._conf:
            self._conf['conf_name'] = os.path.basename(conf_data)

    def _get_default_group(self):
        env = self._config.get('env', dict(os.environ))
        if env.get('SUROK_DISCOVERY_GROUP'):
            return env['SUROK_DISCOVERY_GROUP']
        elif env.get('MARATHON_APP_ID'):
            return ".".join(env['MARATHON_APP_ID'].split('/')[-2:0:-1])
