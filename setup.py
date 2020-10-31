from setuptools import setup

setup(
    name='executor',
    version='0.1',
    py_modules=['executor'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        executor=executor.cli:cli
    ''',
)
