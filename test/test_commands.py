"""
Test some twanager commands which map to the fastly api

This test requires that fastly.* keys are in tiddlywebconfig.py
and that those keys are not checked in. These tests only work
for @cdent as they test against the live api.

As such they are not tests, really, but learning exercises.
"""

import os
import pytest

from tiddlyweb.config import config
from tiddlyweb.manage import handle
from tiddlywebplugins.fastly.commands import initialize_commands

# skip if this is not cdent
pytestmark = pytest.mark.skipif("os.environ['USER'] != 'cdent'")


def setup_module(module):
    initialize_commands(config)


def test_service(capsys):
    handle(['', 'fastlyservice'])
    results, err = capsys.readouterr()

    assert '2013-09-12T10:56:29+00:00' in results


def test_version(capsys):
    handle(['', 'fastlyversion', '2'])
    results, err = capsys.readouterr()

    assert '2013-09-12T10:56:36+00:00' in results


def test_active_version(capsys):
    handle(['', 'fastlyactiveversion'])
    results, err = capsys.readouterr()
    assert results.strip() == '2'


def test_domain(capsys):
    handle(['', 'fastlydomain', '2', 'fastiddly.peermore.com'])
    results, err = capsys.readouterr()
    assert config['fastly.service_id'] in results


def test_purge_url(capsys):
    handle(['', 'fastlypurgeurl', 'fastiddly.peermore.com', '/bags'])
    results, err = capsys.readouterr()
    assert err == ''


def test_purge_service(capsys):
    handle(['', 'fastlypurgeservice'])
    results, err = capsys.readouterr()
    assert err == ''


def test_purge_key(capsys):
    handle(['', 'fastlypurgekey', 'BT:system'])
    results, err = capsys.readouterr()
    assert err == ''
