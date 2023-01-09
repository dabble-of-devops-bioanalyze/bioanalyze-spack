# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from spack.package import *


class Rstudio(CMakePackage):
    """RStudio is an integrated development environment (IDE) for R."""

    homepage = "www.rstudio.com/products/rstudio/"
    url = "https://github.com/rstudio/rstudio/archive/refs/tags/v2022.12.0+353.tar.gz"

    version(
        "2022.12.0",
        sha256="e4f3503e2ad4229301360f56fd5288e5c8e769c490073dae7fe40366237ecce0"
    )

    variant("notebook", default=True, description="Enable notebook support.")
    variant("server", default=False, description="Install RStudio as a server.")
    variant("desktop", default=False, description="Install RStudio as a Desktop app.")

    conflicts("+desktop", when="+server", msg="+server and +desktop are mutually exclusive.")
    conflicts("~desktop", when="~server", msg="One of +server or +desktop must be set.")

    variant("bioconductor", default=False, description="Install bioconductor.")
    variant("tidyverse", default=True, description="Install tidyverse.")

    depends_on("zlib@1.2.5:")

    depends_on("texinfo", type=("build", "run"))
    depends_on("cairo+X+gobject+pdf", type=("build", "run"))
    depends_on("pango+X", type=("build", "run"))
    depends_on("harfbuzz+graphite2", type=("build", "run"))
    depends_on("jpeg", type=("build", "run"))
    depends_on("libpng", type=("build", "run"))
    depends_on("libtiff", type=("build", "run"))
    depends_on("libx11", type=("build", "run"))
    depends_on("libxmu", type=("build", "run"))
    depends_on("libxt", type=("build", "run"))
    depends_on("tk", type=("build", "run"))

    # TODO pretty sure rstudio constrains r version
    depends_on("r+X", type=("build", "run"))
    depends_on("cmake@3.25.1:", type="build")
    depends_on("pkgconfig", type="build")
    depends_on("ant", type="build")
    # Could NOT find Boost (missing: atomic chrono date_time filesystem iostreams
    # program_options random regex system thread)
    depends_on("boost+pic+atomic+chrono+date_time+filesystem+iostreams+program_options+random+regex+system+thread")
    depends_on("patchelf")
    depends_on("yaml-cpp")  # find_package fails with newest version
    # rstudio version is 16, but it fails
    depends_on("node-js")
    depends_on("yarn")
    depends_on("pandoc")
    depends_on("icu4c")
    #         k3q7jx3v/include/soci/soci-platform.h:154:10: error: #error "SOCI must be configured with C++11 s
    #         upport when using C++11"
    #  911             #error "SOCI must be configured with C++11 support when using C++11"
    #  912              ^~~~~

    depends_on("soci~static+boost+postgresql+sqlite cxxstd=11")
    depends_on("java")
    depends_on("r-markdown")
    depends_on("r-rmarkdown")
    depends_on("r-rsconnect")
    depends_on("r-languageserver")

    with when("+tidyverse"):
        depends_on("r-tidyverse")
        depends_on("r-colorbrewer")

    with when("+bioconductor"):
        depends_on("r-ensembldb")
        depends_on("r-biocmanager")
        depends_on("r-biocgenerics")

    with when("+notebook"):
        depends_on("r-base64enc")
        depends_on("r-digest")
        depends_on("r-evaluate")
        depends_on("r-glue")
        depends_on("r-highr")
        depends_on("r-htmltools")
        depends_on("r-jsonlite")
        depends_on("r-knitr")
        depends_on("r-magrittr")
        depends_on("r-stringi")
        depends_on("r-stringr")
        depends_on("r-tinytex")
        depends_on("r-xfun")
        depends_on("r-yaml")

    def patch(self):
        # remove hardcoded soci path to use spack soci
        if self.spec["soci"].version <= Version("4.0.0"):
            soci_lib = self.spec["soci"].prefix.lib64
        else:
            soci_lib = self.spec["soci"].prefix.lib
        filter_file(
            'set(SOCI_LIBRARY_DIR "/usr/lib")',
            'set(SOCI_LIBRARY_DIR "{0}")'.format(soci_lib),
            "src/cpp/CMakeLists.txt",
            string=True,
        )

        # two methods for pandoc
        # 1) replace install-pandoc:
        #    - link pandoc into tools/pandoc/$PANDOC_VERSION
        #      (this is what install-pandoc would do)
        #    - cmake then installs pandoc files from there into bin
        # 2) remove install-pandoc and cmake install step + link directly into bin

        # method 1)
        filter_file(
            'set(PANDOC_VERSION "2.11.4" CACHE INTERNAL "Pandoc version")',
            'set(PANDOC_VERSION "{0}" CACHE INTERNAL "Pandoc version")'.format(
                self.spec["pandoc"].version
            ),
            "src/cpp/session/CMakeLists.txt",
            string=True,
        )

        pandoc_dir = join_path(self.prefix.tools, "pandoc", self.spec["pandoc"].version)
        os.makedirs(pandoc_dir)
        with working_dir(pandoc_dir):
            os.symlink(self.spec["pandoc"].prefix.bin.pandoc, "pandoc")
            os.symlink(
                os.path.join(self.spec["pandoc"].prefix.bin, "pandoc-citeproc"), "pandoc-citeproc"
            )

    @run_before("cmake")
    def install_deps(self):
        dep_scripts = [
            "./dependencies/common/install-dictionaries",
            "./dependencies/common/install-mathjax",
            "./dependencies/common/install-quarto",
        ]
        for dep in dep_scripts:
            deps = Executable(dep)
            deps()

        cwd = os.getcwd()
        os.chdir("dependencies/common")
        deps = Executable("./install-npm-dependencies")
        deps()

        os.chdir(cwd)

    def cmake_args(self):
        args = [
            "-DRSTUDIO_USE_SYSTEM_YAML_CPP=Yes",
            "-DRSTUDIO_USE_SYSTEM_BOOST=Yes",
            "-DRSTUDIO_USE_SYSTEM_SOCI=Yes"
        ]

        if "+server" in self.spec:
            args.append("-DRSTUDIO_TARGET=Server")
            args.append("-DCMAKE_BUILD_TYPE=Release")
        else:
            args.append("-DRSTUDIO_TARGET=Electron")
            args.append("-DRSTUDIO_PACKAGE_BUILD=Yes")

        return args

    def setup_build_environment(self, env):
        env.set("RSTUDIO_TOOLS_ROOT", self.prefix.tools)

