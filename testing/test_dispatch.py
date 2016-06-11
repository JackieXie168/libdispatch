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
