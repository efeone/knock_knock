from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in knock_knock/__init__.py
from knock_knock import __version__ as version

setup(
	name="knock_knock",
	version=version,
	description="knock knock remind my Dockets",
	author="efeone Software Lab",
	author_email="info@efeone.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
