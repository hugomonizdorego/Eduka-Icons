PYTHON ?= python3
.PHONY: all build test preview deb source install clean
all: build
build:
	$(PYTHON) tools/build_theme.py
test:
	$(PYTHON) tools/check_source.py
	$(PYTHON) tools/validate.py
preview:
	$(PYTHON) tools/preview.py
deb:
	$(PYTHON) tools/build_deb.py
source:
	$(PYTHON) tools/build_source.py
install:
ifdef DESTDIR
	$(PYTHON) tools/install.py --destdir "$(DESTDIR)/usr/share/icons"
else
	$(PYTHON) tools/install.py --system
endif
clean:
	rm -rf build dist
