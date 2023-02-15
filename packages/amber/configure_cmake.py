#!/usr/bin/env python3

"""
A replacement script for the legacy configure that calls cmake in the build/ directory
"""

AMBER_VERSION = '22'

import argparse
import subprocess
import os
import sys
import datetime
import platform
import stat

parser = argparse.ArgumentParser(description='Configure Amber(Tools) using cmake.'
    '  Answers to common questions are here: \n'
    '  https://ambermd.org/pmwiki/pmwiki.php/Main/CMake-Quick-Start \n',
                                 usage='%(prog)s [-h] [--source SOURCE] [--prefix PREFIX] [...]')

section = parser.add_argument_group(title='Installation location')
section.add_argument('--prefix',nargs=1,required=False,
                    help='Location of the install directory. Defaults to ./../../amber'+AMBER_VERSION)

section = parser.add_argument_group(title='Source location',
                                    description="""
The Amber(Tools) source is set by the current folder tree or can be set with the --source optional argument.
""")
section.add_argument('--source',nargs=1,
                    help="Location of the source directory. Defaults to current source tree")

section = parser.add_argument_group(title='Compiler and numerical library selection')
section.add_argument('--compiler',nargs=1,
                    choices=["GNU","PGI","INTEL","CRAY","MSVC","CLANG","AUTO","MANUAL",
                             "gnu","pgi","intel","cray","msvc","clang","auto","manual"],
                    help="specify which compiler to use (default is GNU)")
section.add_argument('--blas',nargs=1,dest='blas',
                    choices=['All','OpenBLAS','Goto','ACML','Apple','NAS','Generic'],
                    help='which version of BLAS and LAPACK to look for (default: All)')

section = parser.add_argument_group(title='Acceleration related arguments')
section.add_argument('--mpi',action="store_true",
                    help='Turns on MPI parallelization')
section.add_argument('--cuda',action="store_true",
                    help='Turns on CUDA-accelerated version of Amber(Tools)')
section.add_argument('--openmp',action="store_true",
                    help='Turns on OpenMP parallelization')

section = parser.add_argument_group(title='Optional builds')
section.add_argument('--quick',action="store_true",
                    help='build quick ab initio qm code')
section.add_argument('--reaxff',action="store_true",
                    help='build reaxff puremd code')
section.add_argument('--no-gui','--noX11',action="store_true",dest='noX11',
                    help='Do not build GUI parts of leap (default: build)')
section.add_argument('--disable-tools',nargs=1,dest='disable_tools',
                    help="Comma separated list of Amber Tools not to be built")

section = parser.add_argument_group(title='Tests, examples, and benchmarks')
group = section.add_mutually_exclusive_group()
group.add_argument('--install-tests',action="store_const",dest='install_tests',const=True,
                    help='Install tests, examples, and benchmarks (default)')
group.add_argument('--no-install-tests',action="store_const",dest='install_tests',const=False,
                    help='')

section = parser.add_argument_group(title='Python related stuff')
group = section.add_mutually_exclusive_group()
group.add_argument('--python',dest='python',action="store_const",const=True,
                    help='Build related python packages (default)')
group.add_argument('--no-python',dest='python',action="store_const",const=False,
                    help='')

section.add_argument('--with-python',nargs=1,dest='python_exe',
                    help='Location of the python executable (default: path to system python, if found)')

group = section.add_mutually_exclusive_group()
group.add_argument('--miniconda',action="store_const",dest="miniconda",const=True,
                   help='Download and use the Miniconda python environment (default)')
group.add_argument('--no-miniconda',action="store_const",dest="miniconda",const=False,
                   help='')

section = parser.add_argument_group(title='Handling of internal and external libraries')
section.add_argument('--force-internal-libs',nargs=1,dest='internal_libs',
                    help="Comma separated list of 3rd party libraries to be built from Amber's bundled version (list printed at the end of the cmake build report)")
section.add_argument('--force-external-libs',nargs=1,dest='external_libs',
                    help="Comma separated list of 3rd party libraries to be used from the system (list printed at the end of the cmake build report)")
section.add_argument('--force-disable-libs',nargs=1,dest='disable_libs',
                    help="Comma separated list of 3rd party libraries to be disabled (list printed at the end of the cmake build report)")

