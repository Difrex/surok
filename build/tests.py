#!/usr/bin/python3
import unittest
import json
import os
import re
import sys
import surok.config
import surok.logger
import surok.discovery
import hashlib
from surok.config import Config

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
        "test.zzz0.test":['10.0.0.1','10.1.0.1'],
        "test.zzz1.test":['10.0.1.1','10.1.1.1'],
        "test.zzz2.test":['10.0.2.1','10.1.2.1'],
        "test.zzz3.test":['10.0.3.1','10.1.3.1']
    }
    _testing_fqdn_srv={}

    def __init__(self):
        super().__init__()
        self._orig_logger=surok.logger.Logger()

    def do_query_a(self,fqdn):
        res=self._testing_fqdn_a.get(fqdn,[])
        if res:
            return res
        else:
            self._orig_logger.error('Testing FQDN '+fqdn+' not found in test A records')
            sys.exit(2)

    def do_query_srv(self,fqdn):
        res=self._testing_fqdn_srv.get(fqdn,[])
        if res or fqdn.startswith('_tname_e.') or fqdn.find('._udp.'):
            return res
        else:
            self._orig_logger.error('Testing FQDN '+fqdn+' not found in test SRV records')
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
                                for fqdn in ['_'+tgen['serv'][pid]+'._'+tgen['name'][id]+'.xxx.yyy._'+prot+'.'+self._config['mesos'].get('domain'),
                                                                    '_'+tgen['name'][id]+'.xxx.yyy._'+prot+'.'+self._config['mesos'].get('domain')]:
                                    if not self._testing_fqdn_srv.get(fqdn):
                                        self._testing_fqdn_srv[fqdn]=[]
                                    self._testing_fqdn_srv[fqdn].append({'name':tgen['host'][id],'port':ports[pid]})

            self._testing[class_name]=False

class DiscoveryMesos(DiscoveryTestingTemplate,surok.discovery.DiscoveryMesos):
    pass

class DiscoveryMarathon(DiscoveryTestingTemplate,surok.discovery.DiscoveryMarathon):
    pass

