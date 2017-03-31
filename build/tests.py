#!/usr/bin/python3
import unittest
import json
import os
import re
import sys
import hashlib
import surok.apps
import surok.config
import surok.logger
import surok.discovery
import surok.store

class Config(surok.config.Config):
    def __init__(self, *conf_data):
        self._logger = Logger()
        super().__init__(*conf_data)

    def clear(self):
        self._conf = None
        self.__init__()

    def update_apps(self):
        self.apps={}
        for app_conf in sorted([os.path.join(self.get('confd'), f) for f in os.listdir(self.get('confd')) if os.path.isfile(os.path.join(self.get('confd'), f))]):
            app = AppConfig(app_conf)
            self.apps[app['conf_name']] = app

class AppConfig(surok.config.AppConfig):
    def __init__(self, *conf_data):
        self._config = Config()
        self._logger = Logger()
        super().__init__(*conf_data)

class Logger(surok.logger.Logger):
    _out=''
    _err=''
    def _log2err(self,out):
        self._err+=out

    def _log2out(self,out):
        self._out+=out

    def geterr(self):
        return self._err

    def getout(self):
        return self._out

    def reset(self):
        self._err=''
        self._out=''

class DiscoveryTestingTemplate:
    _testing={}
    _testing_fqdn_a={
        "test.zzz0.test": ['10.0.0.1','10.1.0.1'],
        "test.zzz1.test": ['10.0.1.1','10.1.1.1'],
        "test.zzz2.test": ['10.0.2.1','10.1.2.1'],
        "test.zzz3.test": ['10.0.3.1','10.1.3.1'],
        "localhost": ['127.0.0.1']
    }
    _testing_fqdn_srv={}

    def __init__(self):
        self._config = Config()
        self._logger = Logger()
        super().__init__()

    def do_query_a(self,fqdn):
        res=self._testing_fqdn_a.get(fqdn,[])
        if res:
            return res
        else:
            self._logger.error('Testing FQDN ' + fqdn + ' not found in test A records')
            sys.exit(2)

    def do_query_srv(self,fqdn):
        res=self._testing_fqdn_srv.get(fqdn,[])
        if res or fqdn.startswith('_tname_e.') or fqdn.find('._udp.'):
            return res
        else:
            self._logger.error('Testing FQDN '+fqdn+' not found in test SRV records')
            sys.exit(2)

    def update_data(self):
        class_name=self.__class__.__name__
        tgen={
          "name": ["zzz0","zzy0","zzy1","zzz1"],
          "host": ["test.zzz0.test","test.zzz1.test","test.zzz2.test","test.zzz3.test"],
          "serv": ["tname_aa","tname_ab","tname_ba","tname_bb"],
          "ports": [12341,12342,12343,12344],
          "servicePorts": [21221,21222,21223,21224]
        }
        if self._testing.get(class_name,True):
            if class_name == 'DiscoveryMarathon':
                _tasks=[]
                _ports={}
                for id in (0,1,2,3):
                    ports=[]+tgen['ports']
                    servicePorts=[]+tgen['servicePorts']
                    appId='/'.join(str(tgen['name'][id]+'.xxx.yyy.').split('.')[::-1])
                    _ports[appId]=[]
                    for pid in (0,1,2,3):
                        ports[pid]+=pid*10
                        servicePorts[pid]+=pid*100
                        for prot in ['tcp','udp']:
                            if pid<2 or prot == 'tcp':
                                _ports[appId].append({'containerPort': 0,
                                                      'hostPort': 0,
                                                      'labels': {},
                                                      'name': tgen['serv'][pid],
                                                      'protocol': prot,
                                                      'servicePort': servicePorts[pid]})

                    _tasks.append({'appId':appId,
                                   'host':tgen['host'][id],
                                   'ports':ports,
                                   'servicePorts':servicePorts})
                #_tname_a._zzy0.yyy.xxx._tcp.marathon.mesos
                self._tasks=_tasks
                self._ports=_ports
            elif class_name == 'DiscoveryMesos':
                for id in (0,1,2,3):
                    ports=[]+tgen['ports']
                    for pid in (0,1,2,3):
                        ports[pid]+=pid*10
                        for prot in ['tcp','udp']:
                            if pid<2 or prot == 'tcp':
                                for fqdn in ['_'+tgen['serv'][pid]+'._'+tgen['name'][id]+'.xxx.yyy._'+prot+'.'+self._config['mesos']['domain'],
                                                                    '_'+tgen['name'][id]+'.xxx.yyy._'+prot+'.'+self._config['mesos']['domain']]:
                                    if not self._testing_fqdn_srv.get(fqdn):
                                        self._testing_fqdn_srv[fqdn]=[]
                                    self._testing_fqdn_srv[fqdn].append({'name':tgen['host'][id],'port':ports[pid]})

                if os.environ.get('MEMCACHE_PORT'):
                    memcached = os.environ['MEMCACHE_PORT'].split('/')[2].split(':')
                    self._testing_fqdn_a[memcached[0]] = [memcached[0]]
                else:
                    memcached = ['localhost', '11211']
                self._testing_fqdn_srv['_memcached.system._tcp.' + self._config['mesos']['domain']] = [{'name':memcached[0], 'port':memcached[1]}]
            self._testing[class_name] = False

