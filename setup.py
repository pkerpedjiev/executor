import io
import os

from setuptools import setup

HERE = os.path.dirname(os.path.abspath(__file__))


def read(*parts, **kwargs):
    filepath = os.path.join(HERE, *parts)
    encoding = kwargs.pop("encoding", "utf-8")
    with io.open(filepath, encoding=encoding) as fh:
        text = fh.read()
    return text


def get_requirements(path):
    content = read(path)
    return [req for req in content.split("\n") if req != "" and not req.startswith("#")]


install_requires = get_requirements("requirements.txt")

setup(
    name="executor",
    version="0.1",
    py_modules=["executor"],
    packages=["executor"],
    install_requires=["Click",],
    entry_points="""
        [console_scripts]
        executor=executor.cli:cli
    """,
)
