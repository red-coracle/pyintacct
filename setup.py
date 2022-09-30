from setuptools import find_packages, setup


NAME = 'pyintacct'
VERSION = '0.1.1'
DESCRIPTION = 'Python SDK for Intacct'
LONG_DESCRIPTION = open('README.md').read()
LICENSE = 'MIT'
AUTHOR = 'red-coracle'
AUTHOR_EMAIL = ''
URL = 'https://github.com/red-coracle/pyintacct'
PYTHON_VERSION = '>=3.6.1'
REQUIRES = ['httpx >=0.23.0, <2.0',
            'jxmlease >= 1.0.3',
            'pydantic >= 1.10.0, <2.0.0']
EXTRAS = {
    'http2': ['httpx[http2] >=0.23.0, <2.0']
}


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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9']
)
