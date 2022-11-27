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
#     spack install pyautofep
#
# You can edit this file again by typing:
#
#     spack edit pyautofep
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class Pyautofep(Package):
    git = "https://github.com/luancarvalhomartins/PyAutoFEP.git"
    url = "https://github.com/luancarvalhomartins/PyAutoFEP/archive/9de6a9f93214ece37e5d8808a716234b4c0960d1.zip"

    version(
        "2022.10.20",
        url="https://github.com/luancarvalhomartins/PyAutoFEP/archive/9de6a9f93214ece37e5d8808a716234b4c0960d1.zip",
        sha256="7b9c59257043a6e6d5e9c2d4c2632cc4",
        expand=False,
    )

    depends_on(
        "gromacs@2022",
        type=("run"),
    )
    depends_on(
        "mambaforge@4.14.0-2",
        type=("build", "run"),
    )

    def install(self, spec, prefix):
        mkdirp(prefix)
        pkgname = "pyautofep-{0}".format(self.version)
        sh = which("sh")
        sh(
            "mamba",
            "create",
            "-c",
            "conda-forge",
            "-n",
            "pyautofep",
            "-p",
            prefix,
            "python=3.8",
            "pip",
        )
        sh("chmod 777 *py")
        sh("cp", "-rf", "./*", "{0}/bin".format(prefix))
