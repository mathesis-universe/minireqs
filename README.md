# minireqs

A lightweight Python utility that automatically generates `requirements.txt` files by scanning Python files, detecting import statements, and identifying the corresponding PyPI packages with their installed versions.

## Purpose

Automatically extract minimal dependency requirements from your Python codebase, making it ideal for packaging, deployment, and environment reproduction.

##### Notes: (1) The package must be installed in the same Python environment as the project so it can detect the packages and versions actually in use. (2) Only detection of packages installed via pip has been tested so far. (3) Even if all packages are installed via pip, there is still a small chance that some required packages won’t be detected if they are never explicitly imported in your scripts. After installing the generated requirements in a clean/fresh environment (or building and running your Docker image), test again to identify any missing dependencies.

## Main Functions

### `extract_pip_requirement(script_path, req_path, QA=False)`
Main function that extracts pip requirements from a Python file or directory.

- **Parameters:**
  - `script_path`: Path to a Python file or directory (default: `'main.py'`)
  - `req_path`: Output path for requirements file (default: `'req_main.txt'`)
  - `QA`: If `True`, prints the results DataFrame
- **Returns:** DataFrame with import names and their corresponding pip package requirements

### `get_imports(script_path)`
Extracts all import statements from a Python file using AST parsing.

- **Parameters:** `script_path` - Path to a Python file
- **Returns:** List of import names found in the file

### `find_pip_pkg(import_name)`
Finds the corresponding PyPI package name and version for an import statement.

- **Parameters:** `import_name` - The import name (e.g., `'pandas'`, `'numpy'`)
- **Returns:** Tuple of `(package_name, version)` or `(None, None)` if not found

### Utility Functions
- `find_py_files(script_path)`: Recursively finds all `.py` files in a directory or returns a single file path
- `safe_import(name)`: Safely imports a module by progressively stripping attributes

## Installation

```bash
pip install minireqs
```

## Usage

```python
from minireqs.pip_package_extract import extract_pip_requirement

# Extract requirements from a file or directory
df = extract_pip_requirement('my_script.py', 'requirements.txt')
```

## Requirements

- Python >= 3.10
- pandas >= 2.2.2
- numpy > 2.0

