#!/usr/bin/env python3

# This software was developed at the National Institute of Standards
# and Technology in whole or in part by employees of the Federal
# Government in the course of their official duties. Pursuant to
# title 17 Section 105 of the United States Code portions of this
# software authored by NIST employees are not subject to copyright
# protection and are in the public domain. For portions not authored
# by NIST employees, NIST has been granted unlimited rights. NIST
# assumes no responsibility whatsoever for its use by other parties,
# and makes no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

__version__ = "0.1.2"

import os
import sys
import hashlib
import logging
import subprocess
import tempfile

sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))
import dfxml.objects as Objects

_logger = logging.getLogger(os.path.basename(__file__))

# TODO This script includes two functions that could stand to be in a shared library supporting the pytest tests.
# * XML Schema conformance.
# * File round-tripping.

def _confirm_schema_conformance(dfxml_path):
    """
    This function takes a path to a DFXML file, and tests its conformance to the DFXML schema at the version tracked in this Git repository.
    This function is potentially a NOP - if the schema is not downloaded (with 'make schema-init' run at the top of this repository), then to keep local unit testing operating smoothly, the test *will not* fail because of schema absence.  However, testing in the CI environment *will* use the schema.  If the schema is present, schema conformance will be checked regardless of the environment.

    Environment variables:
    PYTEST_REQUIRES_DFXML_SCHEMA - checked for the string value "1".  Set in .travis.yml.
    """

    # Handle the desired error not existing before Python 3.3.
    #   Via: https://stackoverflow.com/a/21368457
    if sys.version_info < (3,3):
        _FileNotFoundError = IOError
    else:
        _FileNotFoundError = FileNotFoundError

    # Confirm this function is acting from the expected directory relative to the repository root.
    top_srcdir = os.path.join(os.path.dirname(__file__), "..", "..", "..")
    if not os.path.exists(os.path.join(top_srcdir, "dfxml_schema_commit.txt")):
        raise _FileNotFoundError("This script (%r) tries to refer to the top Git-tracked DFXML directory, but could not find it based on looking for dfxml_schema_commit.txt." % os.path.basename(__file__))

    # Use the schema file if it is present.
    #   - Testing in the CI environment should require the file be present.
    #   - Offline testing does not necessarily need to fail if the file wasn't downloaded.
    schema_path = os.path.join(top_srcdir, "schema", "dfxml.xsd")
    if os.path.exists(schema_path):
        command = ["xmllint", "--noout", "--schema", schema_path, dfxml_path]
        try:
            subprocess.check_call(command, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except:
            subprocess.check_call(command)
    else:
        # This variable is set in .travis.yml.
        if os.environ.get("PYTEST_REQUIRES_DFXML_SCHEMA") == "1":
            raise _FileNotFoundError("Tracked DFXML schema not found.  To retrieve it, run 'make schema-init' in the top-level source directory.")

def _file_round_trip_dfxmlobject(dobj):
    """
    Serializes the DFXMLObject (dobj) to a temporary file.  Parses that temporary file into a new DFXMLObject.
    For debugging review, the temporary file is left in place, and it is the caller's responsibility to delete this file (if OS cleanup is not expected to automatically handle it).

    Returns pair:
    * Path of temporary file.  
    * DFXMLObject, reconstituted from parsing that temporary file.
    """
    tmp_filename = None
    dobj_reconst = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dfxml", delete=False) as out_fh:
            tmp_filename = out_fh.name
            dobj.print_dfxml(output_fh=out_fh)
        _confirm_schema_conformance(tmp_filename)
        dobj_reconst = Objects.parse(tmp_filename)
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    return (tmp_filename, dobj_reconst)

def test_sector_size():
    dobj = Objects.DFXMLObject(version="1.2.0")
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.sector_size = 2048

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = _file_round_trip_dfxmlobject(dobj)
    diobj_reconst = dobj_reconst.disk_images[0]
    try:
        assert diobj_reconst.sector_size == 2048
        assert diobj.sector_size == diobj_reconst.sector_size
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_filesize():
    # TODO Upgrade to 1.3.0 on release.
    dobj = Objects.DFXMLObject(version="1.2.0+")
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.filesize = 2 * 2**30

    brs = Objects.ByteRuns()
    diobj.byte_runs = brs

    br1 = Objects.ByteRun()
    br1.img_offset = 0
    br1.len = 512
    brs.append(br1)

    br2 = Objects.ByteRun()
    br2.img_offset = 512
    br2.len = 2 * 2**30 - 512
    brs.append(br2)

    assert sum([x.len for x in diobj.byte_runs]) == diobj.filesize

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = _file_round_trip_dfxmlobject(dobj)
    diobj_reconst = dobj_reconst.disk_images[0]
    try:
        assert sum([x.len for x in diobj_reconst.byte_runs]) == diobj_reconst.filesize
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)

def test_hashes():
    # TODO Upgrade to 1.3.0 on release.
    dobj = Objects.DFXMLObject(version="1.2.0+")
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.filesize = 4

    sha512obj = hashlib.sha512()
    sha512obj.update(b"abcd")
    hash_value = sha512obj.hexdigest()

    diobj.sha512 = hash_value

    assert diobj.sha512 == hash_value

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = _file_round_trip_dfxmlobject(dobj)
    diobj_reconst = dobj_reconst.disk_images[0]
    try:
        assert diobj_reconst.sha512 == hash_value
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)
