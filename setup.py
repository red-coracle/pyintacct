from setuptools import find_packages, setup


NAME = 'pyintacct'
VERSION = '0.0.7'
DESCRIPTION = 'Python SDK for Intacct'
LONG_DESCRIPTION = open('README.md').read()
LICENSE = 'MIT'
AUTHOR = 'red-coracle'
AUTHOR_EMAIL = ''
URL = 'https://github.com/red-coracle/pyintacct'
PYTHON_VERSION = '>=3.6.0'
REQUIRES = ['requests >=2.22, <3.0',
            'jxmlease >= 1.0.1',
            'pydantic == 0.32.2']



setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    python_requires=PYTHON_VERSION,
    install_requires=REQUIRES,
    # test_suite='tests',
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7']
)
