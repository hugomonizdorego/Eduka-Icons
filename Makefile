PYTHON ?= python3
VERSION := $(shell cat VERSION)
.PHONY: all build test screenshots deb release source install install-system clean

all: build

build:
	$(PYTHON) tools/build_theme.py
	$(PYTHON) tools/build_apps.py

test:
	$(PYTHON) tools/check_source.py
	$(PYTHON) tools/validate.py
	$(PYTHON) tools/coverage.py

screenshots:
	$(PYTHON) tools/preview.py
	mkdir -p docs/screenshots
	cp build/screenshots/*.png docs/screenshots/

deb:
	$(PYTHON) tools/build_deb.py

release: deb
	mkdir -p release
	rm -f release/*.deb
	cp dist/*_$(VERSION)_all.deb release/

source:
	$(PYTHON) tools/build_source.py

# Copy the built themes for the current user (no sudo) and select Light.
install:
	$(PYTHON) tools/select_theme.py --install --apply Light

# Copy the built themes to /usr/share/icons (or $(DESTDIR)/usr/share/icons).
install-system:
ifdef DESTDIR
	$(PYTHON) tools/select_theme.py --install "$(DESTDIR)/usr/share/icons"
else
	$(PYTHON) tools/select_theme.py --install /usr/share/icons
endif

clean:
	rm -rf build dist
