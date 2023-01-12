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
    author=MLStructFP.__author__,
    author_email=MLStructFP.__email__,
    classifiers=[
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python',
        'Topic :: Structural/Engineering'
    ],
    description=MLStructFP.__description__,
    include_package_data=True,
    install_requires=[
        # 'dill == 0.3.6',
        # 'glfw == 2.5.5',
        # 'glfw-toolbox == 1.1.0',
        # 'h5py == 2.10.0',
        # 'IPython == 8.8.0',
        # 'ipywidgets == 8.0.4',
        # 'Keras == 2.3.1',
        # 'keras_tqdm == 2.0.1',
        'matplotlib == 3.5.3',
        # 'meshpy == 2022.1.3',
        'nose2 == 0.12.0',
        # 'numba == 0.56.4',
        'numpy == 1.18.5',
        # 'objsize == 0.6.1',
        'opencv-python == 4.7.0.68',
        # 'pandas == 1.4.1',
        'Pillow == 9.4.0',
        'plotly == 5.11.0',
        # 'prettytable == 3.6.0',
        # 'pydot == 1.4.2',
        # 'PyOpenGL == 3.1.6',
        'requests == 2.28.1',
        # 'scipy == 1.8.0',
        # 'seaborn == 0.12.2',
        # 'sectionproperties == 2.1.5',
        # 'shapely == 2.0.0',
        'six == 1.16.0',
        # 'scikit-learn == 1.2.0',
        # 'tabulate == 0.9.0',
        # 'tensorboard == 2.2.2',
        # 'tensorflow-gpu == 2.2.2',  # Check https://www.tensorflow.org/install/gpu. Needs CUDA 10.1 + cuDNN 7.6.5
        # 'tqdm == 4.64.1',
        # 'triangle == 20220202'
    ],
    keywords=MLStructFP.__keywords__,
    name='MLStructFP',
    packages=find_packages(exclude=[
        '.idea',
        '.ipynb_checkpoints',
        'database',
        'test'
    ]),
    platforms=['any'],
    project_urls={
        'Bug Tracker': MLStructFP.__url_bug_tracker__,
        'Documentation': MLStructFP.__url_documentation__,
        'Source Code': MLStructFP.__url_source_code__
    },
    python_requires='>=3.8',
    url=MLStructFP.__url__,
    version=MLStructFP.__version__
)