class DiscoveryMesos(DiscoveryTestingTemplate, surok.discovery.DiscoveryMesos):
    pass

class DiscoveryMarathon(DiscoveryTestingTemplate, surok.discovery.DiscoveryMarathon):
    pass

class Discovery(surok.discovery.Discovery):
    def __init__(self):
        self._config = Config()
        self._logger = Logger()
        if 'mesos_dns' not in self._discoveries:
            self._discoveries['mesos_dns'] = DiscoveryMesos()
        if 'marathon_api' not in self._discoveries:
            self._discoveries['marathon_api'] = DiscoveryMarathon()
        super().__init__()

class StoreMemory(surok.store.StoreMemory):
    def __init__(self, *args):
        self._config = Config()
        self._logger = Logger()
        super().__init__(*args)

class StoreFiles(surok.store.StoreFiles):
    def __init__(self, *args):
        self._config = Config()
        self._logger = Logger()
        super().__init__(*args)

class StoreMemcached(surok.store.StoreMemcached):
    def __init__(self, *args):
        self._config = Config()
        self._logger = Logger()
        self._discovery = Discovery()
        super().__init__(*args)

class Store(surok.store.Store):
    def __init__(self, *args):
        self._config = Config()
        self._logger = Logger()
        if 'memory' not in self._stores:
            self._stores['memory'] = StoreMemory()
        if 'files' not in self._stores:
            self._stores['files'] = StoreFiles()
        if 'memcached' not in self._stores:
            self._stores['memcached'] = StoreMemcached(self)
        super().__init__(*args)

class LoadModules(surok.apps.LoadModules):
    pass

class Apps(surok.apps.Apps):
    def __init__(self):
        self._config = Config()
        self._logger = Logger()
        self._store = Store()
        self._discovery = Discovery()
        self._loadmodule = LoadModules()
        super().__init__()

class Test01_Logger(unittest.TestCase):
    def test_01_logger_default_level(self):
        logger = Logger()
        self.assertEqual(logger.get_level(), 'info')

    def test_02_logger_output_levels(self):
        message='log message'
        tests={
            'debug':{
                'assertIn':['ERROR: {}','WARNING: {}','INFO: {}','DEBUG: {}'],
                'assertNotIn':[]
            },
            'info':{
                'assertIn':['ERROR: {}','WARNING: {}','INFO: {}'],
                'assertNotIn':['DEBUG: {}']
            },
            'warning':{
                'assertIn':['ERROR: {}','WARNING: {}'],
                'assertNotIn':['INFO: {}','DEBUG: {}']
            },
            'error':{
                'assertIn':['ERROR: {}'],
                'assertNotIn':['WARNING: {}','INFO: {}','DEBUG: {}']
            }
        }
        logger = Logger()
        for value01 in tests.keys():
            logger.reset()
            logger.set_level(value01)
            logger.error(message)
            logger.warning(message)
            logger.info(message)
            logger.debug(message)
            resmessage=logger.geterr()+logger.getout()
            for test_name in tests[value01].keys():
                for test_value in tests[value01][test_name]:
                    with self.subTest(msg='Testing Logger for ...', loglevel=value01):
                        test_message=test_value.format(message)
                        eval('self.{}(test_message,resmessage)'.format(test_name))

