#!/usr/bin/env python
# encoding: utf-8
import sys
import fnmatch
import os

HERE = os.path.dirname(__file__)
THIRD_PARTY = os.path.join(HERE, '../thirdparty')

sys.path.insert(1, os.path.join(THIRD_PARTY, 'click'))
import click
del sys.path[1]

###############################################################################

SHARED_LIBRARY_PATTERNS = [
    '*dispatch*', '_os_object*', '_NSConcrete*', 'Block*', '_Block*', ]

STATIC_LIBRARY_PATTERNS = ['*dispatch*', '_os_object*', ]

@click.command()
@click.argument('output_dir', required=True,
                type=click.Path(exists=True, file_okay=False))
def main(output_dir):
    os.chdir(output_dir)

    with open('libdispatch_globals.version', 'wb') as f:
        f.write('{\n')
        f.write('  global: %s;\n' % '; '.join(SHARED_LIBRARY_PATTERNS))
        f.write('  local: *;\n')
        f.write('};\n')

    with open('libdispatch_globals.regex', 'wb') as f:
        f.write('%s\n' %
                '|'.join(map(fnmatch.translate, STATIC_LIBRARY_PATTERNS)))

if __name__ == '__main__':
    main()
