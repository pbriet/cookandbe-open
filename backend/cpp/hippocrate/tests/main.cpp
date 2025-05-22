
#define BOOST_TEST_MAIN
#define BOOST_TEST_MODULE hippocrate

#include <boost/test/included/unit_test.hpp>
#include <boost/test/results_reporter.hpp>
#include <boost/test/unit_test_log.hpp>
#include <boost/filesystem.hpp>
#include <fstream>
#include "hippocrate/tools/debug.h"

/*
Redirect boost::test XML logs into a file.

The following arguments need to be given on the command line to enable the correct layout :
			--build_info=yes --log_level=test_suite --log_format=XML

For MSVC users:
	- Project "test" > properties
	- In the configuration comboBox, choose "all configurations"
	- In configuration property > Debogging > Commnd line arguments
	- Paste the arguments !
*/

const std::string	    DEFAULT_REPORT_PATH = "cpptest_results.xml";


struct MyConfig {
  std::ofstream	out;

  MyConfig() {
  	boost::filesystem::path		path(DEFAULT_REPORT_PATH);
	std::string					stylesheet("<?xml-stylesheet type=\"text/xsl\" href=\"test_stylesheet.xsl\"?>");

	this->out.open(path.string().c_str());
    ASSERT(out.is_open(), "Unable to record XML report");
	out.write(stylesheet.c_str(), stylesheet.size());
    boost::unit_test::unit_test_log.set_format( boost::unit_test::OF_XML );
	boost::unit_test::unit_test_log.set_stream(out);
  }
  ~MyConfig() {}
};

BOOST_TEST_GLOBAL_CONFIGURATION( MyConfig );
