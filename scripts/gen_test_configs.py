#!/usr/bin/env python
# encoding: utf-8

import click # pip install click
import constraint # pip install python-constraint
import yaml # pip install pyyaml

def solution_to_travis_entry(solution):
    env_dict = {}
    entry = {}

    entry['compiler'] = solution['compiler']
    env_dict['DISPATCH_COMPILER'] = solution['compiler']

    if solution['build_type'] == 'debug':
        env_dict.update(DISPATCH_BUILD_TYPE='Debug')
    elif solution['build_type'] == 'release':
        env_dict.update(DISPATCH_BUILD_TYPE='Release')

    if solution['sanitise']:
        env_dict.update(DISPATCH_SANITIZE='address,undefined')

    if solution['run_tests']:
        env_dict.update(DISPATCH_ENABLE_TEST_SUITE=1)

    sorted_env_entries = sorted(env_dict.iteritems())
    entry['env'] = ' '.join('%s=%s' % (k, v) for k, v in sorted_env_entries)
    return entry


@click.command()
@click.option(
    '--output', '-o', 'output_file', type=click.File('wb'), default='-')
def main(output_file):
    p = constraint.Problem()

    p.addVariable('compiler', ['clang', 'gcc'])
    p.addVariable('build_type', ['debug', 'release'])
    p.addVariable('sanitise', [True, False])
    p.addVariable('run_tests', [True, False])

    p.addConstraint(lambda compiler, run_tests, sanitise:
                    not compiler == 'gcc' or (not run_tests and not sanitise),
                    ('compiler', 'run_tests', 'sanitise'))
    p.addConstraint(lambda sanitise, run_tests, build_type:
                    not sanitise or (run_tests and build_type == 'release'),
                    ('sanitise', 'run_tests', 'build_type'))

    entries = map(solution_to_travis_entry, p.getSolutions())
    matrix = {'matrix': { 'include': entries}}
    yaml.dump(matrix, output_file)

if __name__ == '__main__':
    main()
