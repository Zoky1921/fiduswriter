import os
import subprocess
from pathlib import Path
from subprocess import call, check_call
from glob import glob
from setuptools import Command, find_namespace_packages, setup
from setuptools.command.sdist import sdist as _sdist
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
from setuptools.command.install import install
from setuptools.command.build_py import build_py as _build_py
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


def read(name):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), name)) as f:
        return f.read()


class compilemessages(Command):
    """A custom command to create *.mo files for each language."""

    description = "Create *.mo files to be included in the final package."
    user_options = []

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):

        for path in Path(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "fiduswriter/locale"
            )
        ).rglob("*.po"):
            command = ["msgfmt", "-o", path.name.replace(".po", ".mo"), path.name]
            self.announce(
                "Running command: %s in %s" % (str(" ".join(command)), path.parent),
                level=self.distribution.verbose,
            )
            check_call(command, cwd=path.parent)


# From https://github.com/pypa/setuptools/pull/1574
class build_py(_build_py):
    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        patterns = self._get_platform_patterns(
            self.exclude_package_data,
            package,
            package_dir,
        )

        excluded_module_files = []
        for pattern in patterns:
            excluded_module_files.extend(glob(pattern))

        for f in excluded_module_files:
            for module in modules:
                if module[2] == f:
                    modules.remove(module)
        return modules


class bdist_egg(_bdist_egg):
    def run(self):
        self.run_command("compilemessages")
        _bdist_egg.run(self)


class sdist(_sdist):
    """Custom build command."""

    def run(self):
        self.run_command("compilemessages")
        _sdist.run(self)


class bdist_wheel(_bdist_wheel):
    """Custom build command."""

    def run(self):
        self.run_command("compilemessages")
        _bdist_wheel.run(self)


cmdclass = {
    "compilemessages": compilemessages,
    "sdist": sdist,
    "build_py": build_py,
    "bdist_egg": bdist_egg,
    "bdist_wheel": bdist_wheel,
    "install": install,
}


setup(
    cmdclass=cmdclass,
    name="fiduswriter",
    version=read("fiduswriter/version.txt").splitlines()[0],
    description="A semantic wordprocessor for academic purposes",
    license="AGPL",
    author="Lund Info AB",
    author_email="mail@lundinfo.com",
    url="https://www.fiduswriter.org",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Framework :: Django :: 4.1",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Editors :: Word Processors",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: LaTeX",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Utilities",
    ],
    packages=find_namespace_packages(include=["fiduswriter"]),
    include_package_data=True,
    exclude_package_data={
        "": [
            "travis/*",
            "build/*",
            "fiduswriter/media/*",
            "fiduswriter/.transpile/*",
            "fiduswriter/static-transpile/*",
            "fiduswriter/static-collected/*",
            "fiduswriter/static-libs/*",
            "fiduswriter/venv/*",
            "fiduswriter/media/*",
            "fiduswriter/static-transpile/*",
            "fiduswriter/static-libs/*",
            "fiduswriter/book/*",
            "fiduswriter/citation-api-import/*",
            "fiduswriter/languagetool/*",
            "fiduswriter/npm_mjs/*",
            "fiduswriter/ojs/*",
            "fiduswriter/phplist/*",
            "fiduswriter/payment/*",
        ]
    },
    python_requires=">=3",
    install_requires=read("fiduswriter/requirements.txt").splitlines(),
    extras_require={
        "books": "fiduswriter-books ~= 3.11.1",
        "citation-api-import": "fiduswriter-citation-api-import ~= 3.11.0",
        "languagetool": "fiduswriter-languagetool ~= 3.11.0",
        "ojs": "fiduswriter-ojs ~= 3.11.0",
        "phplist": "fiduswriter-phplist ~= 3.11.0",
        "gitrepo-export": "fiduswriter-gitrepo-export ~= 3.11.0",
        "payment-paddle": "fiduswriter-payment-paddle ~= 3.11.1",
        "mysql": read("fiduswriter/mysql-requirements.txt").splitlines(),
        "postgresql": read("fiduswriter/postgresql-requirements.txt").splitlines(),
    },
    entry_points={"console_scripts": ["fiduswriter=fiduswriter.manage:entry"]},
)
