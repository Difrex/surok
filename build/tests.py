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
        self.assertIn('domain', conf)
        self.assertIn('wait_time', conf)
        self.assertIn('lock_dir', conf)
        self.assertTrue(os.path.isdir(conf['lock_dir']))


class TestLogger(unittest.TestCase):

    def test_info(self):
        from surok.logger import make_message
        m = make_message
        self.assertIn('INFO', m({'level': 'info', 'raw': 'log message'}))

    def test_warning(self):
        from surok.logger import make_message
        m = make_message
        self.assertIn('WARNING', m({'level': 'warning', 'raw': 'log message'}))

    def test_error(self):
        from surok.logger import make_message
        m = make_message
        self.assertIn('ERROR', m({'level': 'error', 'raw': 'log message'}))

    def test_info(self):
        from surok.logger import make_message
        m = make_message
        self.assertIn('DEBUG', m({'level': 'debug', 'raw': 'log message'}))


if __name__ == '__main__':
    unittest.main()
