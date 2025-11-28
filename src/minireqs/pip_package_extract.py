# Copyright (C) 2025 Lei Liu
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import pandas as pd
import ast
import importlib
import importlib.metadata as md # Python 3.8+ required

import os
from pathlib import Path

# Utility function
def find_py_files(script_path):
    """
    Return a list of .py file paths from a file or a folder.
    
    Args:
        script_path (str or Path): path to a python file or folder
    
    Returns:
        List[Path]: list of .py file paths
    """
    script_path = Path(script_path)

    if script_path.is_file() and script_path.suffix == ".py":
        # Single file
        return [script_path.resolve()]
    
    elif script_path.is_dir():
        # Folder: recursively find all .py files
        py_files = list(script_path.rglob("*.py"))
        return [p.resolve() for p in py_files]
    
    else:
        # Not a valid file or folder
        print(f"Error: {script_path} is neither a .py file nor a directory.")
        return []

# Safely import a possibly valid import_name
# Unility function
def safe_import(name):
    """
    Import a module safely by progressively stripping attributes.
    Example:
        'google.cloud.storage' → try full, then try 'google.cloud', then 'google'
    """
    parts = name.split(".")
    for i in range(len(parts), 0, -1):
        module_name = ".".join(parts[:i])
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
    return None

# Find the corresponding pip install package requirements 
# of a name in import statement.
# Core function
def find_pip_pkg(import_name):

    module = safe_import(import_name)
    if module is None:
        print(f"WARNING: Cannot import {import_name}")
        return None, None
    
    module_path = getattr(module, "__file__", None)
    if not module_path:
        return None, None

    module_path = module_path.replace("\\", "/")

    best_match = None
    best_len = 0
    version = None

    for dist in md.distributions():
        for file in dist.files or []:
            f = str(file).replace("\\", "/")
            if f in module_path:
                if len(f) > best_len:
                    best_match = dist.metadata["Name"]
                    best_len = len(f)
                    version = dist.version

    return best_match, version

# Get the possible names of imports that are needed from a script file 
# Core function   
def get_imports(script_path):

    if not os.path.isfile(script_path):
        return []

    with open(script_path, 'r') as file:
        content = file.read()
        if not content.strip():  # empty or whitespace-only file
            return []  
        tree = ast.parse(content, filename=script_path)
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_name = alias.name
                imports.add(imported_name)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            imports.add(module_name)
            for alias in node.names:
                imported_name = alias.name
                imports.add(f"{module_name}.{imported_name}")
            
    list_imports = list(imports)
    additional_imports = [x.split('.')[0] for x in list_imports if '.' in x]
    
    return list(set( list_imports + additional_imports ))

# Find all pip install requirements from a py file or all py files in a folder
# Core function
def extract_pip_requirement(script_path = 'main.py', req_path = 'req_main.txt', QA=False):
    
    file_list = find_py_files(script_path)

    list_imports = []
    for i, file in enumerate(file_list):
        print(i, file)
        list_imports = list_imports + get_imports(file)

    if list_imports == []:
        print("List of imports is empty")
        return pd.DataFrame()

    list_imports = list(set(list_imports))    

    combine_pair = lambda pair: f"{pair[0]}={pair[1]}" if pair[0] is not None and pair[1] is not None else None

    df_pip_pkg = pd.DataFrame({
        'import_name': list_imports,
        'requirement': [combine_pair(find_pip_pkg(x)) for x in list_imports] 
        }).dropna(subset=['requirement'])
    
    if QA:
        print(df_pip_pkg.sort_values('requirement').reset_index(drop=True))    

    df_pip_pkg['requirement'].dropna().drop_duplicates().to_csv(req_path, index=False, header=False)

    df_pip_pkg['len_import'] = df_pip_pkg['import_name'].str.len()
    df_pip_pkg_out = df_pip_pkg.sort_values(['requirement','len_import'])\
        [['import_name','requirement']]\
            .drop_duplicates(subset=['requirement'], keep='first').reset_index(drop=True)
    return df_pip_pkg_out

if __name__ == '__main__':
    df_pip_package = extract_pip_requirement()
    print(df_pip_package)