
include ../Makefile.rules

# Default vars
EXECUTABLE  =
LIBRARY     =
OBJS        =
LDLIBS      =
BOOST_LIBS  = -lboost_python38 -lboost_system
PYTHON_LIBS = -lpython3.8
OTHER_LIBS  = -lyaml-cpp

# Core specific vars
CORE_TARGET = core
CORE_BIN    = lib$(CORE_TARGET).so
CORE_PYTHON = $(CORE_TARGET).so
CORE_LIBS   = $(BOOST_LIBS) $(PYTHON_LIBS) $(OTHER_LIBS)

CORE_SRCS_MODELS = \
	models/recipe.cpp \
	models/recipeindex.cpp \
	models/dataindexer.cpp \
	models/dish.cpp \
	models/dishdomain.cpp \
	models/dishindex.cpp \
	models/foodindex.cpp \
	models/dishrecipe.cpp \
	models/constraints/budget.cpp \
	models/constraints/constraint.cpp \
	models/constraints/interval.cpp \
	models/constraints/nutrient.cpp \
	models/constraints/nutrient_balance.cpp \
	models/constraints/recipes.cpp \
	models/constraints/time.cpp \
	models/constraints/unicity.cpp \
	models/constraints/redundancy.cpp \
	models/constraints/max_modifs.cpp \
	models/constraints/meal_balance.cpp \
	models/constraints/meal_type_balance.cpp \
	models/constraints/shopping.cpp \
	models/filters/filter.cpp \
	models/problem.cpp \
	models/solution.cpp \
	models/score.cpp

CORE_SRCS_VIEWS =

CORE_SRCS_CONTROLS = \
	controls/algorithm/algorithm.cpp \
	controls/algorithm/naive/naive.cpp \
	controls/algorithm/naive/naive.cpp \
	controls/algorithm/darwin/darwin.cpp \
	controls/algorithm/darwin/config.cpp \
	controls/algorithm/darwin/interval.cpp \
	controls/algorithm/darwin/other.cpp \
	controls/algorithm/darwin/logger.cpp \
	controls/algorithm/darwin/selection.cpp \
	controls/algorithm/darwin/operator.cpp \
	controls/algorithm/darwin/mutations/mutation.cpp \
	controls/algorithm/darwin/crossovers/crossover.cpp

CORE_SRCS_ROOT = \
	wrapstd.cpp \
	core.cpp \
	tools/random.cpp \
	tools/exception.cpp \
	tools/traceback.cpp \
	tools/print.cpp \
	tools/stats.cpp \
	tools/python.cpp

CORE_SRCS_ALL = $(CORE_SRCS_MODELS) $(CORE_SRCS_VIEWS) $(CORE_SRCS_CONTROLS) $(CORE_SRCS_ROOT)
CORE_OBJS_ALL = $(CORE_SRCS_ALL:.cpp=.o)

# Tests specific vars
TESTS_TARGET= check
TESTS_ARGS  = --report_format=HRF --report_level=confirm --log_format=XML --log_level=test_suite --show_progress=yes --detect_memory_leak=1 --detect_fp_exceptions=yes --build_info=yes
TESTS_PATH  = \$LD_LIBRARY_PATH:/usr/local/lib:.
TESTS_BIN   = cpptest
TESTS_LIBS  = $(BOOST_LIBS) -lboost_unit_test_framework $(PYTHON_LIBS) -l$(CORE_TARGET) $(OTHER_LIBS)
TESTS_OPTS  =

TESTS_SRCS_ALL = \
	tests/main.cpp \
	tests/sample.cpp \
	tests/externals.cpp \
	tests/darwin.cpp \
	tests/nutrient_constraint.cpp \
	tests/constraints/time.cpp \
	tests/algorithm.cpp \
	tests/tools.cpp \
	tests/solution.cpp \
	tests/dish.cpp \
	tests/dishdomain.cpp

TESTS_OBJS_ALL = $(TESTS_SRCS_ALL:.cpp=.o)

# Global vars
TODEL       = *.o */*.o */*~ *~ *\# */*\# *.bak */*.bak
SRCS_ALL    = $(CORE_SRCS_ALL) $(TESTS_SRCS_ALL)
OBJS_ALL    = $(CORE_OBJS_ALL) $(TESTS_OBJS_ALL)
BINS_ALL    = $(CORE_BIN) $(CORE_PYTHON) $(TESTS_BIN)

all:
	@$(MAKE) $(CORE_TARGET)
	@$(MAKE) $(TESTS_TARGET)

%.o: %.cpp
	@echo "$(C_YELLOW)$(CC) $(C_BLUE)$<\033[0m"
	@$(CC) $(OPTIONS) -g $(CFLAGS) $(INCLUDES) -c $< -o $@

$(LIBRARY): $(OBJS)
	@echo "$(C_PURPLE)$(CC) $(C_BLUE)$^ $(C_END)"
	@$(CC) $^ $(OPTIONS) $(LDFLAGS) $(LDPATH) $(LDLIBS) -shared -o $(LIBRARY)

