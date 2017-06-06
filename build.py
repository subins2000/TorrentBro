import os
import sys


def buildResources():
    qrcFile = os.path.join(os.path.dirname(__file__),
                            'designer', 'resources.qrc')
    pyOutput = os.path.join('torrentbro', 'ui', 'resources.py')

    os.system('pyrcc5 {file} -o {output}'.format(
        file=qrcFile,
        output=pyOutput
    ))


def buildUI():
    from PyQt5.uic import compileUiDir

    designDir = os.path.join(os.path.dirname(__file__), 'designer')

    def uicmap(pyDir, pyFile):
        rtnDir = os.path.join('torrentbro', 'ui')
        rtnFile = pyFile

        return rtnDir, rtnFile

    compileUiDir(designDir, map=uicmap)


def _usage():
    import sys
    sys.stdout.write('''
Usage:
    build    - Build everything
    build ui - Build .py files from .ui files in ui directory.
''')


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]

    cmd = args[0]

    if 1 in args:
        mode = args[1]
    else:
        mode = None

    if cmd == 'build':
        if mode == 'resources':
            buildResources()
        elif mode == 'ui':
            buildUI()
        else:
            buildResources()
            buildUI()
    else:
        _usage()
        sys.exit(1)
