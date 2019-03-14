"""choke: simple implementation of throttling mechanism."""

from setuptools import setup, find_packages

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Software Development']

with open('README.rst') as readme:
    LONG_DESCRIPTION = readme.read()

setup(
    name='choke',
    license='MIT',
    description=__doc__,
    use_scm_version=True,
    long_description=LONG_DESCRIPTION,
    platforms=["Linux", "Unix"],
    setup_requires=['setuptools_scm'],
    install_requires=['redis'],
    tests_require=['pytest', 'pytest-mock'],
    author='Konrad Jałowiecki <dexter2206@gmail.com>',
    author_email='dexter2206@gmail.com',
    packages=find_packages(exclude=["tests", "tests.*"]),
    keywords='throttling redis limit'
)
