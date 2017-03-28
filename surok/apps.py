# Public names
__all__ = ['Apps']

from .logger import *
from .config import *
from .discovery import *
from .store import *
import jinja2
import os
import hashlib
import urllib3
import imp
import json
import requests

'''
Public Apps object
==================================================
'''


class Apps:

    def __init__(self):
        if not hasattr(self, '_config'):
            self._config = Config()
        if not hasattr(self, '_logger'):
            self._logger = Logger()
        if not hasattr(self, '_store'):
            self._store = Store()
        if not hasattr(self, '_discovery'):
            self._discovery = Discovery()
        if not hasattr(self, '_loadmodule'):
            self._loadmodule = LoadModules()

    def update(self):
        """ format app config:
            'files': {
                '/destination/file1': 'Config data 1',
                '/destination/file2': 'Config data 2',
                '/destination/fileN': 'Config data N'
            },
            'environments': {
                'ENV1': 'Jinja2 template for value "{{ my.env.get('ENV1') }}"',
                'ENV2': 'Next Jinja2 template for value "{{ my.env.get('ENV2') }}"'
            }
        """
        self._discovery.update_data()
        self._store.check()
        for app in [self._config.apps[x] for x in self._config.apps]:
            my = {"services": self._discovery.resolve(app),
                  "conf_name": app['conf_name'],
                  "env": os.environ}
            _restart = False
            for conf in [{'env': x, 'value': self._render(my, app['environments'][x])} for x in app['environments']]:
                if self._store.check_update(conf):
                    _restart = True
                    os.environ[conf['env']] = conf['value']
            for conf in [{'dest': x, 'value': self._render(my, app['files'][x])} for x in app['files']]:
                if self._store.check_update(conf):
                    _restart = True
                    self._logger.info("Write new configuration of ", conf.get('dest'))
                    try:
                        f = open(conf.get('dest'), 'w')
                        f.write(conf.get('value'))
                        f.close()
                    except OSError as err:
                        self._logger.error(
                            'Config file {0} open or write error. OS error : {1}'.format(conf.get('dest'), err))
                        pass
                    except err:
                        self._logger.error(
                            'Config file {0} open or write error. Error : {1}'.format(conf.get('dest'), err))
                        pass
            if _restart:
                if self._config['marathon']['restart']:
                    self._restart_self_in_marathon()
                else:
                    self._logger.info('Restart ', app.get('reload_cmd'), ' app.\n', os.popen(app['reload_cmd']).read())
        self._store.clear()

    def _render(self, my, temp):
        if type(temp).__name__ == 'str':
            data = None
            try:
                template = jinja2.Template(temp)
                data = template.render(my=my, mod=LoadModules(_my=my))
            except jinja2.UndefinedError as err:
                self._logger.error('Render Jinja2 error. ', err)
            except:
                self._logger.error('Render Jinja2 error. Unknown error')
            return data

    def _restart_self_in_marathon(self):
        env = os.environ.get('MARATHON_APP_ID')
        if env:
            r = requests.post('http://' + self._config['marathon']['host'] + '/v2/apps/' + env + '/restart',
                              data={'force': self._config['marathon']['force']})
            if r.status_code != 200:
                self._logger.error(
                    'Restart container {0} failed. {1}'.format(env, raise_for_status()))
        else:
            logger.error(
                'Restart self container failed. Cannot find MARATHON_APP_ID.')


class LoadModules:
    _instance = None
    _get_module = True

    def __new__(cls, **pars):
        if cls._instance is None:
            cls._instance = super(LoadModules, cls).__new__(cls)
        return cls._instance

    def __init__(self, **pars):
        for key in pars:
            if pars[key] is None:
                if hasattr(LoadModules, key):
                    delattr(LoadModules, key)
            else:
                setattr(LoadModules, key, pars[key])
        if self._get_module:
            if not hasattr(self, '_config'):
                self._config = Config()
            if not hasattr(self, '_logger'):
                self._logger = Logger()
            for module in [os.path.join(self._config['modules'], f) for f in os.listdir(self._config['modules']) if os.path.isfile(os.path.join(self._config['modules'], f))]:
                try:
                    m = imp.load_source('__surok.module__', module)
                except:
                    self._logger.error('Load module {} failed.'.format(module))
                finally:
                    for key in [x for x in dir(m) if type(getattr(m, x)).__name__ == 'function' and not x.startswith('_')]:
                        setattr(LoadModules, key, getattr(m, key))
            self._get_module = False
