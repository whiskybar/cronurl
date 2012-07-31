import os.path
from setuptools import setup, find_packages

VERSION = (0, 0, 0, 1)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

ROOT = os.path.dirname(__file__)
requirements = [line.strip() for line in open(os.path.join(ROOT, 'requirements.txt'))]

setup(
    name = 'cronurl',
    version = __versionstr__,
    description = 'A lightweight daemon for hitting URLs from cron',
    long_description = '\n'.join((
        'cronurl',
        '',
        'A service for reading URLs periodically.',
    )),
    author = 'Jiri Barton',
    author_email='jbar@tele3.cz',
    license = 'BSD',

    packages = find_packages(
        where = '.',
        exclude = ('test_cronurl', )
    ),
    entry_points = {
        'console_scripts': [
            'cronurl = cronurl.server:main',
        ],
    },

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = [
        'setuptools>=0.6b1',
    ] + requirements,
    test_suite='test_cronurl.run_tests.run_all'
)

