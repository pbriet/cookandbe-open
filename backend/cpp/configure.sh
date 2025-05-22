#!/bin/sh

SCRIPT_NAME=`readlink -f "$0"`
DJANGO_PATH=`dirname "$SCRIPT_NAME"`

create_rules()
{
    # Initialization
    rulefile=./Makefile.rules
    dependsfile=./hippocrate/Makefile.depends
    rm -f $rulefile
    touch $rulefile $dependsfile
    chmod 604 $rulefile $dependsfile
    # Checking architecture
    case `uname -a | cut -d ' ' -f 14` in
        "i686")
            echo "
ARCHI       = 32
" >> $rulefile
            ;;
        "x86_64")
            echo "
ARCHI       = 64
" >> $rulefile
            ;;
        *)
            echo "Architecture non reconnue"
            exit
            ;;
    esac
    # Default settings
    echo "
PLATFORM    = `uname -s`
INCLUDES    = -I/usr/include/python3.8 -I/src
LDPATH      = -L/usr/lib/x86_64-linux-gnu
WARNINGS_ENABLED  = -W -Wno-long-long
WARNINGS_DISABLED = -Wno-unused-parameter -Wno-unused-local-typedef -Wno-missing-field-initializers -Wno-deprecated
# Following warnings not added due to uncompliant system libraries : -Wconversion -Wundef -Winline -Wshadow -Wfloat-equal
JOBS        = -j3
RM          = rm
RMFLAGS     = -f
OPTIONS     = -m\$(ARCHI) -Werror -pipe -fPIC -std=c++11 -fomit-frame-pointer -D_UNIX_ -DBOOST_SYSTEM_NO_DEPRECATED
# Add -pg above for profiling (gproof) and --coverage for coverage
" >> $rulefile
    # Platform specific settings
    case `uname -s` in
	"Linux")
	    echo "
CC          = /usr/bin/clang++
CFLAGS      = \$(WARNINGS_ENABLED) \$(WARNINGS_DISABLED) -O2
LDFLAGS     =
CFLAGS_D    = \$(WARNINGS_ENABLED) \$(WARNINGS_DISABLED) -O1 -g -DDEBUG
LDFLAGS_D   = -rdynamic
CFLAGS_R    = \$(WARNINGS_ENABLED) \$(WARNINGS_DISABLED) -O3 -DNDEBUG -D_RELEASE
LDFLAGS_R   =
CFLAGS_B    = \$(CFLAGS_R) -DDARWIN_ENABLE_BENCHMARK
LDFLAGS_B   = \$(LDFLAGS_R)
CFLAGS_P    = \$(CFLAGS_R) -DDARWIN_GOOGLE_PROFILING
LDFLAGS_P   = \$(LDFLAGS_R) -lprofiler
" >> $rulefile
	    ;;
	"NetBSD")
	    echo "
CC          = /usr/bin/clang++
CFLAGS      = \$(WARNINGS_ENABLED) \$(WARNINGS_DISABLED) -ansi -pedantic -O2
LDFLAGS     =
CFLAGS_D    = \$(WARNINGS_ENABLED) \$(WARNINGS_DISABLED) -ansi -pedantic -O1 -g -DDEBUG
LDFLAGS_D   =
CFLAGS_R    = \$(WARNINGS_ENABLED) \$(WARNINGS_DISABLED) -ansi -pedantic -O3 -DNDEBUG -D_RELEASE
LDFLAGS_R   =
CFLAGS_B    = \$(CFLAGS_R) -DDARWIN_ENABLE_BENCHMARK
LDFLAGS_B   = \$(LDFLAGS_R)
CFLAGS_P    = \$(CFLAGS_R) -DDARWIN_GOOGLE_PROFILING
LDFLAGS_P   = \$(LDFLAGS_R) -lprofiler
" >> $rulefile
        ;;
	*)
	    echo "\033[0;31m***** Unknown architecture : `uname -s` *****\033[0m"
        rm $rulefile $dependsfile
        exit
	    ;;
    esac
    # Colors
    echo "
C_BLACK     = \\033[0;30m
C_RED       = \\033[0;31m
C_GREEN     = \\033[0;32m
C_YELLOW    = \\033[0;33m
C_BLUE      = \\033[1;34m
C_PURPLE    = \\033[0;35m
C_CYAN      = \\033[0;36m
C_WHITE     = \\033[0;37m
C_END       = \\033[0m
" >> $rulefile
    # Prevent a creation time issue
    sleep 1
    # Regenerate dependencies
    make depends && echo "\033[0;32m***** Configuration successfull *****\033[0m" || echo "\033[0;31m***** Fail to generate dependencies *****\033[0m"
}

create_rules