section = parser.add_argument_group(title='Updates')
group = section.add_mutually_exclusive_group()
group.add_argument('--check-updates',action="store_const",dest='check_updates',const=True,
                    help="Check for new patches from the Amber update server (default)")
group.add_argument('--no-check-updates',action="store_const",dest='check_updates',const=False,
                    help="")

group = section.add_mutually_exclusive_group()
group.add_argument('--apply-updates',action="store_const",dest='apply_updates',const=True,
                    help="")
group.add_argument('--no-apply-updates',action="store_const",dest='apply_updates',const=False,
                    help="Do not apply available updates for Amber and AmberTools (default)")

section = parser.add_argument_group(title='Miscellaneous')
group = section.add_mutually_exclusive_group()
group.add_argument('--color-message',action="store_const",dest='color',const=True,
                   help="output colored cmake messages (default)")
group.add_argument('--no-color-message',action="store_const",dest='color',const=False,
                   help="")
group.add_argument('-bw',action="store_const",dest='color',const=False,
                   help="Black and White, ie, disable cmake's output coloring")

section.add_argument('--dry-run',action="store_const",dest='dry_run',const=True,
                     help="emit cmake instructions but do not run them")
section.add_argument('--save',nargs='?',const='run_cmake',default=False,
                     help='save the cmake command in a file (default: run_cmake)')

parser.set_defaults(compiler=['CLANG'] if platform.system() == "Darwin" else ['GNU'],
                    python=True,
                    miniconda=True,
                    check_updates=True,
                    apply_updates=False,
                    color=True,
                    dry_run=False,
                    install_tests=True)

args = parser.parse_args()

def printSave(aString,first=False):
    # save to cmake.log + print
    if first:
        with open('cmake.log','w') as f:
            f.write(aString+'\n')
    else:
        with open('cmake.log','a') as f:
            f.write(aString+'\n')
    print(aString)


def action_bool(key_bool,key_str,comment):
    comment_formatted=comment+' '+'.'*40
    comment_formatted=comment_formatted[:max(40,len(comment)+3)]
    if key_bool:
       printSave("{} yes".format(comment_formatted))
       return "-D%s=TRUE" % (key_str)
    else:
       printSave("{} no".format(comment_formatted))
       return "-D%s=FALSE" % (key_str)

def action_string(key,cmake_str,comment):
    comment_formatted=comment+' '+'.'*40
    comment_formatted=comment_formatted[:max(40,len(comment)+3)]
    printSave("{} {}".format(comment_formatted,key[0]))
    # this seems innocuous but unnecessary wrt AMBERHOME with spaces or '\ ' in it.
    #return "-D%s='%s'" % (cmake_str,key[0])
    return "-D%s=%s" % (cmake_str,key[0])


printSave('Starting configure_cmake.py on {}\n'.format(datetime.datetime.now().strftime('%c')),first=True)
# script meant to run within build folder. location of the source depends on current tree
if args.source is None:
    source_path = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)),os.pardir))
    printSave('Setting SOURCE path automatically to ... '+source_path)
    args.source=[source_path]

if args.prefix is None:
    install_path = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)),os.pardir))
    install_path = os.path.normpath(os.path.join(os.path.abspath(install_path),os.pardir,'amber'+AMBER_VERSION))
    printSave('Setting INSTALL path PREFIX automatically to ... '+install_path)
    args.prefix=[install_path]
else:
    # reformat prefix to get absolute path
    args.prefix=[os.path.abspath(args.prefix[0])]

mystr=['cmake',args.source[0]]
action_string(args.source,'','Amber(Tools) source directory')
if not os.path.exists(os.path.join(args.source[0],'CMakeLists.txt')):
    printSave('This directory is not a Amber source tree. CMakeLists.txt is missing...')
    sys.exit(1)
mystr += [action_string(args.prefix,'CMAKE_INSTALL_PREFIX','install directory')]

if args.compiler is not None:
    args.compiler[0] = args.compiler[0].upper()
    mystr += [action_string(args.compiler,'COMPILER','compiler')]

mystr += [action_bool(args.mpi,'MPI','enable MPI parallelization')]
mystr += [action_bool(args.cuda,'CUDA','enable CUDA acceleration')]
mystr += [action_bool(args.openmp,'OPENMP','enable OpenMP parallelization')]

