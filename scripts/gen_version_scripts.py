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

GLOBAL_SYMBOL_PATTERNS = """
    *dispatch*
    _NSConcrete*
    _os_object*
    Block*
    _Block*
""".split()

@click.command()
@click.argument('output_dir', required=True,
                type=click.Path(exists=True, file_okay=False))
def main(output_dir):
    os.chdir(output_dir)

    with open('libdispatch_globals.version', 'wb') as f:
        f.write('{\n')
        f.write('  global: %s;\n' % '; '.join(GLOBAL_SYMBOL_PATTERNS))
        f.write('  local: *;\n')
        f.write('};\n')

    with open('libdispatch_globals.regex', 'wb') as f:
        f.write('%s\n' %
                '|'.join(map(fnmatch.translate, GLOBAL_SYMBOL_PATTERNS)))

if __name__ == '__main__':
    main()
