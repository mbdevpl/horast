"""Tests for setup scripts."""

import importlib
import itertools
import os
import pathlib
import runpy
import sys
import typing as t
import unittest

__updated__ = '2017-08-31'


def run_module(name: str, *args) -> None:
    backup_sys_argv = sys.argv
    sys.argv = [name + '.py'] + list(args)
    runpy.run_module(name, run_name='__main__')
    sys.argv = backup_sys_argv


def import_module(name: str = 'setup') -> 'module':
    setup_module = importlib.import_module(name)
    return setup_module


def import_module_member(module_name: str, member_name: str) -> t.Any:
    module = import_module(module_name)
    return getattr(module, member_name)


#def import_module_members(module_name: str, member_names: t.Iterable[str]) -> t.List[t.Any]:
#    module = import_module(module_name)
#    return [getattr(module, member_name) for member_name in member_names]


CLASSIFIERS_LICENSES = (
    'License :: OSI Approved :: Python License (CNRI Python License)',
    'License :: OSI Approved :: Python Software Foundation License',
    'License :: Other/Proprietary License',
    'License :: Public Domain')

CLASSIFIERS_PYTHON_VERSIONS = tuple("""Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.3
Programming Language :: Python :: 2.4
Programming Language :: Python :: 2.5
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 2 :: Only
Programming Language :: Python :: 3
Programming Language :: Python :: 3.0
Programming Language :: Python :: 3.1
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3 :: Only""".splitlines())

CLASSIFIERS_PYTHON_IMPLEMENTATIONS = tuple("""Programming Language :: Python :: Implementation
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: IronPython
Programming Language :: Python :: Implementation :: Jython
Programming Language :: Python :: Implementation :: MicroPython
Programming Language :: Python :: Implementation :: PyPy
Programming Language :: Python :: Implementation :: Stackless""".splitlines())

CLASSIFIERS_VARIOUS = (
    'Framework :: IPython',
    'Topic :: Scientific/Engineering',
    'Topic :: Sociology',
    'Topic :: Security :: Cryptography',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Version Control :: Git',
    'Topic :: System',
    'Topic :: Utilities')

CLASSIFIERS_LICENSES_TUPLES = tuple((_,) for _ in CLASSIFIERS_LICENSES) + ((),)

CLASSIFIERS_PYTHON_VERSIONS_COMBINATIONS = tuple((_,) for _ in CLASSIFIERS_PYTHON_VERSIONS)

CLASSIFIERS_PYTHON_IMPLEMENTATIONS_TUPLES = tuple((_,) for _ in CLASSIFIERS_PYTHON_IMPLEMENTATIONS)

#CLASSIFIERS_VARIOUS_PERMUTATIONS = tuple(itertools.chain.from_iterable(
#    itertools.permutations(..., n)
#    for n in range(...)
#    ))

CLASSIFIERS_VARIOUS_COMBINATIONS = tuple(itertools.combinations(
    CLASSIFIERS_VARIOUS, len(CLASSIFIERS_VARIOUS) - 1)) + (CLASSIFIERS_VARIOUS,)

ALL_CLASSIFIERS_VARIANTS = [
    licenses + versions + implementations + various
    for licenses in CLASSIFIERS_LICENSES_TUPLES
    for versions in CLASSIFIERS_PYTHON_VERSIONS_COMBINATIONS
    for implementations in CLASSIFIERS_PYTHON_IMPLEMENTATIONS_TUPLES
    for various in CLASSIFIERS_VARIOUS_COMBINATIONS]


class Tests(unittest.TestCase):
    """Test """

    def test_find_version(self):
        find_version = import_module_member('setup_boilerplate', 'find_version')
        cwd = pathlib.Path.cwd()
        directories = [
            path for path in cwd.iterdir() if pathlib.Path(cwd, path).is_dir() \
                and pathlib.Path(cwd, path, '__init__.py').is_file()
                and path.name != 'test']
        self.assertEqual(len(directories), 1, directories)
        result = find_version(directories[0].name)
        self.assertIsInstance(result, str)

    def test_find_packages(self):
        find_packages = import_module_member('setup_boilerplate', 'find_packages')
        results = find_packages()
        self.assertIsInstance(results, list)
        for result in results:
            self.assertIsInstance(result, str)

    def test_parse_readme(self):
        parse_readme = import_module_member('setup_boilerplate', 'parse_readme')
        result = parse_readme()
        self.assertIsInstance(result, str)

    def test_parse_requirements(self):
        parse_requirements = import_module_member('setup_boilerplate', 'parse_requirements')
        results = parse_requirements()
        self.assertIsInstance(results, list)
        for result in results:
            self.assertIsInstance(result, str)

    def test_find_required_python_ver(self):
        find_required_python_version = import_module_member(
            'setup_boilerplate', 'find_required_python_version')
        for variant in ALL_CLASSIFIERS_VARIANTS:
            with self.subTest(variant=variant):
                result = find_required_python_version(variant)
                if result is not None:
                    self.assertIsInstance(result, str)

    @unittest.skipUnless(os.environ.get('TEST_PACKAGING'), 'skipping packaging test')
    def test_bdist(self):
        run_module('setup', 'bdist')
        self.assertTrue(os.path.isdir('dist'))

    @unittest.skipUnless(os.environ.get('TEST_PACKAGING'), 'skipping packaging test')
    def test_bdist_wheel(self):
        run_module('setup', 'bdist_wheel')
        self.assertTrue(os.path.isdir('dist'))

    @unittest.skipUnless(os.environ.get('TEST_PACKAGING'), 'skipping packaging test')
    def test_clean(self):
        run_module('setup', 'bdist')
        self.assertTrue(os.path.isdir('build'))
        clean = import_module_member('setup_boilerplate', 'clean')
        clean()
        self.assertFalse(os.path.isdir('build'))

    @unittest.skipUnless(os.environ.get('TEST_PACKAGING'), 'skipping packaging test')
    def test_sdist(self):
        run_module('setup', 'sdist', '--formats=gztar,zip')
        self.assertTrue(os.path.isdir('dist'))
