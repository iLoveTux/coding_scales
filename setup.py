"""
setup.py for coding_scales.

Useful links:

https://pythonhosted.org/setuptools/setuptools.html#command-reference
https://pythonhosted.org/setuptools/setuptools.html#basic-use
https://pythonhosted.org/setuptools/setuptools.html#new-and-changed-setup-keywords
https://pypi.python.org/pypi?%3Aaction=list_classifiers
"""
import sys
from setuptools import setup

tests_require = ["nose", "flask_testing"]
if sys.version_info < (3,0):
    tests_require.append("mock")

setup(
    name = "coding_scales",
    version = "0.1.0",
    author = "iLoveTux",
    author_email = "me@ilovetux.com",
    description = ("A typing tutor with a twist of coding."),
    install_requires=[
        "flask",
        "flask_restful",
        "flask_login",
        "flask_sqlalchemy",
        "matplotlib",
        "numpy",
        "scipy",
    ],
    test_suite="nose.collector",
    tests_require=tests_require,
    license = "Affero",
    keywords = "programming coding practice",
    url = "https://github.com/ilovetux/coding_scales",
    packages=['coding_scales'],
    long_description="Long description",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
    ],
)
