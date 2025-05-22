
#include <boost/test/auto_unit_test.hpp>

#define BOOST_TODO do { BOOST_CHECK(true); opl::warning << "**** TODO in " << __FILE__ << ":" << __LINE__  << " (" << __FUNCTION__ << ") ****" << opl::endl; } while (false)

/*
Command line arguments are listed here: http://www.boost.org/doc/libs/1_55_0/libs/test/doc/html/utf/user-guide/runtime-config/reference.html

Here are the most usefull ones:
===============================
--run_test: can run specific tests like
    * (lists) testName1,testName2
    * (trees) testSuite1/testName1
    * (regex) *1/test*1
--log_format: {HRF|XML}
--log_level:
    * all
    * warning
    * error
    * cpp_exception
    * system_error
    * fata_error
--report_format: {HRF|XML}
--report_level: /see log_level/
--detect_memory_leak: {0|1}
--detect_fp_exceptions: {yes|no}
--output_format: {HRF|XML}
--random: {0|1}
--result_code: {yes|no}
--show_progress: {yes|no}
*/
