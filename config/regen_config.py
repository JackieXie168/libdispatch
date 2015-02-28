#!/usr/bin/env python
# encoding: utf-8

import ConfigParser
import os
import re
import sys
import textwrap

HERE = os.path.dirname(__file__)
THIRD_PARTY = os.path.join(HERE, '../thirdparty')

sys.path.insert(1, os.path.join(THIRD_PARTY, 'click'))
import click


def make_symbol(s):
    return re.sub(r'[^A-Z0-9_]', '_', s.upper())


class ConfigFile(object):
    @classmethod
    def from_file(cls, fobj):
        parser = ConfigParser.SafeConfigParser(allow_no_value=True)
        parser.optionxform = str
        parser.readfp(fobj)
        return cls(parser)

    def __init__(self, parser):
        """ :type parser: ConfigParser.ConfigParser """
        self._parser = parser

    def iter_values(self, section_name):
        if not self._parser.has_section(section_name):
            return

        for option_name in self._parser.options(section_name):
            raw_value = self.try_get(section_name, option_name)
            yield option_name, raw_value

    def try_get(self, section_name, option_name):
        try:
            return (self._parser.get(section_name, option_name) or '').strip()
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            return None


@click.command()
@click.argument(
    'input_file',
    'config_file',
    type=click.File('rb'),
    required=True)
@click.argument('output_file', type=click.File('wb'), default='-')
def main(input_file, output_file):
    """
    Given a ConfigParser document listing the headers, declarations and
    functions libdispatch needs to know about, generates a CMake configuration
    file in the style of GNU Autoheader.

    \b
    The document is expected to contain the following sections, where each
    section contains a list of "options". Options can optionally have an
    associated value that is written into the config.h header as a C comment.

    The sections are:
        'headers': a list of headers to check for.
        'declarations': list of declarations to check for.
        'functions': list of functions to check for.
        'custom': list of custom entries for the header file.
        'prologue', 'epilogue': these sections, if present, should contain an
            option named 'value', whose contents is written out verbatim into
            the C header at the beginning or end, respectively.
    """
    document = ConfigFile.from_file(input_file)

    wrapper = textwrap.TextWrapper(
        width=80,
        subsequent_indent=' ' * 3,
        break_long_words=False)

    output_file.write('/* vim: set ft=c.cmake: */\n')

    prologue = document.try_get('prologue', 'value')
    if prologue:
        output_file.write(prologue)
        output_file.write('\n')

    for decl, help_text in document.iter_values('headers'):
        output_file.write('\n')
        if help_text:
            output_file.write(wrapper.fill("/* %s */" % help_text))
        else:
            output_file.write(wrapper.fill(
                "/* Define to 1 if you have the <%s> header file. */" % decl))
        output_file.write('\n')
        output_file.write("#cmakedefine HAVE_%s 1\n" % make_symbol(decl))

    for decl, help_text in document.iter_values('declarations'):
        output_file.write('\n')
        if help_text:
            output_file.write(wrapper.fill("/* %s */" % help_text))
        else:
            output_file.write(wrapper.fill(
                "/* Define to 1 if you have the declaration of `%s', and to "
                "0 if you don't. */" % decl))
        output_file.write('\n')
        output_file.write("#cmakedefine01 HAVE_DECL_%s\n" % make_symbol(decl))

    for func, help_text in document.iter_values('functions'):
        output_file.write('\n')
        if help_text:
            output_file.write(wrapper.fill("/* %s */" % help_text))
        else:
            output_file.write(wrapper.fill(
                "/* Define to 1 if you have the `%s' function. */" % func))
        output_file.write('\n')
        output_file.write("#cmakedefine HAVE_%s 1\n" % make_symbol(func))

    for decl, help_text in document.iter_values('custom'):
        if help_text:
            output_file.write('\n')
            output_file.write(wrapper.fill("/* %s */" % help_text))
        output_file.write('\n')
        output_file.write("#cmakedefine %s 1\n" % make_symbol(decl))

    epilogue = document.try_get('epilogue', 'value')
    if epilogue:
        output_file.write('\n')
        output_file.write(epilogue)
        output_file.write('\n')


if __name__ == '__main__':
    main()
