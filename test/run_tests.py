# -*- coding: utf-8 -*-

import os
import sys
from subprocess import Popen, PIPE

this_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
interpreter_path = os.path.abspath(sys.executable)
python_path = os.path.abspath(os.path.join(this_dir, '..'))


def before_test_1():
    pass


def after_test_1():
    pass


def before_test_2():
    config_content = "[APP]\n" \
                     + "DEVELOPMENT = True\n" \
                     + "DEBUG = True\n" \
                     + "SECRET_KEY = VERY-SECRET-K3Y\n" \
                     + "SQLALCHEMY_DATABASE_URI = postgresql://talhasch:@localhost:5434/wild_cat\n" \
                     + "SQLALCHEMY_POOL_SIZE = 100\n" \
                     + "SQLALCHEMY_TRACK_MODIFICATIONS = False\n" \
                     + "BASE_URL = http://0.0.0.0:5000\n" \
                     + "X_RATE = 1.23\n"

    with open(os.path.join(this_dir, 'config.ini'), 'w') as f:
        f.write(config_content)
        f.close()


def after_test_2():
    os.remove(os.path.join(this_dir, 'config.ini'))


def before_test_3():
    config_content = "[APP]\n" \
                     + "DEVELOPMENT = False\n" \
                     + "DEBUG = False\n" \
                     + "SQLALCHEMY_TRACK_MODIFICATIONS = False\n" \
                     + "X_RATE = 1.23\n"

    with open(os.path.join(this_dir, 'config.ini'), 'w') as f:
        f.write(config_content)
        f.close()

    config_content = "[APP]\n" \
                     + "DEVELOPMENT = True\n" \
                     + "DEBUG = True\n" \
                     + "SECRET_KEY = VERY-SECRET-K3Y\n" \
                     + "SQLALCHEMY_DATABASE_URI = postgresql://talhasch:@localhost:5434/db_name\n" \
                     + "SQLALCHEMY_POOL_SIZE = 100\n" \
                     + "BASE_URL = http://0.0.0.0:5000\n" \
                     + "[X_API]\n" \
                     + "KEY = fweffqdqfedefwefewf\n" \
                     + "SECRET = 312df121323\n" \
                     + "[FOO]\n"

    with open(os.path.join(this_dir, 'config.development.ini'), 'w') as f:
        f.write(config_content)
        f.close()


def after_test_3():
    os.remove(os.path.join(this_dir, 'config.ini'))
    os.remove(os.path.join(this_dir, 'config.development.ini'))


def before_test_4():
    config_content = "[APP]\n" \
                     + "DEVELOPMENT = False\n" \
                     + "DEBUG = False\n" \
                     + "SQLALCHEMY_TRACK_MODIFICATIONS = False\n" \
                     + "X_RATE = 1.23\n" \
                     + "BASE_URL = http://0.0.0.0:5000\n"

    with open(os.path.join(this_dir, 'temp', 'config.ini'), 'w') as f:
        f.write(config_content)
        f.close()

    config_content = "[APP]\n" \
                     + "BASE_URL = http://0.0.0.0:5003\n" \
                     + "X_RATE = 1.80\n"

    with open(os.path.join(this_dir, 'temp', 'config.production.ini'), 'w') as f:
        f.write(config_content)
        f.close()


def after_test_4():
    os.remove(os.path.join(this_dir, 'temp', 'config.ini'))
    os.remove(os.path.join(this_dir, 'temp', 'config.production.ini'))


test_list = [
    {
        "file": "test1.py",
        "env": {'PYTHONPATH': python_path},
        "before_test": before_test_1,
        "after_test": after_test_1
    },
    {
        "file": "test2.py",
        "env": {'PYTHONPATH': python_path},
        "before_test": before_test_2,
        "after_test": after_test_2
    },
    {
        "file": "test3.py",
        "env": {'PYTHONPATH': python_path},
        "before_test": before_test_3,
        "after_test": after_test_3
    },
    {
        "file": "test4.py",
        "env": {
            'PYTHONPATH': python_path,
            '__ENV__': 'PRODUCTION',
            '__ENV__APP_SQLALCHEMY_DATABASE_URI': 'postgresql://talhasch:@localhost:5434/db_name',
            '__ENV__APP_SQLALCHEMY_POOL_SIZE': '100',
            '__ENV__APP_SECRET_KEY': 'VERY-SECRET-K3Y',
            '__ENV__FOO_BAR': 'Lorem',
            '__ENV__APP_BASE_URL': 'http://0.0.0.0:5004'

        },
        "before_test": before_test_4,
        "after_test": after_test_4
    }
]

i = 1
for item in test_list:

    if callable(item['before_test']):
        item['before_test']()

    test_file_path = os.path.abspath(os.path.join(this_dir, item['file']))

    p = Popen([interpreter_path, test_file_path], env=item['env'], stdout=PIPE, stderr=PIPE)
    output, error = p.communicate()
    if p.returncode != 0:
        print("Test {} Failed\n---\nError code: {}\n---\nOutput: {}\n---\nError: {}\n" \
              .format(i, p.returncode, output, error))

    if callable(item['after_test']):
        item['after_test']()

    i += 1

print("All tests passed")