class Test02_LoadConfig(unittest.TestCase):

    def test_01_default_values(self):
        config=Config()
        with self.subTest(msg="Testing default values for Config...\nConfig:\n" + config.dump()):
            self.assertEqual(config.get('confd'), '/etc/surok/conf.d')
            self.assertEqual(config.get('default_discovery'), 'mesos_dns')
            self.assertEqual(config.get('loglevel'), 'info')
            self.assertEqual(dict(config.get('marathon',{})).get('enabled'), False)
            self.assertEqual(dict(config.get('mesos',{})).get('enabled'), False)
            self.assertEqual(dict(config.get('memcached',{})).get('enabled'), False)
            self.assertEqual(dict(config.get('files',{})).get('enabled'), False)
            self.assertEqual(dict(config.get('files',{})).get('path'), '/var/tmp')
            self.assertEqual(config.get('version'), '0.7')
            self.assertEqual(config.get('wait_time'), 20)
            self.assertEqual(config.get('default_store'), 'memory')
        config.clear()

    def test_02_main_conf_loader(self):
        tests = {
            '6a6d3844e6964f6be2418b7439169632d626f638': '/usr/share/surok/conf/surok_07.json',
            'ac17e62f9082ea5d3fca614ecb75a4da271cfd8b': '/usr/share/surok/conf/surok_08.json',
        }
        for test in tests.keys():
            logger = Logger('info')
            logger.reset()
            config=Config(tests[test])
            with self.subTest(msg="Testing hash load config for Config...\nConfig:\n" + config.dump()):
                self.assertEqual(config.hash(), test)
            with self.subTest(msg="Check logger ERR/OUT output for Config...\nConfig:\n" + config.dump()):
                self.assertEqual(logger.getout() + logger.geterr(), '')
            config.clear()

    def test_03_apps_config_loader(self):
        tests=[
            {
                'env':{},
                'self_check.json': 'c264d23a99facee701d68b90e1df590c1fc19d58',
                'marathon_check.json': '02ababe60de38f4bf527e604963d64857c8f8230'
            },
            {
                'env':{'SUROK_DISCOVERY_GROUP': 'xxx.yyy'},
                'self_check.json': 'e92c0982cce5b562f6e2cf09fb0776f6c3c76cf7',
                'marathon_check.json': '2e429365260af51b0da36a51ca3a601ee7409143'
            },
            {
                'env':{'MARATHON_APP_ID': '/yyy/xxx/zzz'},
                'self_check.json': 'e92c0982cce5b562f6e2cf09fb0776f6c3c76cf7',
                'marathon_check.json': '2e429365260af51b0da36a51ca3a601ee7409143'
            }
        ]
        config = Config({'confd': '/usr/share/surok/conf.d'})
        for test in tests:
            config['env'] = test['env']
            config.update_apps()
            for app in [config.apps[x] for x in config.apps]:
                with self.subTest(msg="Testing AppConfig for ...\n" + app.dump(), env=test['env'], conf_name=app.get('conf_name')):
                    self.assertEqual(app.hash(), test[app.get('conf_name')])
        config.clear()

    def test_04_main_config_change(self):
        tests={
            'confd':{
                'assertEqual': ['/var', '/var/tmp', '/etc/surok/conf.d'],
                'assertNotEqual': [20, '/var/tmp1', '/etc/surok/conf/surok.json', 1, None, True]
            },
            'default_discovery':{
                'assertEqual':['marathon_api', 'mesos_dns'],
                'assertNotEqual':[20, 'test', None]
            },
            'loglevel':{
                'assertEqual':['error', 'debug', 'info', 'warning'],
                'assertNotEqual':['errrr', 'DEBUG','warn', 'test', 1, None, True]
            },
            'version':{
                'assertEqual': ['0.7', '0.8'],
                'assertNotEqual': ['0,7', '07', '0.9', 0.7, 0.8, None]
            },
            'wait_time':{
                'assertEqual': [10, 15, 20],
                'assertNotEqual': ['10', '15', None, True]
            },
            'default_store':{
                'assertEqual': ['memcached', 'files', 'memory'],
                'assertNotEqual': ['File', '10', 15 , None, True]
            }
        }
        config = Config()
        for name01 in tests.keys():
            oldvalue = config.get(name01)
            for test_name in tests[name01].keys():
                for value01 in tests[name01][test_name]:
                    config.set_config({name01:value01})
                    test_value = config.get(name01)
                    with self.subTest(msg='Testing Config Change for values...', name=name01, value=value01, test_value=test_value):
                        eval('self.{}(test_value, value01)'.format(test_name))
            config.set(name01,oldvalue)
        config.clear()

