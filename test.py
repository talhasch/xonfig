# -*- coding: utf-8 -*-

import os
import unittest
from configparser import ConfigParser, NoSectionError, NoOptionError

from xonfig import *

this_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


class Test1(unittest.TestCase):
    """
    Test with no configuration. There is no config file and there is no environment variable.
    """

    @classmethod
    def setUpClass(cls):
        # Delete all environment variables
        for key in [k for k, v in os.environ.items()]:
            del os.environ[key]

        refresh()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_01_config_type(self):
        # Test config object is instance of ConfigParser
        self.assertIsInstance(get_config(), ConfigParser)

    def test_01_get_env(self):
        # Detected environment should be None because no __ENV__ declared in environment variables
        self.assertEqual(get_env(), None)

    def test_02_empty_sections(self):
        # _config_file_detected should be None. No config file loaded.
        self.assertEqual(get_config_file_detected(), None)

    def test_03_empty_sections(self):
        # _sections should be {}. There is no section loaded neither file nor environment variables.
        self.assertEqual(get_sections(), {})

    def test_04_no_section(self):
        # KeyError should be raised because there is no section named 'SECT1'.
        with self.assertRaises(KeyError):
            get_section('SECT1')

    def test_05_no_section(self):
        # NoSectionError should be raised because there is no section named 'SECT1'.
        with self.assertRaises(NoSectionError):
            get_option('SECT1', 'OPT1')


class Test2(unittest.TestCase):
    """
    Test with config file. There is no environment variable.
    """

    @classmethod
    def setUpClass(cls):
        refresh()
        # Delete all environment variables
        for key in [k for k, v in os.environ.items()]:
            del os.environ[key]

        cls.config_dir = os.path.join(this_dir, 'test_temp')

        # Create temporary config file
        config_content = "[APP]\n" \
                         + "DEVELOPMENT = True\n" \
                         + "DEBUG = True\n" \
                         + "SECRET_KEY = VERY-SECRET-K3Y\n" \
                         + "SQLALCHEMY_DATABASE_URI = postgresql://talhasch:@localhost:5434/wild_cat\n" \
                         + "SQLALCHEMY_POOL_SIZE = 100\n" \
                         + "SQLALCHEMY_TRACK_MODIFICATIONS = False\n" \
                         + "BASE_URL = http://0.0.0.0:5000\n" \
                         + "X_RATE = 1.23\n"

        with open(os.path.join(cls.config_dir, 'config.ini'), 'w') as f:
            f.write(config_content)
            f.close()

        set_config_dir(cls.config_dir)

    @classmethod
    def tearDownClass(cls):
        # Delete temporary config file
        os.remove(os.path.join(cls.config_dir, 'config.ini'))

    def test_01_set_config_dir(self):
        # Config file loaded. It should not be None
        self.assertNotEqual(get_config_file_detected(), None)
        self.assertEqual(os.path.isfile(get_config_file_detected()), True)

    def test_02_set_config_dir(self):
        set_config_dir(None)

        # Config file not loaded. It should be None
        self.assertEqual(get_config_file_detected(), None)

    def test_03_set_config_dir(self):
        set_config_dir(self.config_dir)

        # Config file loaded again. It should not be None
        self.assertNotEqual(get_config_file_detected(), None)
        self.assertEqual(os.path.isfile(get_config_file_detected()), True)

    def test_04_get_section(self):
        self.assertIsInstance(get_section('APP'), dict)

    def test_05_get_section(self):
        # KeyError should be raised because there is no section named 'DB'.
        with self.assertRaises(KeyError):
            get_section('DB')

    def test_06_get_option(self):
        # Get option tests
        self.assertEqual(get_option('APP', 'DEBUG'), True)
        self.assertEqual(get_option('APP', 'SECRET_KEY'), 'VERY-SECRET-K3Y')
        self.assertEqual(get_option('APP', 'SQLALCHEMY_POOL_SIZE'), 100)
        self.assertEqual(get_option('APP', 'X_RATE'), 1.23)

    def test_07_get_option_by_dict(self):
        # Get option directly from dictionary
        self.assertEqual(get_section('APP')['DEVELOPMENT'], True)
        self.assertEqual(get_section('APP')['SECRET_KEY'], 'VERY-SECRET-K3Y')

    def test_08_get_option(self):
        # Should be raise NoOptionError
        with self.assertRaises(NoOptionError):
            self.assertEqual(get_option('APP', 'DEBUG1'), True)


