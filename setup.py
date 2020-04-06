import os
from setuptools import setup, find_packages


def read(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    file = open(filepath, 'r')
    return file.read()


setup(
    name='tuneconfig',
    version='v0.5.0',
    author='Thiago P. Bueno',
    author_email='thiago.pbueno@gmail.com',
    description='Hyperparameter config file generator.',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    license='GNU General Public License v3.0',
    keywords=['hyperparameter-tuning', 'grid-search-hyperparameter'],
    url='https://github.com/thiagopbueno/tuneconfig',
    packages=find_packages(),
    scripts=[],
    install_requires=[
        "numpy",
        "pandas",
        "tqdm",
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
)
