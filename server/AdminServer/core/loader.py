#!/usr/bin/env python3
# License: GPL-3.0

from os import listdir
import importlib.util

class Loader():
    def __init__(self):
        self.help    = []
        self.modules = {}

    def create_help(self):
        # Base Help Menu
        data = """

        """
        # Add Data
        for x in self.help:
            data += """
            <tr>
                <td>{}</td>
                <td>{}</td>
            </tr>""".format(x['usage'], x['description'])
        # Return help table
        return data

    def load_file(self, name, path):
        # Dynamically import module by file path
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod


    def load_data(self):
        # Collect data in module file
        module_path = 'server/AdminServer/modules/'
        for module in listdir(module_path):
            if module.endswith('.py'):
                full_path = module_path+module
                m = self.load_file(module, full_path)
                tm = m.TransModule()
                # Collect help info for admin.html template
                self.help.append(
                    {'usage'        : tm.usage,
                     'description'  : tm.description}
                )
                # Collect class obj, prep for execution
                self.modules[tm.name] = tm

def get_help():
    # Get HTML menu to add to admin.html template
    tmp = Loader()
    tmp.load_data()
    return tmp.create_help()

def list_modules():
    # Get dict of modules to compare against cmd exec
    tmp = Loader()
    tmp.load_data()
    return tmp.modules

def exec_module(name, cmd):
    tmp = Loader()
    tmp.load_data()
    return tmp.modules[name].run(cmd)
