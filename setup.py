from setuptools import setup, find_packages

test_deps = ['pytest-cov',
             'pytest']

extras = {
    'test': test_deps,
}

setup(
    name='bidsify',
    version='0.0.1',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*",
                                    "tests"]),
    license='MIT',
    author='Dan Gale',
    long_description=open('README.md').read(),
    url='https://github.com/danjgale/bidsify',
    install_requires=[
        'numpy',
        'pandas',
        'natsort'
    ],
    tests_require=test_deps,
    extras_require=extras,
    setup_requires=['pytest-runner'],
    entry_points={
        'console_scripts': [
            'bidsify=bidsify.main:main'
            ]
        }
)