mystr += [action_bool(not args.noX11,'BUILD_GUI','build GUI')]

mystr += [action_bool(args.install_tests,'INSTALL_TESTS','install tests')]

if args.quick: mystr += [action_bool(args.quick,'BUILD_QUICK','enable QUICK')]
if args.reaxff: mystr += [action_bool(args.reaxff,'BUILD_REAXFF_PUREMD','enable REAXFF_PUREMD')]

# Python related stuff
mystr += [action_bool(args.python,'BUILD_PYTHON','build python programs')]
if not args.python:
    # don't install miniconda if build_python is False
    args.miniconda=False
else:
    if args.python_exe is not None: mystr += [action_string(args.python_exe,'PYTHON_EXECUTABLE','python executable location')]
if args.python_exe is None:
    mystr += [action_bool(args.miniconda,'DOWNLOAD_MINICONDA','download miniconda')]

# libraries
if platform.system() == "Darwin" and args.blas is None:
    mystr += [action_string("Apple",'BLA_VENDOR','blas/lapack vendor')]
elif args.blas is not None:
    mystr += [action_string(args.blas,'BLA_VENDOR','blas/lapack vendor')]
if args.internal_libs is not None: mystr += [action_string(args.internal_libs,'FORCE_INTERNAL_LIBS','force internal library building for')]
if args.external_libs is not None: mystr += [action_string(args.external_libs,'FORCE_EXTERNAL_LIBS','force external library building for')]
if args.disable_libs is not None: mystr += [action_string(args.disable_libs,'FORCE_DISABLE_LIBS','disable library building for')]
if args.disable_tools is not None: mystr += [action_string(args.disable_tools,'DISABLE_TOOLS','disable Amber Tools')]

# Updates
mystr += [action_bool(args.check_updates,'CHECK_UPDATES','check for available updates')]
mystr += [action_bool(args.apply_updates,'APPLY_UPDATES','apply available updates')]

# Miscellaneous
mystr += [action_bool(args.color,'COLOR_CMAKE_MESSAGES','cmake color messages')]

# Begin long if
if args.save:
    action_string([args.save],'','Saving cmake instructions')
    with open(args.save,'w') as f:
        f.write("""#!/bin/bash

#  cmake instructions from running configure_cmake.py

#  For information on how to get cmake, visit this page:
#  https://ambermd.org/pmwiki/pmwiki.php/Main/CMake-Quick-Start

#  For information on common options for cmake, visit this page:
#  http://ambermd.org/pmwiki/pmwiki.php/Main/CMake-Common-Options

#  (Note that you can change the value of CMAKE_INSTALL_PREFIX from what
#  is suggested below, but it cannot coincide with the amber{amber_version}_src
#  folder.)

{cmake} 2>&1 | tee  cmake.log

if [ ! -s cmake.log ]; then
  echo ""
  echo "Error:  No cmake.log file created: you may need to edit {save}"
  exit 1
fi

echo ""
echo "If the cmake build report looks OK, you should now do the following:"
echo ""
echo "    make install"
echo "    source {prefix}/amber.sh"
echo ""
echo "Consider adding the last line to your login startup script, e.g. ~/.bashrc"
echo ""
""".format(cmake=" ".join(mystr),
           amber_version=AMBER_VERSION,
           save=args.save,
           prefix=args.prefix[0]))
    if os.path.exists(args.save): os.chmod(args.save,0o755)
# End long if


# echo cmake command, then apply
printSave("\nRunning cmake command:")
printSave(" ".join(mystr)+'\n')

if not args.dry_run:
    # run cmake and save output into cmake.log
    cmake = subprocess.Popen(mystr,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    save = subprocess.Popen(['tee','-a','cmake.log'],stdin=cmake.stdout,stdout=subprocess.PIPE,universal_newlines=True)
    for line in save.stdout:
        print(line,end='')
    cmake.stdout.close()
    output=save.communicate()[0]
    # clean source directories just to be safe; see issue 207.
    printSave("\nCleaning source directories.")
    os.system('cp config.h ../src; cd ../src; make silentclean')
    os.system('cp config.h ../AmberTools/src; cd ../AmberTools/src; make silentclean')
    sys.exit(cmake.poll())

