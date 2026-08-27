.PHONY: check doctor

PYTHON ?= python3
CONFIG ?= config/harness.example.json

check:
	PYTHONPATH=src $(PYTHON) -m py_compile src/mochi_harness/*.py
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v
	$(PYTHON) -m json.tool $(CONFIG) >/dev/null
	$(PYTHON) -m json.tool schemas/harness.schema.json >/dev/null

doctor:
	PYTHONPATH=src $(PYTHON) -m mochi_harness.doctor --config $(CONFIG)
