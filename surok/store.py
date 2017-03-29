# Public names
__all__ = ['Store']

from .logger import *
from .config import *
from .discovery import *
import os
import hashlib
import json
import importlib


class Store(dict):

    """ Public Store object
    ==================================================
    """
    _instance = None
    _stores = {}
    _update_store = {}

    def __new__(cls, *args):
        if cls._instance is None:
            cls._instance = super(Store, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args):
        if not hasattr(self, '_config'):
            self._config = Config()
        if not hasattr(self, '_logger'):
            self._logger = Logger()
        if 'memory' not in self._stores:
            self._stores['memory'] = StoreMemory()
        if 'files' not in self._stores:
            self._stores['files'] = StoreFiles()
        if 'memcached' not in self._stores:
            self._stores['memcached'] = StoreMemcached(self)

    def get(self, temp):
        new_temp = self._normalize(temp)
        old_temp = self._stores[new_temp['store']].get(new_temp['hashid'], {})
        old_temp['store'] = new_temp['store']
        old_temp['hashid'] = new_temp['hashid']
        self._update_store[new_temp['hashid']] = new_temp['store']
        return old_temp

    def set(self, temp):
        new_temp = self._normalize(temp)
        if new_temp.get('dest'):
            self._stores[new_temp['store']].set(new_temp.get('hashid'),
                                       {'hash': new_temp.get('hash'),
                                        'dest': new_temp.get('dest')})
        elif new_temp.get('env'):
            self._stores[new_temp['store']].set(new_temp.get('hashid'),
                                       {'hash': new_temp.get('hash'),
                                         'env': new_temp.get('env')})
        else:
            self._stores[new_temp['store']].set(new_temp.get('hashid'),
                                       {'hash': new_temp.get('hash')})

    def delete(self, temp):
        new_temp = self._normalize(temp)
        if self._update_store.get(new_temp['hashid']):
            del self._update_store[new_temp['hashid']]
        self._stores[new_temp['store']].delete(new_temp['hashid'])

    def keys(self):
        keys = {}
        for key in self._stores.keys():
            if self._stores[key].enabled():
                keys.update(dict.fromkeys(self._stores[key].keys(), key))
        return keys

    def check_update(self, temp):
        new_temp = self._normalize(temp)
        old_temp = self.get(new_temp.get('hashid'))
        if new_temp.get('hash') is not None and old_temp.get('hash') != new_temp.get('hash'):
            self.set(new_temp)
            return True
        return False

    def check(self):
        for key in self._stores:
            self._stores[key].check()

    def clear(self):
        keys = self.keys()
        for temp in [self.get(x) for x in keys if x not in self._update_store]:
            temp['store'] = keys[temp['hashid']]
            if temp.get('dest'):
                try:
                    if os.path.isfile(temp.get('dest')):
                        os.remove(temp.get('dest'))
                except OSError as err:
                    self._logger.warning(
                        "Delete file {0} failed:\n{1}".format(temp.get('dest'), err))
                    pass
            elif temp.get('env'):
                try:
                    if os.environ.get(temp.get('env')):
                        del os.environ[temp.get('env')]
                except:
                    self._logger.warning(
                        'Delete environment "{0}" failed.'.format(temp.get('env')))
                    pass
            self.delete(temp)
        self._update_store = {}

    def _normalize(self, unnormconf):
        if type(unnormconf).__name__ == 'dict':
            conf = unnormconf.copy()
        else:
            conf = {'hashid': unnormconf}
        conf.setdefault('store', self._config['default_store'])
        if 'dest' in conf:
            conf['hashid'] = hashlib.sha1(conf['dest'].encode()).hexdigest()
        elif 'env' in conf:
            conf['hashid'] = hashlib.sha1(str('env:' + conf['env']).encode()).hexdigest()
        elif 'localid' in conf:
            conf['hashid'] = hashlib.sha1(str('data:' + conf['localid']).encode()).hexdigest()

        if 'data' in conf:
            conf['hash'] = hashlib.sha1(json.dumps(conf['data'], sort_keys=True).encode()).hexdigest()
        elif type(conf.get('value')).__name__ == 'str':
            conf['hash'] = hashlib.sha1(conf['value'].encode()).hexdigest()

        if not self._stores[conf['store']].enabled():
            self._logger.warning(
                'Store "{0}" not enabled. Store type change to "memory" for hashid "{1}".'.format(conf['store'], conf['hashid']))
            conf['store'] = 'memory'
        return conf


class _StoreTemplate(dict):

    def __init__(self, *args):
        if not hasattr(self, '_config'):
            self._config = Config()
        if not hasattr(self, '_logger'):
            self._logger = Logger()

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        self.delete(key)

    def __contains__(self, item):
        return bool(item in self.keys())

    def __len__(self):
        return len(self.keys())

    def enabled(self):
        return self._enabled

    def check(self):
        pass


class StoreMemory(_StoreTemplate):
    _store = {}
    _enabled = True

    def get(self, key, default=None):
        return self._store.get(key, default)

    def set(self, key, value):
        self._store[key] = value.copy()

    def keys(self):
        return self._store.keys()

    def delete(self, key):
        del self._store[key]


