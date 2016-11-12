import unittest
import json
import os


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


if __name__ == '__main__':
    unittest.main()
