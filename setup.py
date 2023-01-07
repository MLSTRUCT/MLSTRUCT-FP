"""
SETUP
MLSTRUCTFP

Setup distribution.
"""

# Library imports
from setuptools import setup, find_packages
import MLStructFP

# Setup library
setup(
    author=MLAi.__author__,
    author_email=MLAi.__email__,
    classifiers=[
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python',
        'Topic :: Structural/Engineering'
    ],
    description=MLAi.__description__,
    include_package_data=True,
    install_requires=[
        'dill >= 0.3.3',
        'glfw >= 2.1.0',
        'glfw-toolbox >= 1.1.0',
        'h5py >= 2.10',
        'IPython >= 7.21',
        'ipywidgets >= 7.6.3',
        'keras == 2.3.1',  # No longer support for further versions of keras, 2.4.0 does not work
        'keras_tqdm >= 2.0.1',
        'matplotlib >= 3.4.3',
        'meshpy >= 2020.1',
        'nose >= 1.3.7',
        'numba >= 0.53.0',
        'numpy >= 1.18.5',
        'objsize >= 0.3.3',
        'opencv-python >= 4.5.1.48',
        'pandas >= 1.3.3',
        'pillow >= 8.1.2',
        'plotly >= 4.14.3',
        'prettytable >= 2.1.0',
        'pydot >= 1.4.2',
        'PyOpenGL >= 3.1.5',
        'requests >= 2.23.0',
        'scipy >= 1.6.1',
        'seaborn >= 0.11.1',
        'sectionproperties >= 2.0.3',
        'shap >= 0.39.0',
        'Shapely >= 1.7.1',  # https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
        'six >= 1.15.0',
        'sklearn',  # conda install scikit-learn
        'tabulate >= 0.8.9',
        'tensorboard == 2.2.2',
        'tensorflow-gpu == 2.2.2',  # Check https://www.tensorflow.org/install/gpu. Needs CUDA 10.1 + cuDNN 7.6.5
        'tqdm >= 4.59.0',
        'triangle >= 20200424'  # https://www.lfd.uci.edu/~gohlke/pythonlibs/#triangle
    ],
    keywords=MLAi.__keywords__,
    name='MLAi',
    packages=find_packages(exclude=[
        '.idea',
        '.ipynb_checkpoints',
        'data',
        'test'
    ]),
    platforms=['any'],
    project_urls={
        'Bug Tracker': MLAi.__url_bug_tracker__,
        'Documentation': MLAi.__url_documentation__,
        'Source Code': MLAi.__url_source_code__
    },
    python_requires='>=3.8',
    url=MLAi.__url__,
    version=MLAi.__version__
)
