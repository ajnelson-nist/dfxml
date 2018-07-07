
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

import Objects
import copy
import logging
import os

_logger = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=logging.DEBUG)

ho = Objects.HiveObject()

ho.mtime = "2010-01-02T03:45:00Z"

hoc = copy.deepcopy(ho)

diffs = hoc.compare_to_other(ho)
_logger.debug(repr(diffs))
assert len(diffs) == 0

hoc.mtime = "2011-01-02T03:45:00Z"

diffs = hoc.compare_to_other(ho)
_logger.debug(repr(diffs))
assert len(diffs) == 1
