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
#     spack install r-languageserver
#
# You can edit this file again by typing:
#
#     spack edit r-languageserver
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class RLanguageserver(RPackage):
    """An implementation of the Language Server Protocol for R. The Language Server protocol is used by an editor
    client to integrate features like auto completion. See <https://microsoft.github.io/language-server-protocol/>
    for details. """

    homepage = "https://cran.r-project.org/web/packages/languageserver/index.html"
    cran = "languageserver"

    version("0.3.15", sha256="94eebc1afbaee5bb0d3a684673007299d3a5520fa398f22838b603ca78f8c100")
    version("0.3.14", sha256="266fe5a074dfef7a61de2943d5ac7c4838149c66b695505c89c094776e30d460")
    version("0.3.13", sha256="2850246cba8340b68e27be1ec1273f6deae37c4f7538c56b3ea35a21563b5a78")
    version("0.3.12", sha256="431514b49f8049c07b24e1571f79663b791239ebbc87e4f2a77c6482ac95ba36")
    version("0.3.11", sha256="87eece0d3f69bfcadaacc396a112c014c4a2dc6cdc7f927e46032cbc3e51c1fb")
    version("0.3.10", sha256="92a300234e52f1af3022ff6f3037f8342ed26ce0d9127a6790d277fb19e610d5")
    version("0.3.9", sha256="3b43acc89afce4a10526cbdb3a0e0ce0ed57c73c575b9e2f7ac08fac10fb92a9")
    version("0.3.8", sha256="371db6976d6066d654c9d31f911dba667c1f8ceb4ab67da34d44037b66f3ca9b")
    version("0.3.7", sha256="ddc7a3f0bf14e63a37a1471f53583e4758182cecd02be13bf1e28baa72d9a069")

    # FIXME: Add dependencies if required.
    depends_on("r", type=("build", "run"))

    def configure_args(self):
        # FIXME: Add arguments to pass to install via --configure-args
        # FIXME: If not needed delete this function
        args = []
        return args
