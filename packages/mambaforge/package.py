# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install mambaforge
#
# You can edit this file again by typing:
#
#     spack edit mambaforge
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *
from os.path import split

from spack.package import *
from spack.util.environment import EnvironmentModifications


class Mambaforge(Package):
    """Conda but mamba."""

    homepage = "https://github.com/conda-forge"
    url = "https://github.com/conda-forge/miniforge/releases/download/4.14.0-2/Mambaforge-4.14.0-2-Linux-x86_64.sh"

    # version(
    #     "22.9.0-2",
    #     expand=False,
    #     sha256="d2bb6c33f2373131fc71283baae9eb81a279708d007e55d627d85abe30c2d0eb",
    # )
    version(
        "4.14.0-2",
        expand=False,
        sha256="ac3cabd483712a216f1dddeb92a7f8e198a771390c6627aa94791ab6abc7fae8",
        url="https://github.com/conda-forge/miniforge/releases/download/4.14.0-2/Mambaforge-4.14.0-2-Linux-x86_64.sh"
    )

    # FIXME: Add dependencies if required.
    # depends_on("foo")

    def install(self, spec, prefix):
        # peel the name of the script out of the pathname of the
        # downloaded file
        dir, script = split(self.stage.archive_file)
        bash = which("bash")
        bash(script, "-b", "-f", "-p", self.prefix)

    def setup_run_environment(self, env):
        filename = self.prefix.etc.join("profile.d").join("conda.sh")
        env.extend(EnvironmentModifications.from_sourcing_file(filename))