class Test03_Discovery(unittest.TestCase):

    def test_01_discovery(self):
        tests={
            'T':{                                                                                   #mesos_enabled
                'T':{                                                                               #marathon_enabled
                    '0.7':{                                                                         #version
                        'mesos_dns':{                                                               #default_discovery
                            'marathon_check.json':'ef55fb10c20df700cb715f4836eadb2d0cfa9cc1',       #app['conf_name']
                            'self_check.json':'53b8ddc27e357620f01ea75a7ab827cd90c77446'
                        },
                        'marathon_api':{
                            'marathon_check.json':'ef55fb10c20df700cb715f4836eadb2d0cfa9cc1',
                            'self_check.json':'53b8ddc27e357620f01ea75a7ab827cd90c77446'
                        }
                    },
                    '0.8':{
                        'mesos_dns':{
                            'marathon_check.json':'01c3a7ed5830c08d3469dca57cde4c9c1d90f34d',
                            'self_check.json':'27c0ffd26da16ccaf63280946076e39265e0b3e8'
                        },
                        'marathon_api':{
                            'marathon_check.json':'01c3a7ed5830c08d3469dca57cde4c9c1d90f34d',
                            'self_check.json':'27c0ffd26da16ccaf63280946076e39265e0b3e8'
                        }
                    }
                },
                'F':{
                    '0.7':{
                        'mesos_dns':{
                            'marathon_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f',
                            'self_check.json':'53b8ddc27e357620f01ea75a7ab827cd90c77446'
                        },
                        'marathon_api':{
                            'marathon_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f',
                            'self_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f'
                        }
                    },
                    '0.8':{
                        'mesos_dns':{
                            'marathon_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f',
                            'self_check.json':'27c0ffd26da16ccaf63280946076e39265e0b3e8'
                        },
                        'marathon_api':{
                            'marathon_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f',
                            'self_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f'
                        }
                    }
                }
            },
            'F':{
                'T':{
                    '0.7':{
                        'mesos_dns':{
                            'marathon_check.json':'ef55fb10c20df700cb715f4836eadb2d0cfa9cc1',
                            'self_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f'
                        },
                        'marathon_api':{
                            'marathon_check.json':'ef55fb10c20df700cb715f4836eadb2d0cfa9cc1',
                            'self_check.json':'53b8ddc27e357620f01ea75a7ab827cd90c77446'
                        }
                    },
                    '0.8':{
                        'mesos_dns':{
                            'marathon_check.json':'01c3a7ed5830c08d3469dca57cde4c9c1d90f34d',
                            'self_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f'
                        },
                        'marathon_api':{
                            'marathon_check.json':'01c3a7ed5830c08d3469dca57cde4c9c1d90f34d',
                            'self_check.json':'27c0ffd26da16ccaf63280946076e39265e0b3e8'
                        }
                    }
                },
                'F':{
                    '0.7':{
                        'mesos_dns':{
                            'marathon_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f',
                            'self_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f'
                        },
                        'marathon_api':{
                            'marathon_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f',
                            'self_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f'
                        }
                    },
                    '0.8':{
                        'mesos_dns':{
                            'marathon_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f',
                            'self_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f'
                        },
                        'marathon_api':{
                            'marathon_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f',
                            'self_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f'
                        }
                    }
                }
            }
        }
        config = Config('/usr/share/surok/conf/surok_check.json')
        config['env'] = {'SUROK_DISCOVERY_GROUP': 'xxx.yyy'}
        discovery = Discovery()
        for mesos_enabled in tests:
            for marathon_enabled in tests[mesos_enabled]:
                for version in tests[mesos_enabled][marathon_enabled]:
                    for default_discovery in tests[mesos_enabled][marathon_enabled][version]:
                        config['default_discovery'] = default_discovery
                        config['mesos']['enabled'] = mesos_enabled == 'T'
                        config['marathon']['enabled'] = marathon_enabled == 'T'
                        config['version'] = version
                        config.update_apps()
                        discovery.update_data()
                        for app in [config.apps[x] for x in config.apps]:
                            conf_name = app.get('conf_name')
                            res = discovery.resolve(app)
                            with self.subTest(msg="Testing Discovery for values...\nConfig:\n" + config.dump() +
                                                  "\nApp config:\n" + app.dump() +
                                                  "\nDiscovery dump:\n" + json.dumps(res, sort_keys=True, indent=2),
                                                  conf_name=conf_name,
                                                  mesos_enabled=mesos_enabled,
                                                  marathon_enabled=marathon_enabled,
                                                  version=version,
                                                  default_discovery=default_discovery):
                                if tests[mesos_enabled][marathon_enabled][version][default_discovery].get(conf_name):
                                    self.assertEqual(hashlib.sha1(json.dumps(res, sort_keys=True).encode()).hexdigest(),
                                                      tests[mesos_enabled][marathon_enabled][version][default_discovery][conf_name])

        config.clear()

