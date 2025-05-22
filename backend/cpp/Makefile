ifeq ($(wildcard Makefile.rules),$(null)) 
  $(info ********** Makefile not configured **********)
  $(error Did you try ./configure.sh ?)
endif

include Makefile.rules

all debug release check valgrind prof prof-gif bench:
	$(MAKE) -C hippocrate $(JOBS) $@

clean distclean depends:
	$(MAKE) -C hippocrate $@

migrate:
	python3 manage.py migrate

reset:
	./reset_db_from_staging.sh

install: update reset

test:
ifdef ARGS
	python3 manage.py test --keepdb $(ARGS)
else
	python3 manage.py test --keepdb --noinput --parallel
endif