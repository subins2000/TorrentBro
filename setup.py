import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def build_resources():
    import os
    from PyQt5.pyrcc_main import main as pyrcc_main_func

    QRC_FILE = 'resources.qrc'
    PY_OUTPUT = os.path.join('src', 'resources.py')

    sys.argv = ['', '-o', PY_OUTPUT, QRC_FILE]
    pyrcc_main_func()


def build_ui():
    import os
    from PyQt5.uic import compileUiDir

    design_dir = os.path.join(os.path.dirname(__file__), 'designer')

    def uicmap(py_dir, py_file):
        rtn_dir = os.path.join('src', 'ui')
        rtn_file = py_file.replace('.py', '_ui.py')

        return rtn_dir, rtn_file

    compileUiDir(design_dir, map=uicmap)


def _usage():
    import sys
    sys.stdout.write('''
Usage:
    build ui -  Build .py files from .ui files in ui directory.
''')


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]

    cmd = args[0]
    mode = args[1]

    if cmd == 'build':
        if mode == 'resources':
            build_resources()
        elif mode == 'ui':
            build_ui()
        else:
            _usage()
            sys.exit(1)
    else:
        _usage()
        sys.exit(1)
