import os
from setuptools import setup
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "smart_utilities",
    version = "1.4",
    author = "smart-etech",
    author_email = "",
    description = ("Utilities Package "),
    license = "BSD",
    keywords = "utilities",
    url = "",
    packages=['smart_utils'],

    classifiers=[
        "Development Status :: 1 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)