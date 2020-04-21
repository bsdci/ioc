PYTHON_VERSION ?= $(TRAVIS_PYTHON_VERSION)
SELECTED_PYTHON_VERSION != if [ "$(PYTHON_VERSION)" != "" ]; then echo $(PYTHON_VERSION); else pkg info -g 'python3*' | cut -d'-' -f1 | sed 's/^python//' | sort -n | tail -n1 | sed -r 's/^([0-9])([0-9]+)/\1.\2/'; fi
PYTHON ?= python${SELECTED_PYTHON_VERSION}
# turn python3.7 -> 3.7 -> 37
pyver= ${PYTHON:S/^python//:S/.//:C/\([0-9]+\)/\1/}

.if $(pyver) < 35
. error "ioc cannot run with a Python version < 3.5"
.endif

deps:
	$(PYTHON) -m ensurepip
	$(PYTHON) -m pip install -Ur requirements.txt
install-libioc:
	git submodule init
	git submodule update
	make -C .libioc/ install
install-ioc: deps install-service
	$(PYTHON) -m pip install -U .
install-service:
	@if [ -f /usr/local/etc/init.d ]; then \
		install -m 0755 rc.d/ioc /usr/local/etc/init.d; \
	else \
		install -m 0755 rc.d/ioc /usr/local/etc/rc.d; \
	fi
install: install-libioc install-ioc
install-dev: deps
	if [ "`uname`" = "FreeBSD" ]; then pkg install -y gmake; fi
	$(PYTHON) -m pip install -Ur requirements-dev.txt
	$(PYTHON) -m pip install -e .
	@if [ -f /usr/local/etc/init.d ]; then \
		install -m 0755 -o root -g wheel rc.d/ioc /usr/local/etc/init.d; \
	else \
		install -m 0755 -o root -g wheel rc.d/ioc /usr/local/etc/rc.d; \
	fi
install-travis:
	$(PYTHON) -m pip install -U -r requirements-dev.txt
uninstall:
	$(PYTHON) -m pip uninstall -y ioc_cli
	@if [ -f /usr/local/etc/rc.d/ioc ]; then \
		rm /usr/local/etc/rc.d/ioc; \
	fi
check:
	flake8 --version
	flake8 --exclude=".eggs,__init__.py,docs" --ignore=E203,E252,W391,D107,A001,A002,A003,A004
	bandit --skip B404 --exclude tests/ -r .
help:
	@echo "    install"
	@echo "        Installs ioc"
	@echo "    uninstall"
	@echo "        Removes ioc."
	@echo "    check"
	@echo "        Run static linters & other static analysis tests"
	@echo "    install-dev"
	@echo "        Install dependencies needed to run `check`"
