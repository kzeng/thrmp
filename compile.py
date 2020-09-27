import compileall
import os

compileall.compile_dir('./build/exe.win-amd64-3.6/router', force=True, maxlevels=10, legacy=True)

os.system('del .\\build\\exe.win-amd64-3.6\\router\\*.py')
# os.system('rename *.pyc *.py')

print("compile all python files ok.")