$(EXECUTABLE): $(OBJS)
	@echo "$(C_GREEN)$(CC) $(C_BLUE)$^ $(C_END)"
	@$(CC) $^ $(OPTIONS) $(LDFLAGS) $(LDPATH) $(LDLIBS) -o $(EXECUTABLE)

debug:
	@$(MAKE) $(CORE_TARGET) CFLAGS="$(CFLAGS_D)" LDFLAGS="$(LDFLAGS_D)"

release:
	@$(MAKE) $(CORE_TARGET) CFLAGS="$(CFLAGS_R)" LDFLAGS="$(LDFLAGS_R)"

bench:
	@$(MAKE) $(CORE_TARGET) CFLAGS="$(CFLAGS_B)" LDFLAGS="$(LDFLAGS_B)"

prof:
	@$(MAKE) $(CORE_TARGET) CFLAGS="$(CFLAGS_P)" LDFLAGS="$(LDFLAGS_P)"

prof-gif:
	google-pprof --focus=Darwin /bin/ls darwin.prof --gif > darwin.gif

core:
	@$(MAKE) infos $(CORE_BIN) LIBRARY="$(CORE_BIN)" OBJS="$(CORE_OBJS_ALL)" $(JOBS) LDLIBS="$(CORE_LIBS)"
    # Special python
	@cp $(CORE_BIN) $(CORE_PYTHON)

valgrind:
	@$(MAKE) check TESTS_OPTS="valgrind --leak-check=full --show-reachable=no --show-possibly-lost=no"

check: debug
	@$(MAKE) infos $(TESTS_BIN) EXECUTABLE="$(TESTS_BIN)" OBJS="$(TESTS_OBJS_ALL)" CFLAGS="$(CFLAGS_D)" \
                                LDFLAGS="$(LDFLAGS_D)" LDPATH="$(LDPATH) -L." LDLIBS="$(TESTS_LIBS)" $(JOBS)
	@echo "$(C_YELLOW)LD_LIBRARY_PATH = $(C_BLUE)$(TESTS_PATH) $(C_END)"
	@echo "$(C_YELLOW)TESTS_OPTS = $(C_RED)$(TESTS_OPTS) $(C_END)"
	@echo "$(C_GREEN)$(TESTS_BIN) $(C_BLUE)$(TESTS_ARGS) $(C_END)"
	@LD_LIBRARY_PATH=$(TESTS_PATH) $(TESTS_OPTS) ./$(TESTS_BIN) $(TESTS_ARGS)

infos:
ifdef EXECUTABLE
	@echo "$(C_YELLOW)TARGET    = $(C_GREEN)$(EXECUTABLE)$(C_END)"
endif
ifdef LIBRARY
	@echo "$(C_YELLOW)TARGET    = $(C_PURPLE)$(LIBRARY)$(C_END)"
endif
	@echo "\
$(C_YELLOW)CFLAGS    = $(C_BLUE)$(CFLAGS)   $(C_END) \n\
$(C_YELLOW)INCLUDES  = $(C_BLUE)$(INCLUDES) $(C_END) \n\
$(C_YELLOW)LDFLAGS   = $(C_BLUE)$(LDFLAGS)  $(C_END) \n\
$(C_YELLOW)LDPATH    = $(C_BLUE)$(LDPATH)   $(C_END) \n\
$(C_YELLOW)LDLIBS    = $(C_BLUE)$(LDLIBS)   $(C_END) \n\
$(C_YELLOW)OPTIONS   = $(C_BLUE)$(OPTIONS)  $(C_END) \n\
"

clean:
	@echo "$(C_YELLOW)$(RM) $(C_BLUE)$(RMFLAGS) $(C_RED)$(BINS_ALL) $(TODEL) $(OBJS_ALL)$(C_END)"
	@$(RM) $(RMFLAGS) $(BINS_ALL) $(TODEL) $(OBJS_ALL)

distclean: clean
	@echo "$(C_YELLOW)$(RM) $(C_BLUE)$(RMFLAGS) $(C_RED)../Makefile.rules Makefile.depends$(C_END)"
	@$(RM) $(RMFLAGS) ../Makefile.rules Makefile.depends

depends:
	@echo "$(C_YELLOW)$(CC) $(C_BLUE)$(OPTIONS) $(INCLUDES) $(CFLAGS) -MM Makefile.depends $(C_RED)$(SRCS_ALL)$(C_END)"
	@echo "" > Makefile.depends
	@$(call make-all-depends)

define make-all-depends
   for file in $(OBJS_ALL); \
   do \
        $(call make-file-depends,$$file,$${file%o}cpp); \
   done
endef

define make-file-depends
   $(CC) -MM            \
         -MT $1         \
         $(OPTIONS)     \
         $(CFLAGS)      \
         $(INCLUDES)    \
         $2 >> Makefile.depends
endef

# Include the generated dependance file
include Makefile.depends
