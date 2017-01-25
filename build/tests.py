import unittest
import json
import os
import re

class TestLoadConfig(unittest.TestCase):

    def test_main_conf(self):
        # Load base configurations
        surok_conf = '/etc/surok/conf/surok.json'
        # Read config file
        f = open(surok_conf, 'r')
        conf = json.loads(f.read())
        f.close()

        self.assertIn('confd', conf)
        self.assertTrue(os.path.isdir(conf['confd']))
        self.assertIn('wait_time', conf)
        self.assertIn('lock_dir', conf)
        self.assertTrue(os.path.isdir(conf['lock_dir']))


class TestLogger(unittest.TestCase):

    def test_debug(self):
        from surok.logger import Logger
        m = Logger()
        self.assertIn('DEBUG', m.testing('debug','log message'))

    def test_info(self):
        from surok.logger import Logger
        m = Logger()
        self.assertIn('INFO', m.testing('info','log message'))

    def test_warning(self):
        from surok.logger import Logger
        m = Logger()
        self.assertIn('WARNING', m.testing('warning','log message'))

    def test_error(self):
        from surok.logger import Logger
        m = Logger()
        self.assertIn('ERROR', m.testing('error','log message'))


class TestMemcachedDiscovery(unittest.TestCase):

    def test_discovery_memcache(self):
        from surok.system import discovery_memcached
        from surok.discovery import Discovery
        # Load base configurations
        surok_conf = '/etc/surok/conf/surok.json'
        # Read config file
        f = open(surok_conf, 'r')
        conf = json.loads(f.read())
        f.close()
        d=Discovery(conf)
        self.assertEqual(discovery_memcached(conf), [])


class TestGetGroup(unittest.TestCase):

    def test_get_group_from_service(self):
        from surok.discovery import DiscoveryTemplate
        d=DiscoveryTemplate({})
        self.assertEqual('xxx.yyy.zzz',d.get_group({'group':'xxx.yyy.zzz'}, {}))

    def test_get_group_from_env(self):
        from surok.discovery import DiscoveryTemplate
        d=DiscoveryTemplate({})
        self.assertEqual('xxx.yyy.zzz',d.get_group({}, {'env':{'SUROK_DISCOVERY_GROUP':'xxx.yyy.zzz'}}))

    def test_get_group_from_marathon_id(self):
        from surok.discovery import DiscoveryTemplate
        d=DiscoveryTemplate({})
        self.assertEqual('xxx.yyy.zzz',d.get_group({}, {'env':{'MARATHON_APP_ID':'/zzz/yyy/xxx/www'}}))


if __name__ == '__main__':
    unittest.main()