class Test04_Store(unittest.TestCase):
    def test01_Store_Objects(self):
        store = Store()
        logger = Logger()
        logger.reset()
        conf = {'217c2c25755ce4ca91046d21c3243b7f7589bf73': {'dest': '/tmp/test.dest', 'value': 'Testing config'},
                '3ef62a84abe248f25c91e7fac9da6d581ffc3461': {'env': 'TEST', 'value': 'Testing environment'},
                'f9ac6090c76fd9e62fb0319abcea7ebb2266fab2': {'localid': 'TEST', 'data': {
                    'confd': '/usr/share/surok/conf.d',
                    'default_discovery': 'mesos_dns',
                    'default_store': 'memory',
                    'files': {
                        'enabled': False,
                        'path': '/var/tmp'
                    },
                    'loglevel': 'info',
                    'marathon': {
                        'enabled': False,
                        'force': True,
                        'host': 'http://marathon.mesos:8080',
                        'restart': False
                    },
                    'memcached': {
                        'discovery': {
                            'enabled': False
                        },
                        'enabled': True,
                        'host': 'localhost:11211'
                    },
                    'mesos': {
                        'domain': 'marathon.mesos',
                        'enabled': False
                    },
                    'version': '0.8',
                    'wait_time': 20
                }
            }
        }

        conf['217c2c25755ce4ca91046d21c3243b7f7589bf73'].update({'hash':hashlib.sha1(conf['217c2c25755ce4ca91046d21c3243b7f7589bf73']['value'].encode()).hexdigest(),
                                                                 'hashid': hashlib.sha1(conf['217c2c25755ce4ca91046d21c3243b7f7589bf73']['dest'].encode()).hexdigest()})
        conf['3ef62a84abe248f25c91e7fac9da6d581ffc3461'].update({'hash': hashlib.sha1(conf['3ef62a84abe248f25c91e7fac9da6d581ffc3461']['value'].encode()).hexdigest(),
                                                                 'hashid': hashlib.sha1(str('env:' + conf['3ef62a84abe248f25c91e7fac9da6d581ffc3461']['env']).encode()).hexdigest()})
        conf['f9ac6090c76fd9e62fb0319abcea7ebb2266fab2'].update({'hash': hashlib.sha1(json.dumps(conf['f9ac6090c76fd9e62fb0319abcea7ebb2266fab2']['data'], sort_keys = True).encode()).hexdigest(),
                                                                 'hashid': hashlib.sha1(str('data:'+conf['f9ac6090c76fd9e62fb0319abcea7ebb2266fab2']['localid']).encode()).hexdigest()})
        tests = [
            {
                'name': 'memory',
                'store': StoreMemory()
            },
            {
                'enabled': True,
                'name': 'files',
                'store': StoreFiles()
            },
            {
                'enabled': True,
                'name': 'memcached',
                'store': StoreMemcached()
            }
        ]

        for test in tests:
            config = Config('/usr/share/surok/conf/surok_check.json')
            store = test['store']
            store.check()
            with self.subTest(msg="Testing enabled for default {0} object...\nConfig:\n{1}".format(store.__class__.__name__, config), test=test):
                self.assertEqual(store.enabled(), test['name'] == 'memory') # Enabled only for memory store

            if test.get('enabled'):
                config[test['name']]['enabled'] = True

            if test.get('name') == 'memcached':
                config['memcached']['host'] = 'localhost:11211'
                if os.environ.get('MEMCACHE_PORT'):
                    config['memcached']['host'] = os.environ['MEMCACHE_PORT'].split('/')[2]

            store.check()
            with self.subTest(msg="Testing enabled for {0} object...\nConfig:\n{1}".format(store.__class__.__name__, config), test=test):
                self.assertEqual(store.enabled(), True)
            for key in conf:
                store_data = store.get(conf[key]['hashid'])
                with self.subTest(msg="Testing get keys from empty {0} object...\nKey:\n{1}".format(store.__class__.__name__, json.dumps(key, sort_keys = True)), test=test):
                    self.assertEqual(store_data, None)
                if conf[key].get('dest'):
                    store.set(conf[key]['hashid'], {'hash': conf[key].get('hash'), 'dest': conf[key].get('dest')})
                elif conf[key].get('env'):
                    store.set(conf[key]['hashid'], {'hash': conf[key].get('hash'), 'env': conf[key].get('env')})
                else:
                    store.set(conf[key]['hashid'], {'hash': conf[key].get('hash')})

            keys = list(store.keys())
            keys.sort()
            with self.subTest(msg="Testing set keys for {0} object...\nKeys:\n{1}".format(store.__class__.__name__, json.dumps(keys, sort_keys = True)), test=test):
                self.assertEqual(hashlib.sha1(json.dumps(keys, sort_keys=True).encode()).hexdigest(), '479f31609545203de17cc9ba71e649003966388d')

            for key in conf.keys():
                store_data = store.get(conf[key]['hashid'])
                store_data['hashid'] = conf[key]['hashid']
                store_data = json.dumps(store_data, sort_keys=True)
                with self.subTest(msg="Testing set/get data for {0} object...\nStore data:\n{1}".format(store.__class__.__name__, store_data), key=key, test=test):
                    self.assertEqual(hashlib.sha1(store_data.encode()).hexdigest(), key)
                    store.delete(conf[key]['hashid'])
            keys=list(store.keys())
            with self.subTest(msg="Testing delete keys for {0} object...".format(store.__class__.__name__), keys=keys, test=test):
                self.assertEqual(keys,[])
            with self.subTest(msg="Check logger ERR/OUT output for Config...\nConfig:\n" + config.dump(), test=test):
                self.assertEqual(logger.getout() + logger.geterr(), '')
            config.clear()

    def test02_Main_Store(self):
        logger = Logger()
        logger.reset()
        conf = {'217c2c25755ce4ca91046d21c3243b7f7589bf73': {'dest': '/tmp/test.dest', 'value': 'Testing config'},
                '3ef62a84abe248f25c91e7fac9da6d581ffc3461': {'env': 'TEST', 'value': 'Testing environment'},
                'f9ac6090c76fd9e62fb0319abcea7ebb2266fab2': {'localid': 'TEST', 'data': {
                    'confd': '/usr/share/surok/conf.d',
                    'default_discovery': 'mesos_dns',
                    'default_store': 'memory',
                    'files': {
                    'enabled': False,
                        'path': '/var/tmp'
                    },
                    'loglevel': 'info',
                    'marathon': {
                        'enabled': False,
                        'force': True,
                        'host': 'http://marathon.mesos:8080',
                        'restart': False
                    },
                    'memcached': {
                        'discovery': {
                            'enabled': False
                        },
                        'enabled': True,
                        'host': 'localhost:11211'
                    },
                    'mesos': {
                        'domain': 'marathon.mesos',
                        'enabled': False
                    },
                    'version': '0.8',
                    'wait_time': 20
                }
            }
        }
        conf_update = {'8f6357358fba9a1f5162f6603ae54ccdf573cf7f': {'dest': '/tmp/test.dest', 'value': 'New testing config'},
                       '0346fc7691daa29001ff92155b57f9b6abeeaed8': {'env': 'TEST', 'value': 'New testing environment'},
                       'fb6af582df2a771fe731c3a0898485fc6268c66d': {'localid': 'TEST', 'data': {}}}
        store = Store()
        config = Config()
        with self.subTest(msg="Check logger ERR/OUT output for Store init...\nConfig:\n{0}".format(config.dump())):
            self.assertEqual(logger.getout() + logger.geterr(), '')
        for conf_store in ['memory', 'files', 'memcached', 'memcached_discovery']:
            logger.reset()
            config.clear()
            config.set_config('/usr/share/surok/conf/surok_check.json')
            if conf_store == 'memcached_discovery':
                config['default_store'] = 'memcached'
                config['memcached'] =  {'enabled': True,
                                        'discovery': {
                                            'enabled': True,
                                            'service': 'memcached',
                                            'group': 'system'}}
                config['mesos']['enabled'] = True
                discovery = Discovery()
                discovery.update_data()
            else:
                if conf_store in ['files', 'memcached']:
                    config[conf_store]['enabled'] = True
                config['default_store'] = conf_store
                if conf_store == 'memcached':
                    config['memcached']['host'] = 'localhost:11211'
                    if os.environ.get('MEMCACHE_PORT'):
                        config['memcached']['host'] = os.environ['MEMCACHE_PORT'].split('/')[2]
            store.check()

            for key in conf.keys():
                store.set(conf[key])
            keys = list(store.keys())
            keys.sort()
            hash_keys = hashlib.sha1(json.dumps(keys, sort_keys=True).encode()).hexdigest()
            discovery_key = [x for x in keys if x not in conf_update]
            with self.subTest(msg="Testing set keys for Store({0}) object...\nConfig:\n{1}".format(conf_store, config.dump()), keys = keys, discovery_key = discovery_key):
                self.assertEqual(len(discovery_key), 1 if conf_store == 'memcached_discovery' else 0)

            for key in conf.keys():
                store_data = store.get(conf[key])
                store_json = store_data.copy()
                del store_json['store']
                store_json = json.dumps(store_json, sort_keys=True)
                orig_data = json.dumps(conf[key], sort_keys=True, indent=2)
                with self.subTest(msg="Testing set/get data for Store({0}) object...\nConfig:\n{1}\nStore data:\n{2}\nOrigin data:\n{3}".format(conf_store, config.dump(), store_json, orig_data),
                                  key = key, store = store_data.get('store')):
                    self.assertEqual(hashlib.sha1(store_json.encode()).hexdigest(), key)
                    self.assertEqual(store_data.get('store'), config['default_store'])
                    store.delete(conf[key])

            keys=list(store.keys())
            with self.subTest(msg="Testing delete keys for Store({0}) object...\nConfig:\n{1}".format(conf_store, config.dump()), keys = keys):
                self.assertEqual(keys, discovery_key)

            for key in conf.keys():
                store_data = json.dumps(store.get(conf[key]), sort_keys=True)
                with self.subTest(msg="Testing check_update for Store({0}) object...\nConfig:\n{1}\nStore data:\n{2}".format(conf_store, config.dump(), store_data), keys = keys):
                    self.assertEqual(store.check_update(conf[key]),True)

            store.clear()
            keys = list(store.keys())
            keys.sort()
            with self.subTest(msg="Testing clear for Store({0}) object...\nConfig:\n{1}".format(conf_store, config.dump()), keys=keys):
                self.assertEqual(hashlib.sha1(json.dumps(keys, sort_keys=True).encode()).hexdigest(), hash_keys)

            for key in conf_update.keys():
                store_data = json.dumps(store.get(conf_update[key]), sort_keys = True)
                with self.subTest(msg="Testing update data with check_update for Store({0}) object...\nConfig:\n{1}\nStore data:\n{2}".format(conf_store, config.dump(), store_data), keys = keys):
                    self.assertEqual(store.check_update(conf_update[key]), True)

            store.check()
            store.clear()
            keys = list(store.keys())
            keys.sort()
            with self.subTest(msg="Testing update data with clear for Store({0}) object...\nConfig:\n{1}".format(conf_store, config.dump()), keys = keys):
                self.assertEqual(hashlib.sha1(json.dumps(keys, sort_keys=True).encode()).hexdigest(), hash_keys)

            store.check_update(conf['217c2c25755ce4ca91046d21c3243b7f7589bf73'])
            store.check()
            store.clear()
            keys = list(store.keys())
            keys.sort()
            test_keys = ['8f6357358fba9a1f5162f6603ae54ccdf573cf7f'] + discovery_key
            test_keys.sort()
            with self.subTest(msg = "Testing remove 1 key data with clear for Store({0}) object...\nConfig:\n{1}".format(conf_store, config.dump()), keys = keys, discovery_key = discovery_key):
                self.assertEqual(keys, test_keys)

            store.check()
            store.clear()
            keys=list(store.keys())
            keys.sort()
            with self.subTest(msg="Testing remove 2 key data with clear for Store({0}) object...\nConfig:\n{1}".format(conf_store, config.dump()), keys = keys):
                self.assertEqual(keys, discovery_key)

            output = logger.getout() + logger.geterr()
            with self.subTest(msg="Check logger ERR/OUT output for Store({0}) object...\nConfig:\n{1}\nOutput:\n{2}".format(conf_store, config.dump(), output)):
                self.assertEqual(output, '')
        config.clear()

