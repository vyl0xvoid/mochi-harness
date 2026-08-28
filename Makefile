.PHONY: check doctor package-check privacy-check

PYTHON ?= python3
CONFIG ?= config/harness.example.json

check:
	PYTHONPATH=src $(PYTHON) -m py_compile src/mochi_harness/*.py src/mochi_harness/resources/*.py tools/*.py
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v
	$(PYTHON) -m json.tool $(CONFIG) >/dev/null
	$(PYTHON) -m json.tool schemas/harness.schema.json >/dev/null
	$(PYTHON) tools/privacy_check.py

doctor:
	PYTHONPATH=src $(PYTHON) -m mochi_harness.doctor --config $(CONFIG) --allow-public-config

package-check:
	$(PYTHON) tools/package_check.py

privacy-check:
	$(PYTHON) tools/privacy_check.py
