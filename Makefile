deps:
	# pkg install -q -y py36-ioc
	python3.6 -m ensurepip
	python3.6 -m pip install -Ur requirements.txt
	git submodule init
	git submodule update
	cd .libioc/; make install
install: deps
	python3.6 -m pip install -U .
	@if [ -f /usr/local/etc/init.d ]; then \
		install -m 0755 rc.d/ioc /usr/local/etc/init.d; \
	else \
		install -m 0755 rc.d/ioc /usr/local/etc/rc.d; \
	fi
install-dev: deps
	if [ "`uname`" = "FreeBSD" ]; then pkg install -y gmake; fi
	python3.6 -m pip install -Ur requirements-dev.txt
	python3.6 -m pip install -e .
	@if [ -f /usr/local/etc/init.d ]; then \
		install -m 0755 -o root -g wheel rc.d/ioc /usr/local/etc/init.d; \
	else \
		install -m 0755 -o root -g wheel rc.d/ioc /usr/local/etc/rc.d; \
	fi
install-travis:
	python3.6 -m pip install -U -r requirements-dev.txt
uninstall:
	python3.6 -m pip uninstall -y ioc_cli
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
