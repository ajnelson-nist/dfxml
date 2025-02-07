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

__version__ = "0.3.1"

import hashlib
import logging
import os
import sys

import libtest

import dfxml.objects as Objects

_logger = logging.getLogger(os.path.basename(__file__))

ERROR_1 = "Error 1"
ERROR_2 = "Error 2"


def test_empty_object():
    dobj = Objects.DFXMLObject()
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)


def test_sector_size():
    dobj = Objects.DFXMLObject()
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.sector_size = 2048

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
        assert diobj_reconst.sector_size == 2048
        assert diobj.sector_size == diobj_reconst.sector_size
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)


def test_error():
    dobj = Objects.DFXMLObject()
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.error = ERROR_1

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
        assert diobj_reconst.error == ERROR_1
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)


def test_error_after_partition_system():
    dobj = Objects.DFXMLObject()
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.error = ERROR_1

    psobj = Objects.PartitionSystemObject()
    psobj.error = ERROR_2
    diobj.append(psobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
        psobj_reconst = diobj_reconst.partition_systems[0]
        assert diobj_reconst.error == ERROR_1
        assert psobj_reconst.error == ERROR_2
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)


def test_error_after_file_system():
    dobj = Objects.DFXMLObject()
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.error = ERROR_1

    vobj = Objects.VolumeObject()
    vobj.error = ERROR_2
    diobj.append(vobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
        vobj_reconst = diobj_reconst.volumes[0]
        assert diobj_reconst.error == ERROR_1
        assert vobj_reconst.error == ERROR_2
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)


def test_error_after_file():
    # TODO Bump version when feature branch merged into schema.
    dobj = Objects.DFXMLObject()
    diobj = Objects.DiskImageObject()
    dobj.append(diobj)

    diobj.error = ERROR_1

    fobj = Objects.FileObject()
    fobj.alloc_inode = False
    fobj.alloc_name = False
    fobj.error = ERROR_2
    diobj.append(fobj)

    # Do file I/O round trip.
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    try:
        diobj_reconst = dobj_reconst.disk_images[0]
        fobj_reconst = diobj_reconst.files[0]
        assert diobj_reconst.error == ERROR_1
        assert fobj_reconst.error == ERROR_2
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
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
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
    (tmp_filename, dobj_reconst) = libtest.file_round_trip_dfxmlobject(dobj)
    diobj_reconst = dobj_reconst.disk_images[0]
    try:
        assert diobj_reconst.sha512 == hash_value
    except:
        _logger.debug("tmp_filename = %r." % tmp_filename)
        raise
    os.remove(tmp_filename)
