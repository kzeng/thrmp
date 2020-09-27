# python setup.py build
# python setup.py bdist_msi

import sys
from cx_Freeze import setup, Executable
# import matplotlib
import os
PYTHONDIR = 'F:\\Python36'
# PYTHON_DLL = PYTHONDIR + '\\DLLs\\'
os.environ['TCL_LIBRARY'] = PYTHONDIR + '\\tcl\\tcl8.6'
os.environ['TK_LIBRARY'] = PYTHONDIR + '\\tcl\\tk8.6'

build_exe_options = {
    # "packages": ["os"],
    'include_files':  
        [
            # PYTHON_DLL + 'tcl86t.dll', PYTHON_DLL + 'tk86t.dll',
            'Config.ini',
            'router', 'static', 'templates', 
            'GoogleChromePortable', 
        ],
    'includes':  
        [
            'jinja2', 'jinja2.ext', 'flask', 'csv', 'pandas', 'yaml',
            'threading', 
            # 'numpy', 'PIL', 
            'numpy',
            'openpyxl',
            # 'matplotlib',
            'numpy.core._methods', 'numpy.lib.format',
            # 'matplotlib.backends.backend_tkagg',
        ],
    'packages': ['encodings', 'asyncio'],
    # 'optimize': 2,
    'excludes' : ['scipy', 'wx', 'tornado', 'test', 'matplotlib', 'PyQt5', 'tcl', 'nbconvert', 'nbformat', 'notebook', 'jupyter_client', 'jupyter_core', 'PIL', 'ipykernel', 'ipython_genutils' ],
}

executables = [Executable(script='run.py',
               targetName="OSFP-DEBUG-GUI.exe",
               icon=".\\static\\assets\\favicon.ico")]

setup(
    name = 'OSFP-DEBUG-GUI',
    version = '3.0',
    description = 'OSFP DEBUG GUI',
    author = 'zengkai',
    author_email = 'kai.zeng@neophotonics.com',
    # Add includes to the options
    options = {'build_exe': build_exe_options}, 
    executables = executables
)
