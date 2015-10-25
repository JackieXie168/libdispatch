#!/usr/bin/env python
# encoding: utf-8
import click
import jinja2
import shlex
import yaml
from pluginbase import PluginBase

JINJA_CONFIG = dict(
    keep_trailing_newline=True,  # newline-terminate generated files
    lstrip_blocks=True,  # so can indent control flow tags
    trim_blocks=True,  # so don't need {%- -%} everywhere
    undefined=jinja2.StrictUndefined)


@click.command()
@click.option('--config',
              type=click.File('rb'),
              default='config.yaml',
              show_default=True)
@click.option('--extra-var', '-v', 'extra_vars',
              metavar='KEY VALUE',
              multiple=True,
              type=(str, str, ))
@click.option('--plugins-dir', 'plugins_dirs',
              multiple=True,
              type=click.Path(file_okay=False,
                              exists=True))
@click.option('--template', type=click.File(), required=True)
@click.option('--output', '-o',
              default='-',
              type=click.File(mode='w',
                              atomic=True))
def main(config, plugins_dirs, extra_vars, template, output):
    """ Renders a Jinja2 template from the command line.  """
    jinja_env = jinja2.Environment(**JINJA_CONFIG)

    plugin_base = PluginBase(package='j2cli.plugins')
    plugin_source = plugin_base.make_plugin_source(
        searchpath=list(plugins_dirs))
    for plugin_name in plugin_source.list_plugins():
        plugin = plugin_source.load_plugin(plugin_name)
        plugin.setup(jinja_env)

    doc = yaml.load(config)
    user_vars = dict(
        (k.encode('utf8'), shlex.split(v.encode('utf8')))
        for k, v in extra_vars)

    context = dict(doc)
    context.update(user_vars)
    output.write(jinja_env.from_string(template.read()).render(context))


if __name__ == '__main__':
    main.main()