class Test3(unittest.TestCase):
    """
    Test with environment variables. There is no config file
    """

    @classmethod
    def setUpClass(cls):
        # Delete all environment variables
        for key in [k for k, v in os.environ.items()]:
            del os.environ[key]

        os.environ['__ENV__'] = 'production'
        os.environ['__ENV__APP_DEBUG'] = 'True'
        os.environ['__ENV__APP_XRATE'] = '1.12'
        os.environ['__ENV__SECRET_KEY'] = '123'

        os.environ['__ENV__MYSECTION_A_CONFIG'] = 'lorem'

        refresh()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_01_get_env(self):
        # Environment should be production because it passed from variable
        self.assertEqual(get_env(), 'production')

    def test_02_get_sections(self):
        # There should be 2 section APP, MYSECTION
        self.assertIn('APP', get_sections())
        self.assertNotEqual(get_section('APP'), {})

        self.assertIn('MYSECTION', get_sections())
        self.assertNotEqual(get_section('MYSECTION'), {})

    def test_03_get_config(self):
        # Get option tests

        self.assertEqual(get_option('APP', 'DEBUG'), True)
        self.assertEqual(get_option('APP', 'XRATE'), 1.12)
        self.assertEqual(get_option('MYSECTION', 'A_CONFIG'), 'lorem')

        with self.assertRaises(NoOptionError):
            # Should raise no option error. Declared wrong. See setUpClass
            get_option('APP', 'SECRET_KEY')


class Test4(unittest.TestCase):
    """
    Test with environment variables and config file
    """

    @classmethod
    def setUpClass(cls):
        # Delete all environment variables
        for key in [k for k, v in os.environ.items()]:
            del os.environ[key]

        refresh()

        cls.config_dir = os.path.join(this_dir, 'test_temp')

        # Create temporary config file
        config_content = "[APP]\n" \
                         + "DEVELOPMENT = True\n" \
                         + "DEBUG = True\n" \
                         + "SECRET_KEY = VERY-SECRET-K3Y\n" \
                         + "SQLALCHEMY_DATABASE_URI = postgresql://talhasch:@localhost:5434/wild_cat\n" \
                         + "SQLALCHEMY_POOL_SIZE = 100\n" \
                         + "SQLALCHEMY_TRACK_MODIFICATIONS = False\n" \
                         + "BASE_URL = http://0.0.0.0:5000\n" \
                         + "X_RATE = 1.23\n"

        with open(os.path.join(cls.config_dir, 'config.ini'), 'w') as f:
            f.write(config_content)
            f.close()

        set_config_dir(cls.config_dir)

        os.environ['__ENV__APP_DEVELOPMENT'] = 'False'
        os.environ['__ENV__APP_BASE_URL'] = 'http://0.0.0.0:5002'

        os.environ['__ENV__DB_CACHE'] = 'False'

        read_env()

    @classmethod
    def tearDownClass(cls):
        # Delete temporary config file
        os.remove(os.path.join(cls.config_dir, 'config.ini'))

    def test_01_get_config(self):
        # get_option tests
        self.assertEqual(get_option('APP', 'DEBUG'), True)
        self.assertEqual(get_option('APP', 'DEVELOPMENT'), False)
        self.assertEqual(get_option('APP', 'BASE_URL'), 'http://0.0.0.0:5002')
        self.assertEqual(get_option('APP', 'X_RATE'), 1.23)

        self.assertEqual(get_option('DB', 'CACHE'), False)


if __name__ == '__main__':
    unittest.main()
