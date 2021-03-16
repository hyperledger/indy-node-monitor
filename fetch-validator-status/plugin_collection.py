""" 
MIT License

Copyright (c) 2020 Guido Diepen
Git Hub Repo: https://github.com/gdiepen/python_plugin_example

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. 

Change History:
  - 15/01/2021 Modified from orginal.
"""

import inspect
import os
import sys
import pkgutil


class Plugin(object):
    """Base class that each plugin must inherit from. within this class
    you must define the methods that all of your plugins must implement
    """

    def __init__(self):
        self.index = None
        self.name = 'UNKNOWN'
        self.description = 'UNKNOWN'
        self.type = 'UNKNOWN'
        self.enabled = False

    def parse_args(self, argument):
        raise NotImplementedError

    def load_parse_args(self, argument):
        raise NotImplementedError

    def perform_operation(self, argument):
        """The method that we expect all plugins to implement. This is the
        method that our framework will call
        """
        raise NotImplementedError

class PluginCollection(object):
    """Upon creation, this class will read the plugins package for modules
    that contain a class definition that is inheriting from the Plugin class
    """

    def __init__(self, plugin_package):
        """Constructor that initiates the reading of all available plugins
        when an instance of the PluginCollection object is created
        """
        self.plugin_package = plugin_package
        self.reload_plugins()

    def reload_plugins(self):
        """Reset the list of all plugins and initiate the walk over the main
        provided plugin package to load all available plugins
        """
        self.plugins = []
        self.seen_paths = []
        # print(f'\nLooking for plugins under package {self.plugin_package}')
        self.walk_package(self.plugin_package)
        self.sort()

    async def apply_all_plugins_on_value(self, result, network_name, response, verifiers):
        """Apply all of the plugins with the argument supplied to this function
        """
        self.log(f'\033[38;5;37mRunning plugins...\033[0m\n')
        for plugin in self.plugins:
            if plugin.enabled:
                self.log(f'\033[38;5;37mRunning {plugin.name}...\033[0m')
                result = await plugin.perform_operation(result, network_name, response, verifiers)
                self.log((f'\033[38;5;37m{plugin.name} yields value\033[0m\n')) #{result}
            else:
                self.log(f"\033[38;5;3m{plugin.name} disabled.\033[0m\n")
        return result

    def walk_package(self, package):
        """Recursively walk the supplied package to retrieve all plugins
        """
        imported_package = __import__(package, fromlist=['blah'])

        for _, pluginname, ispkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
            if not ispkg:
                plugin_module = __import__(pluginname, fromlist=['blah'])
                clsmembers = inspect.getmembers(plugin_module, inspect.isclass)
                for (_, c) in clsmembers:
                    # Only add classes that are a sub class of Plugin, but NOT Plugin itself
                    if issubclass(c, Plugin) & (c is not Plugin):
                        # print(f'    Found plugin class: {c.__module__}.{c.__name__}')
                        self.plugins.append(c())


        # Now that we have looked at all the modules in the current package, start looking
        # recursively for additional modules in sub packages
        all_current_paths = []
        if isinstance(imported_package.__path__, str):
            all_current_paths.append(imported_package.__path__)
        else:
            all_current_paths.extend([x for x in imported_package.__path__])

        for pkg_path in all_current_paths:
            if pkg_path not in self.seen_paths:
                self.seen_paths.append(pkg_path)

                # Get all sub directory of the current package path directory
                child_pkgs = [p for p in os.listdir(pkg_path) if os.path.isdir(os.path.join(pkg_path, p))]

                # For each sub directory, apply the walk_package method recursively
                for child_pkg in child_pkgs:
                    self.walk_package(package + '.' + child_pkg)

    def sort(self):
        self.plugins.sort(key=lambda x: x.index, reverse=False)

    def get_parse_args(self, parser):
        for plugin in self.plugins:
            plugin.parse_args(parser)

    def load_all_parse_args(self, args):
        global verbose
        verbose = args.verbose
        if verbose: self.plugin_list()
        for plugin in self.plugins:
            plugin.load_parse_args(args)

    def log(self, *args):
        if verbose:
            print(*args, file=sys.stderr)

    def plugin_list(self):
        self.log("\033[38;5;37m--- Plug-ins ---\033[0m")
        for plugin in self.plugins:
            self.log(f"\033[38;5;37m{plugin.name}: {plugin.__class__.__module__}.{plugin.__class__.__name__}\033[0m")