# This script works with Python 2 and 3

from __future__ import print_function

import sys
import os
import datetime
import subprocess

def make_version_header(filename):
    # Note: git describe doesn't work if no tag is available
    try:
        git_tag = subprocess.check_output(["git", "describe", "--dirty", "--always"], universal_newlines=True).strip()
    except subprocess.CalledProcessError:
        git_tag = ""
    try:
        git_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.STDOUT, universal_newlines=True).strip()
    except subprocess.CalledProcessError:
        git_hash = "unknown"

    try:
        # Check if there are any modified files.
        subprocess.check_call(["git", "diff", "--no-ext-diff", "--quiet", "--exit-code"], stderr=subprocess.STDOUT)
        # Check if there are any staged files.
        subprocess.check_call(["git", "diff-index", "--cached", "--quiet", "HEAD", "--"], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        git_hash += "-dirty"

    # Try to extract MicroPython version from git tag
    if git_tag.startswith("v"):
        ver = git_tag[1:].split("-")[0].split(".")
        if len(ver) == 2:
            ver.append("0")
    else:
        ver = ["0", "0", "1"]

    # Generate the file with the git and version info
    file_data = """\
// This file was generated by py/makeversionhdr.py
#define MICROPY_GIT_TAG "%s"
#define MICROPY_GIT_HASH "%s"
#define MICROPY_BUILD_DATE "%s"
#define MICROPY_VERSION_MAJOR (%s)
#define MICROPY_VERSION_MINOR (%s)
#define MICROPY_VERSION_MICRO (%s)
#define MICROPY_VERSION_STRING "%s.%s.%s"
""" % (git_tag, git_hash, datetime.date.today().strftime("%Y-%m-%d"),
    ver[0], ver[1], ver[2], ver[0], ver[1], ver[2])

    # Check if the file contents changed from last time
    write_file = True
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            existing_data = f.read()
        if existing_data == file_data:
            write_file = False

    # Only write the file if we need to
    if write_file:
        print("Generating %s" % filename)
        with open(filename, 'w') as f:
            f.write(file_data)

make_version_header(sys.argv[1])