class Discovery(surok.discovery.Discovery):
    _discoveries={}
    def __init__(self):
        self._config=Config()
        self._logger=Logger()
        if not self._discoveries.get('mesos_dns'):
            self._discoveries['mesos_dns']=DiscoveryMesos()
        if not self._discoveries.get('marathon_api'):
            self._discoveries['marathon_api']=DiscoveryMarathon()

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
        with self.subTest(msg='Testing default values for Config.', dump=config.dump()):
            self.assertEqual(config.get('confd'), '/etc/surok/conf.d')
            self.assertEqual(config.get('default_discovery'), 'mesos_dns')
            self.assertEqual(config.get('lock_dir'), '/var/tmp')
            self.assertEqual(config.get('loglevel'), 'info')
            self.assertEqual(dict(config.get('marathon',{})).get('enabled'), False)
            self.assertEqual(dict(config.get('mesos',{})).get('enabled'), False)
            self.assertEqual(dict(config.get('memcached',{})).get('enabled'), False)
            self.assertEqual(config.get('version'), '0.7')
            self.assertEqual(config.get('wait_time'), 20)

    def test_02_main_conf(self):
        config=Config('/etc/surok/conf/surok.json')
        with self.subTest(msg='Testing load config for Config.', dump=config.dump()):
            self.assertEqual(config.hash(), '545c20b322a6ba5fef9c7d2416d80178f26a924b')

    def test_03_apps_conf(self):
        tests=[
            {
                'env':{},
                'self_check.json':'a4e109b9fec696776fd3df091b607e9c1489748c',
                'marathon_check.json':'6be7f26d421d4a0a2e7b089184be0c0e3a50f986'
            },
            {
                'env':{'SUROK_DISCOVERY_GROUP':'xxx.yyy'},
                'self_check.json':'38ab770ff2ba69bf70673288425337ff3c18a807',
                'marathon_check.json':'7b0cb4eab2d8e0f901cc567df28b17279af21baa'
            },
            {
                'env':{'MARATHON_APP_ID':'/xxx/yyy/zzz'},
                'self_check.json':'cbd2a15179649d0e06f98bd64e024481a944d65c',
                'marathon_check.json':'08a382d14285feb1f22b92ba597ecf73d654a2e0'
            }
        ]
        config=Config({'confd':'/usr/share/surok/conf.d'})
        for test in tests:
            config.set('env',test['env'])
            config.update_apps()
            for app in config.apps:
                with self.subTest(msg='Testing AppConfig for ...', env=test['env'], conf_name=app.get('conf_name'), dump=app.dump()):
                    self.assertEqual(test[app.get('conf_name')],app.hash())

    def test_04_apps_conf(self):
        tests={
            'confd':{
                'assertEqual': ['/var', '/var/tmp', '/etc/surok/conf.d'],
                'assertNotEqual': [20, '/var/tmp1', '/etc/surok/conf/surok.json', 1, None, True]
            },
            'default_discovery':{
                'assertEqual':['marathon_api', 'mesos_dns'],
                'assertNotEqual':[20, 'test', None]
            },
            'lock_dir':{
                'assertEqual':['/var', '/etc/surok/conf.d', '/var/tmp'],
                'assertNotEqual':[20, '/var/tmp1', '/etc/surok/conf/surok.json', 1, None, True]
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
            }

        }
        config=Config({'confd':'/usr/share/surok/conf.d'})
        for name01 in tests.keys():
            oldvalue=config.get(name01)
            for test_name in tests[name01].keys():
                for value01 in tests[name01][test_name]:
                    config.set_config({name01:value01})
                    test_value=config.get(name01)
                    with self.subTest(msg='Testing Config Change for values...', name=name01, value=value01, test_value=test_value):
                        eval('self.{}(value01, test_value)'.format(test_name))
            config.set(name01,oldvalue)


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
                            'marathon_check.json':'2016238426eb8ee7df9c4c016b6aecbfdf251a9b',
                            'self_check.json':'b6279a3e8e2fbbc78c6b302ef109bd6e2b456d9f'
                        },
                        'marathon_api':{
                            'marathon_check.json':'2016238426eb8ee7df9c4c016b6aecbfdf251a9b',
                            'self_check.json':'b6279a3e8e2fbbc78c6b302ef109bd6e2b456d9f'
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
                            'self_check.json':'b6279a3e8e2fbbc78c6b302ef109bd6e2b456d9f'
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
                            'marathon_check.json':'2016238426eb8ee7df9c4c016b6aecbfdf251a9b',
                            'self_check.json':'bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f'
                        },
                        'marathon_api':{
                            'marathon_check.json':'2016238426eb8ee7df9c4c016b6aecbfdf251a9b',
                            'self_check.json':'b6279a3e8e2fbbc78c6b302ef109bd6e2b456d9f'
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
        config=Config('/etc/surok/conf/surok.json')
        config.set_config({'confd':'/usr/share/surok/conf.d'})
        config.set('env',{'SUROK_DISCOVERY_GROUP':'xxx.yyy'})
        discovery=Discovery()
        for mesos_enabled in tests.keys():
            for marathon_enabled in tests[mesos_enabled].keys():
                for version in tests[mesos_enabled][marathon_enabled].keys():
                    for default_discovery in tests[mesos_enabled][marathon_enabled][version].keys():
                        config.set_config({'default_discovery':default_discovery,
                                           'mesos':{'enabled':(mesos_enabled=='T')},
                                           'marathon':{'enabled':(marathon_enabled=='T')},
                                           'version':version})
                        discovery.update_data()
                        for app in config.apps:
                            conf_name=app.get('conf_name')
                            with self.subTest(msg='Testing Discovery for values...', config=config.dump(), conf_name=conf_name):
                                self.assertEqual(hashlib.sha1(json.dumps(discovery.resolve(app), sort_keys=True).encode()).hexdigest(),
                                                 tests[mesos_enabled][marathon_enabled][version][default_discovery][conf_name])

if __name__ == '__main__':
    unittest.main()
