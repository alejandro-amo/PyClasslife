"""Setuptools build hooks for PyClasslife distributions."""

from setuptools import setup
from setuptools.command.sdist import sdist as _sdist


class sdist(_sdist):
    """Exclude generated setuptools metadata from the source archive."""

    def make_release_tree(self, base_dir, files):
        files = [path for path in files if ".egg-info" not in path]
        super().make_release_tree(base_dir, files)


setup(cmdclass={"sdist": sdist})