class StoreFiles(_StoreTemplate):
    _enabled = False

    def __init__(self, *args):
        super().__init__(*args)
        self.check()

    def get(self, key, default=None):
        temp = default
        try:
            filename = self._config['files']['path'] + '/' + key + '.surok'
            if os.path.isfile(filename):
                f = open(filename, 'r')
                json_temp = f.read()
                f.close()
                temp = json.loads(json_temp)
        except OSError as err:
            self._logger.error(
                'Get from "files" store failed. OS error: {0}'.format(err))
            pass
        except ValueError as err:
            self._logger.error(
                'Get from "files" store failed. JSON format error: {0}'.format(err))
            pass
        except:
            self._logger.error('Get from "files" store failed. Unknown error.')
            pass
        return temp

    def set(self, key, value):
        try:
            f = open(self._config['files']['path'] + '/' + key + '.surok', 'w')
            f.write(json.dumps(value, sort_keys=True))
            f.close()
        except OSError as err:
            self._logger.error(
                'Set from "files" store failed. OS error: {0}'.format(err))
            pass
        except ValueError as err:
            self._logger.error(
                'Set from "files" store failed. JSON format error: {0}'.format(err))
            pass
        except:
            self._logger.error('Set from "files" store failed. Unknown error.')
            pass

    def keys(self):
        return [f.split('.')[0] for f in os.listdir(self._config['files']['path']) if os.path.isfile(os.path.join(self._config['files']['path'], f)) and f.split('.')[1] == 'surok']

    def delete(self, key):
        try:
            os.remove(self._config['files']['path'] + '/' + key + '.surok')
        except OSError as err:
            self._logger.error(
                'Delete from "files" store failed. OS error: {0}'.format(err))
            pass

    def check(self):
        self._enabled = self._config['files']['enabled']
        if self._enabled and not os.path.isdir(self._config['files']['path']):
            self._enabled = False


class StoreMemcached(_StoreTemplate):
    _mc = None
    _enabled = False
    _hosts = []
    _mod_memcache = None
    def __init__(self, *args):
        super().__init__(*args)
        self._enabled = self._config['memcached']['enabled']
        if self._enabled and not hasattr(self, '_discovery'):
            self._discovery = Discovery()
        if args and not hasattr(self, '_store'):
            self._store = args[0]

    def _reconnect(self):
        if self._hosts:
            if self._mc is None:
                if self._mod_memcache is None:
                    self._mod_memcache = importlib.import_module('memcache')
                try:
                    self._mc = self._module.Client(self._hosts)
                    self._enabled = True
                except:
                    self._logger.error('Create memcached object failed')
                    self._disconnect()
            else:
                try:
                    self._mc.disconnect_all()
                    self._mc.set_servers(self._hosts)
                    self._enabled = True
                except:
                    self._logger.error('Change memcached list of servers failed')
                    self._disconnect()
        else:
            self._disconnect()

    def check(self):
        if self._config['memcached']['enabled']:
            if self._config['memcached']['discovery']['enabled'] and self._config['memcached']['discovery'].get('service') is not None:
                service = self._config['memcached']['discovery']['service']
                app_conf = {'services': [{'name': service}]}
                if self._config['memcached']['discovery']['group']:
                    app_conf['services'][0]['group'] = self._config['memcached']['discovery']['group']
                app = AppConfig(app_conf)
                discovery_data = self._discovery.resolve(app)
                if discovery_data.get(service) and discovery_data[service][0].get('name') and discovery_data[service][0].get('tcp'):
                    hosts = [discovery_data[service][0]['name'] + ':' + discovery_data[service][0]['tcp'][0]]
                else:
                    if self._config['memcached'].get('host'):
                        hosts = [self._config['memcached']['host']]
                    else:
                        hosts = []
                if self._store.check_update({'localid': 'memcached_discovery', 'data': hosts, 'store': 'memory'}):
                    self._hosts = hosts
                    self._enabled = True
                    self._reconnect()
            else:
                hosts = []
                if self._config['memcached'].get('host'):
                    hosts = [self._config['memcached']['host']]
                elif self._config['memcached'].get('hosts'):
                    hosts = self._config['memcached']['hosts']
                if self._mc is None or self._hosts != hosts:
                    self._hosts = hosts
                    self._reconnect()
        else:
            self._disconnect()

    def _disconnect(self):
            self._enabled = False
            if self._mc is not None:
                self._mc.disconnect_all()
                self._mc = None

    def get(self, key, default=None):
        temp = default
        try:
            if key in self.keys():
                temp = json.loads(self._mc.get(key))
        except ValueError as err:
            self._logger.error(
                'Get from "memcached" store failed. JSON format error: {0}'.format(err))
            pass
        except:
            self._logger.error(
                'Get from "memcached" store failed. Unknown error. Made reconnect\nKey:', key)
            self.check()
            pass
        return temp

    def set(self, key, value):
        try:
            self._mc.set(key, json.dumps(value, sort_keys=True))
        except ValueError as err:
            self._logger.error(
                'Set from "memcached" store failed. JSON format error: {0}'.format(err))
            pass
        except:
            self._logger.error(
                'Set from "memcached" store failed. Unknown error. Made reconnect\nKey:', key, '\nValue:\n', value)
            self.check()
            pass

    def keys(self):
        mkeys = {}
        for server_item in self._mc.get_stats('items'):
            for item in server_item[-1].keys():
                keys_item = item.split(':')
                if keys_item[2] == 'number':
                    for server_dump in self._mc.get_stats(' '.join(['cachedump', keys_item[1], server_item[-1][item]])):
                        mkeys.update(server_dump[-1])
        return mkeys.keys()

    def delete(self, key):
        try:
            self._mc.delete(key)
        except:
            self._logger.error(
                'Delete from "memcached" store failed. Unknown error. Made reconnect')
            self.check()
            pass
