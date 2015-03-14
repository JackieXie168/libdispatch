#!/usr/bin/env python
# encoding: utf-8

import click
import re
import textwrap
import yaml


def make_symbol(s):
    return re.sub(r'[^A-Z0-9_]', '_', s.upper())


@click.command()
@click.argument(
    'input_file', 'config_file', type=click.File('rb'), required=True)
@click.argument('output_file', type=click.File('wb'), default='-')
def main(input_file, output_file):
    """
    Given a YAML document listing the headers, declarations and functions
    libdispatch needs to know about, generates a CMake configuration file in
    the style of GNU Autoheader.

    \b
    The document is expected to be a dictionary with the following (optional)
    keys:
        'headers': list of headers to check for
        'declarations': list of declarations to check for
        'functions': list of functions to check for
        'custom': list of dictionaries, keyed by the #define to add to the
            config file. The value is the text that will accompany the #define
            in the form of a C-style comment.
    """
    document = yaml.load(input_file)

    wrapper = textwrap.TextWrapper(
        width=80,
        subsequent_indent=' ' * 3,
        break_long_words=False)

    prologue = document.get('prologue', '')
    if prologue:
        output_file.write(prologue)
        output_file.write('\n')

    for decl in document.get('headers', []):
        output_file.write('\n')
        output_file.write(wrapper.fill(
            "/* Define to 1 if you have the <%s> header file. */" % decl))
        output_file.write('\n')
        output_file.write("#cmakedefine01 HAVE_%s\n" % make_symbol(decl))

    for decl in document.get('declarations', []):
        output_file.write('\n')
        output_file.write(wrapper.fill(
            "/* Define to 1 if you have the declaration of `%s', and to "
            "0 if you don't. */" % decl))
        output_file.write('\n')
        output_file.write(
            "#cmakedefine01 HAVE_DECL_%s\n" % make_symbol(decl))

    for func in document.get('functions', []):
        output_file.write('\n')
        output_file.write(
            wrapper.fill(
                "/* Define to 1 if you have the `%s' function. */" % func))
        output_file.write('\n')
        output_file.write("#cmakedefine01 HAVE_%s\n" % make_symbol(func))

    for entry in document.get('custom', []):
        for decl, text in entry.iteritems():
            output_file.write('\n')
            output_file.write(wrapper.fill("/* %s */" % text))
            output_file.write('\n')
            output_file.write("#cmakedefine01 %s\n" % make_symbol(decl))

    epilogue = document.get('epilogue', '')
    if epilogue:
        output_file.write('\n')
        output_file.write(epilogue)

if __name__ == '__main__':
    main()

