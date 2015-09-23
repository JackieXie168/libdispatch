import pytest
import subprocess
import os

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, '..')


@pytest.mark.parametrize('cc', ['clang', 'gcc'])
@pytest.mark.parametrize('filetype', ['c', 'c++'])
def test_header_compat(cc, filetype):
    ret = subprocess.call(
        [
            cc, '-x', filetype, '-I%s' % PROJECT_ROOT, '-fsyntax-only',
            os.path.join(PROJECT_ROOT, 'dispatch/dispatch.h')
        ])
    assert ret == 0


TESTS = [
    'after',
    'api',
    'c99',
    'cascade',
    'context_for_key',
    'data',
    'debug',
    'io',
    'io_net',
    'main_queue',
    'np',
    'overcommit',
    'pingpong',
    'plusplus',
    'priority',
    'proc',
    'queue_finalizer',
    'read',
    'readsync',
    'select',
    'sema',
    'starfish',
    'suspend_timer',
    'timer',
    'timer_bit31',
    'timer_bit63',
    'timer_set_time',
    'timer_timeout',
    'vm',
    pytest.mark.slow('concur'),
    pytest.mark.slow('drift'),
    pytest.mark.slow('group'),
    pytest.mark.slow('timer_short'),
    pytest.mark.xfail('apply'),
    pytest.mark.xfail('priority2'),
    pytest.mark.xfail('read2'),
    pytest.mark.xfail('vnode'),
]


@pytest.mark.parametrize('test', TESTS)
def test_dispatch(test):
    ret = subprocess.call(os.path.join(pytest.config.option.dispatch_test_dir,
                                       'dispatch_%s' % test))
    assert ret == 0
