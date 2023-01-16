"""
MLSTRUCTFP - BUILD

Build file.
"""

import os
import sys

assert len(sys.argv) == 2, 'Argument is required, usage: build.py pip/twine'
mode = sys.argv[1].strip()

if mode == 'pip':
    if os.path.isdir('dist'):
        for k in os.listdir('dist'):
            if 'MLStructFP-' in k:
                os.remove(f'dist/{k}')
    if os.path.isdir('build'):
        for k in os.listdir('build'):
            if 'bdist.' in k or k == 'lib':
                os.system(f'rm -rf build/{k}')
    os.system(f'python setup.py sdist bdist_wheel')

elif mode == 'twine':
    if os.path.isdir('dist'):
        os.system(f'python -m twine upload dist/*')
    else:
        raise FileNotFoundError('Not distribution been found, execute build.py pip')

else:
    raise ValueError(f'Unknown mode {mode}')
