#!/usr/bin/env python
# encoding: utf-8
"""
static_link.py
Applies DSO-like behaviour to static libraries. Multiple archives are merged
into a single archive, and, optionally, hidden symbols are made local.

Also takes a |--localize-hidden| option that points to a file containing an
explicit list of symbols to hide, one per line.

Inspiration:
- https://github.com/MLton/mlton/blob/master/bin/static-library
- https://github.com/DynamoRIO/dynamorio/blob/master/core/CMakeLists.txt
"""
import os
import pipes
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from os.path import join

HERE = os.path.dirname(__file__)
THIRD_PARTY = os.path.join(HERE, '../thirdparty')

sys.path.insert(1, os.path.join(THIRD_PARTY, 'click'))
import click
del sys.path[1]

VERBOSE = False


def shelljoin(args):
    return ' '.join(pipes.quote(arg) for arg in args)


def echo_err(*args, **kwargs):
    click.echo(*args, err=True, **kwargs)


def run(args):
    if VERBOSE:
        echo_err('+ %s' % shelljoin(args))
    subprocess.check_call(args)


def iter_hidden_symbols(objdump_path, object_file):
    """
    Uses objdump to filter the symbol list in |object_file| to those symbols
    marked as having hidden visibility.
    """
    cmd = [objdump_path, '-t', object_file]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    for line in iter(process.stdout.readline, ''):
        m = re.search(r'\.hidden (\w+)$', line)
        if not m:
            continue

        symbol = m.group(1)
        if re.match(r'__\S*get_pc_thunk', symbol):
            # Avoid localising GCC internal symbols. See links mentioned above.
            continue

        yield symbol

    process.wait()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd)

def iter_global_symbols(nm_path, object_file):
    """
    Iterates over symbols matched by `nm --defined-only --extern-only`
    """
    cmd = [
        nm_path,
        '--defined-only',
        '--extern-only',
        '--print-file-name',
        object_file]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    for line in iter(process.stdout.readline, ''):
        # print line
        m = re.search(r'\b(\w+)$', line)
        if not m: continue
        yield m.group(1)

    process.wait()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd)



@click.command()
@click.option(
    '--localize-hidden/--no-localize-hidden', default=True, show_default=True,
     help='Whether symbols with hidden visibility are made local.')
@click.option(
    '--keep-global-regex', default=r'.*', show_default=True, metavar='REGEX',
    help="Regex to determine which symbols are kept as global. (If "
    "--localize-hidden is set, this does NOT override it.)")
@click.option('--is-final-link/--no-is-final-link', default=False,
              help='See objcopy documentation for the -r, -Ur flags.')
@click.option('-o', '--output', default='archive.a', show_default=True,
              type=click.Path(dir_okay=False, resolve_path=True))
@click.option('--with-cc', 'cc', envvar='CC', default='cc')
@click.option('--cflags', envvar='CFLAGS', default='')
@click.option('--with-objcopy', 'objcopy', envvar='OBJCOPY', default='objcopy')
@click.option('--with-objdump', 'objdump', envvar='OBJDUMP', default='objdump')
@click.option('--with-ar', 'ar', envvar='AR', default='ar')
@click.option('--with-nm', 'nm', envvar='NM', default='nm')
@click.option('--with-ranlib', 'ranlib', envvar='RANLIB', default='ranlib')
@click.option('--verbose', '-v', is_flag=True, default=False)
@click.argument('archives', nargs=-1, required=True,
                type=click.Path(exists=True, dir_okay=False, readable=True,
                                resolve_path=True))
def main(
        cc,
        cflags,
        objcopy,
        objdump,
        ar,
        nm,
        ranlib,
        verbose,
        localize_hidden,
        keep_global_regex,
        is_final_link,
        output,
        archives):
    global VERBOSE
    if verbose:
        VERBOSE = True

    output_archive_dir, output_archive_name = os.path.split(output)
    output_archive_name_wo_ext, _ = os.path.splitext(output_archive_name)

    temp_dir = tempfile.mkdtemp('_%s' % output_archive_name_wo_ext)
    partial_link_path = join(
        temp_dir, '%s.o' % output_archive_name_wo_ext)
    symbol_list_path = join(
        temp_dir, '%s.locals' % output_archive_name_wo_ext)

    link_command = [cc]
    link_command.extend(shlex.split(cflags))
    link_command.extend([
        '-nostartfiles',
        '-nodefaultlibs',
        '-Wl,--build-id=none',
        is_final_link and '-Wl,-Ur' or '-Wl,-r',
        '-Wl,--whole-archive',
    ])
    link_command.extend(archives)
    link_command.extend([
        '-Wl,--no-whole-archive',
        '-o', partial_link_path
    ])
    run(link_command)

    with open(symbol_list_path, 'wb') as f:
        if localize_hidden:
            for symbol in iter_hidden_symbols(objdump, partial_link_path):
                f.write('%s\n' % symbol)

        for symbol in iter_global_symbols(nm, partial_link_path):
            if re.search(keep_global_regex, symbol):
                continue
            f.write('%s\n' % symbol)

    run([objcopy, '--localize-symbols', symbol_list_path, partial_link_path])
    run([ar, 'cr', join(temp_dir, output_archive_name), partial_link_path])
    run([ranlib, join(temp_dir, output_archive_name)])
    run(['mv', join(temp_dir, output_archive_name), output])
    run(['rm', '-fr', temp_dir])

if __name__ == '__main__':
    main()

