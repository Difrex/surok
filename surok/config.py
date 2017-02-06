# Public names
__all__ = ['Config', 'AppConfig']

import hashlib
import importlib
import json
import os
from .logger import *

# Logger link

# Config singleton link
_config_singleton = None

'''
Test values
==================================================
key - key
value - value of key
type_value - type of value
type_par - additional parameters for test

'''


'''
Public Config object
==================================================
.set_config(conf_data) - set config data
    Use: conf_data(str type) - path of json config file
         conf_data(dict type) - dict with config
.set(key,value) - set config key
.get(key) - get config key
.update_apps() - update apps config data
.apps - Apps object. List of AppConfig oblects
'''


class _ConfigTemplate(dict):
    _conf = {}

    def _init_conf(self, params):
        conf = {}
        for k in params.keys():
            if params[k].get('params'):
                conf[k] = self._init_conf(params[k].get('params'))
            else:
                if params[k].get('value') is not None:
                    conf[k] = params[k].get('value')
        return conf

    def __init__(self, *conf_data):
        self._logger = Logger()
        if not self._conf:
            self._conf = self._init_conf(self._params)
        for c in conf_data:
            self.set_config(c)

    def _set_conf_params(self, oldconf, testconf, params):
        conf = oldconf if oldconf else {}
        for key in testconf.keys():
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
                if type(testvalue).__name__ != 'list':
                    testvalue = [testvalue]
                for testitem in testvalue:
                    if self._test_value(key, testitem, param):
                        if 'dict' in type_param:
                            if param.get('params'):
                                res = self._set_conf_params(
                                    oldvalue, testitem, param.get('params'))
                                if res is not None:
                                    resvalue.append(res)
                        else:
                            resvalue.append(testitem)
                if 'list' not in type_param:
                    resvalue = list([None] + resvalue).pop()
                if resvalue is not None and 'do' in type_param:
                    if not self._do_type_set(key, resvalue, param):
                        self._logger.warning(
                            'Parameter "', key, '" current "', resvalue, '" type is "', type(resvalue).__name__, '" testing failed')
                        resvalue = None
                if resvalue is not None:
                    conf[key] = resvalue
        return conf

    def _test_value(self, key, value, param):
        type_param = param.get('type')
        type_value = [
            x for x in type_param if x in ['str', 'int', 'bool', 'dict']]
        if type_value:
            if type(value).__name__ not in type_value:
                self._logger.error(
                    'Parameter "', key, '" must be ', type_value,
                                   ' types, current "', value, '" (', type(value).__name__, ')')
                return False
            if 'value' in type_param:
                if value not in param.get('values', []):
                    self._logger.error(
                        'Value "', value, '" of key "', key, '" unknown')
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
                self._logger.error('Load main config file failed')
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
        return self._conf.__str__()

    def __repr__(self):
        return self._conf.__repr__()


class Config(_ConfigTemplate):
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
                "domain": {
                    'value': "marathon.mesos",
                    'type': ['str']
                },
                "enabled": {
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
                            'value': 'memcached',
                            'type': ['str']
                        },
                        'group': {
                            'value': 'system',
                            'type': ['str']
                        }
                    },
                    'type': ['dict']
                },
                'hosts': {
                    'value': ['localhost:11211'],
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
        'wait_time': {
            'value': 20,
            'type': ['int']
        },
        'lock_dir': {
            'value': '/var/tmp',
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
        }
    }

    def __new__(cls, *args):
        global _config_singleton
        if _config_singleton is None:
            _config_singleton = super(Config, cls).__new__(cls)
        return _config_singleton

    def __init__(self, *conf_data):
        super().__init__(*conf_data)
        self.apps = _Apps()

    def set_config(self, conf_data):
        super().set_config(conf_data)
        if self.get('version') == '0.7':
            domain = self.get('domain')
            if domain is not None and self.get('mesos') is None:
                self.set('mesos', {'domain': domain, 'enabled': True})

    def _do_type_set(self, key, value, param):
        if param.get('do') == 'set_loglevel':
            if self._logger.set_level(value):
                return True
        return False

    def update_apps(self):
        self.apps.reset()
        for app in sorted([os.path.join(self.get('confd'), f) for f in os.listdir(self.get('confd')) if os.path.isfile(os.path.join(self.get('confd'), f))]):
            self.apps.set(AppConfig(app))

'''
Private Apps object
==================================================
.get(app) - get _AppConfig object
.set(app) - set _AppConfig object
'''


class _Apps:
    _apps = {}
    _items = []

    def get(self, key):
        return self._apps.get(key)

    def set(self, app):
        self._apps[app.get('conf_name')] = app

    def reset(self):
        keys = [] + list(self.keys())
        for k in keys:
            del self._apps[k]

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, item):
        return bool(item in self._apps)

    def __iter__(self):
        self._items = sorted(self.keys())
        return self

    def __next__(self):
        if self._items:
            return self.get(self._items.pop(0))
        raise StopIteration

    def keys(self):
        return self._apps.keys()

'''
Public AppConfig object
==================================================
.set_config(conf_data) - set config data
    Use: conf_data(str type) - path of json config file
         conf_data(dict type) - dict with config
.set(key,value) - set config key
.get(key) - get config key
'''


class AppConfig(_ConfigTemplate):
    _params = {
        'conf_name': {
            'type': ['str']
        },
        'services': {
            'params': {
                'name': {
                    'type': ['str']
                },
                'ports': {
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
        'template': {
            'type': ['str', 'file']
        },
        'dest': {
            'type': ['str']
        },
        'reload_cmd': {
            'type': ['str']
        },
        'discovery': {
            'type': ['str']
        },
        'group': {
            'type': ['str']
        }
    }

    def __init__(self, *conf_data):
        self._config = Config()
        super().__init__(*conf_data)

    def set_config(self, conf_data):
        super().set_config(conf_data)
        self._conf.setdefault(
            'discovery', self._config.get('default_discovery'))
        self._conf.setdefault('group', self._get_default_group())
        if type(conf_data).__name__ == 'str':
            self._conf.setdefault('conf_name', os.path.basename(conf_data))

    def _get_default_group(self):
        env = self._config.get('env', dict(os.environ))
        # Check environment variable
        if env.get('SUROK_DISCOVERY_GROUP'):
            return env['SUROK_DISCOVERY_GROUP']
        # Check marathon environment variable
        elif env.get('MARATHON_APP_ID'):
            return ".".join(env['MARATHON_APP_ID'].split('/')[-2:0:-1])
