#!/usr/bin/make -f

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

# While SHELL would typically be set with ":=" assignment, some
# environments do not have Bash at /bin/bash (e.g. FreeBSD stores Bash
# at /usr/local/bin/bash).
ifeq ($(shell basename $(SHELL)),sh)
SHELL := $(shell which /bin/bash 2>/dev/null || which /usr/local/bin/bash)
endif

all:

.PHONY: \
  check-mypy \
  check-supply-chain

.git_submodule_init.done.log: .gitmodules
	# Confirm dfxml_schema has been checked out at least once.
	test -r dependencies/dfxml_schema/dfxml.xsd \
	  || (git submodule init dependencies/dfxml_schema && git submodule update dependencies/dfxml_schema)
	test -r dependencies/dfxml_schema/dfxml.xsd
	touch $@

clean:
	find . -name '*~' -exec rm {} \;
	$(MAKE) \
	  --directory tests \
	  clean

check: \
  check-mypy 
	$(MAKE) \
	  SHELL=$(SHELL) \
	  --directory tests \
	  check

check-mypy: \
  .git_submodule_init.done.log
	$(MAKE) \
	  SHELL=$(SHELL) \
	  --directory tests \
	  check-mypy

check-supply-chain: \
  check-mypy

check-tools:
	(cd tests/misc_object_tests;make check)