class Test05_Apps(unittest.TestCase):
    def test01_Apps(self):
        def get_file(path):
            data = None
            if os.path.isfile(path):
                f = open(path, 'r')
                data = f.read()
                f.close()
            return data

        def hash_data(data):
            return None if data is None else hashlib.sha1(data.encode()).hexdigest()

        config = Config('/usr/share/surok/conf/surok_check.json')
        config['marathon']['enabled'] = True
        config['mesos']['enabled'] = True
        config['env'] = {'SUROK_DISCOVERY_GROUP': 'xxx.yyy'}
        logger = Logger()
        logger.reset()
        apps = Apps()
        apps.update()
        tests = {
            '/tmp/test_1': '162165ae96553d94b803728bb870e571c304de5d',
            '/tmp/test_2': 'e899d5ee7c5dd11e614a7c67abbb47f3ab1646fc',
            '/tmp/test_cmd': 'a325fb4bca52825ff80289a49f8a6fe2df32ff08',
            '/tmp/test_old': '4afc5ac4f1a2f0ec45596b798c311fe1fc9bfbbf'
        }
        tests_2 = {
            '/tmp/test_1': '162165ae96553d94b803728bb870e571c304de5d',
            '/tmp/test_2': None,
            '/tmp/test_cmd': 'a325fb4bca52825ff80289a49f8a6fe2df32ff08',
            '/tmp/test_old': None
        }

        for file_name in tests:
            data = get_file(file_name)
            with self.subTest(msg="Testing result for Apps object...\nFile:\n{0}\nData:\n{1}".format(file_name, data)):
                self.assertEqual(hash_data(data), tests[file_name])
        with self.subTest(msg="Testing environments 1 for Apps object...\nFile:\n{0}\nData:\n{1}".format(file_name, data)):
             self.assertEqual(hash_data(os.environ.get('TEST1')), '3d6c95ac5893fea2bfdc56ceb286f1f168754bc3')
             self.assertEqual(hash_data(os.environ.get('TEST2')), '5be7bb08d246fe9b4e7f35ee637baeea1c02948f')

        config.set_config({'confd': '/usr/share/surok/conf.d_2'})
        apps.update()
        for file_name in tests_2:
            data = get_file(file_name)
            with self.subTest(msg="Testing result for Apps object...\nFile:\n{0}\nData:\n{1}".format(file_name, data)):
                self.assertEqual(hash_data(data), tests_2[file_name])
        with self.subTest(msg="Testing environments 2 for Apps object...\nFile:\n{0}\nData:\n{1}".format(file_name, data)):
             self.assertEqual(hash_data(os.environ.get('TEST1')), '3d6c95ac5893fea2bfdc56ceb286f1f168754bc3')
             self.assertEqual(hash_data(os.environ.get('TEST2')), None)

        output = logger.getout() + logger.geterr()
        with self.subTest(msg="Check logger ERR/OUT output for Apps object...\nOutput:\n{0}".format(output)):
            self.assertNotIn(' ERROR: ', output)
            self.assertNotIn(' WARNING: ', output)

if __name__ == '__main__':
    unittest.main()
    sleep(1)
