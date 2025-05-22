
#include <boost/test/unit_test.hpp>
#include <boost/test/output_test_stream.hpp> 

#include "hippocrate/tests/tools.h"
#include "hippocrate/tools/container.h"
#include "hippocrate/tools/iter.h"
#include "hippocrate/tools/math.h"

BOOST_AUTO_TEST_SUITE(tools_suite)

using boost::test_tools::output_test_stream;

BOOST_AUTO_TEST_CASE(print_types)
{
    std::streambuf      * coutBackup = std::cout.rdbuf();
    std::streambuf      * cerrBackup = std::cerr.rdbuf();
    std::stringstream   tmpCout, tmpCerr;
    const std::string   str = "test";
    
    // Redirecting standard outputs
    std::cout.rdbuf(tmpCout.rdbuf());
    std::cerr.rdbuf(tmpCerr.rdbuf());

    // Doing some tests...
    print();                    // Empty
    print(0);                   // Temporary object
    print(1, 7.42, str);        // Multi types (including const)
    print(std::cerr, 0, str);   // Changing output
    print("there is no ", Printer::noend);
    print("newline here");

    // Restoring standard outputs
    std::cout.rdbuf(coutBackup);
    std::cerr.rdbuf(cerrBackup);
    
    // Checking results...
    BOOST_CHECK_EQUAL(tmpCout.str(), "\n0\n1 7.42 test\nthere is no newline here\n");
    BOOST_CHECK_EQUAL(tmpCerr.str(), "0 test\n");

    // With redirections
    output_test_stream      output;
    print(output, 1, 2, 3, str, Printer::noend);
    BOOST_CHECK(output.is_equal("1 2 3 test"));
}

BOOST_AUTO_TEST_CASE(print_containers)
{
    output_test_stream      output;
    const std::vector<int>  tab = {1, 2, 3};
    const std::list<int>    list = {1, 2, 3};
    std::map<float, long>   map;
    std::set<int>           set = {1, 2, 3, 3, 0};
    std::list<std::map<float, long> > multi;
    
    // init
    map[42.0] = 69;
    map[3.14116] = 1337;
    multi.push_back(map);
    
    print(output, tab);                 // Vector
    BOOST_CHECK(output.is_equal("< 1, 2, 3 >\n"));
    print(output, map);                 // Map
    BOOST_CHECK(output.is_equal("{ 3.14116 : 1337, 42 : 69 }\n"));
    print(output, list);                // List
    BOOST_CHECK(output.is_equal("[ 1, 2, 3 ]\n"));
    print(output, set);                 // Set
    BOOST_CHECK(output.is_equal("{ 0, 1, 2, 3 }\n"));
    print(output, multi);               // Nested containers
    BOOST_CHECK(output.is_equal("[ { 3.14116 : 1337, 42 : 69 } ]\n"));
    print(output, list, multi, set);    // All together
    BOOST_CHECK(output.is_equal("[ 1, 2, 3 ] [ { 3.14116 : 1337, 42 : 69 } ] { 0, 1, 2, 3 }\n"));
}

typedef TemplatedTestException<ExceptionTestClass> TypedefTemplatedTestException;

void    exception_raising_function()
{
    RAISE(TypedefTemplatedTestException, ExceptionTestClass());
}

BOOST_AUTO_TEST_CASE(exceptions)
{
    BOOST_REQUIRE_THROW(RAISE(TypedefTemplatedTestException, ExceptionTestClass()), TypedefTemplatedTestException);
    
    // Custom nested templated exception
    try {
        exception_raising_function();
    } catch (TypedefTemplatedTestException & e) {
        std::string     msg = e.message();

        BOOST_CHECK(msg.find(ExceptionTestClass::text()) != std::string::npos);
        BOOST_CHECK(msg.find("exception_raising_function") != std::string::npos);
    }
    // AssertionError exception
    try {
        ASSERT(false && true, "Meurs !");
    } catch (hp::AssertionError & e) {
        std::string     msg = e.message();

        BOOST_CHECK(msg.find("false && true") != std::string::npos);
        BOOST_CHECK(msg.find("Meurs !") != std::string::npos);
    }
    // ValueError exception with local addressed container
    try {
        std::vector<int>    range3 = {0, 1, 2};
        hp::get_index(range3, 42);
    } catch (hp::ValueError<std::vector<int> > & e) {
        std::string     msg = e.message();

        BOOST_CHECK(msg.find("42 not in < 0, 1, 2 >") != std::string::npos);
    }
}


#define CHECK_COMBINATION_DIM1(iterator)\
  BOOST_CHECK(iterator.value().size() == 1 && iterator.value()[0] == 1);\
  BOOST_CHECK(iterator.next());\
  BOOST_CHECK(iterator.value().size() == 1 && iterator.value()[0] == 4);\
  BOOST_CHECK(iterator.next());\
  BOOST_CHECK(iterator.value().size() == 1 && iterator.value()[0] == 7);

#define CHECK_COMBINATION_DIM2(iterator)\
  BOOST_CHECK(iterator.value().size() == 2 && iterator.value()[0] == 1\
                                           && iterator.value()[1] == 4);\
  BOOST_CHECK(iterator.next());\
  BOOST_CHECK(iterator.value().size() == 2 && iterator.value()[0] == 1\
                                           && iterator.value()[1] == 7);\
  BOOST_CHECK(iterator.next());\
  BOOST_CHECK(iterator.value().size() == 2 && iterator.value()[0] == 4\
                                           && iterator.value()[1] == 7);

#define CHECK_COMBINATION_DIM3(iterator)\
  BOOST_CHECK(iterator.value().size() == 3 && iterator.value()[0] == 1\
                                           && iterator.value()[1] == 4\
                                           && iterator.value()[2] == 7);

  
BOOST_AUTO_TEST_CASE(combination_iterator)
{
  std::vector<int> elements = {1, 4, 7};

  hp::CombinationIterator<int> it_one_element(elements, (uint) 1);
  CHECK_COMBINATION_DIM1(it_one_element);
  BOOST_CHECK(!(it_one_element.next()));

  hp::CombinationIterator<int> it_two_elements(elements, (uint) 2);
  CHECK_COMBINATION_DIM2(it_two_elements);
  BOOST_CHECK(!(it_two_elements.next()));

  hp::CombinationIterator<int> it_three_elements(elements, (uint) 3);
  CHECK_COMBINATION_DIM3(it_three_elements);
  BOOST_CHECK(!(it_three_elements.next()));

  hp::CombinationIterator<int> it_all_elements(elements, 3, true);
  CHECK_COMBINATION_DIM1(it_all_elements);
  BOOST_CHECK(it_all_elements.next());
  CHECK_COMBINATION_DIM2(it_all_elements);
  BOOST_CHECK(it_all_elements.next());
  CHECK_COMBINATION_DIM3(it_all_elements);
  BOOST_CHECK(!(it_all_elements.next()));
}


BOOST_AUTO_TEST_CASE(concatenation)
{
  std::vector<int>  els1 = {1, 4, 7};
  std::vector<int>  els2 = {7, -5, 2};
  
  std::vector<int>  res = hp::concatenate(els1, els2);
  std::vector<int>  expected = {1, 4, 7, 7, -5, 2};
  BOOST_CHECK_EQUAL(res, expected);
}

BOOST_AUTO_TEST_CASE(tools_math)
{
    BOOST_CHECK_EQUAL(::hp::mod(42, -5), 2);
    #ifdef DEBUG
    BOOST_CHECK_THROW(::hp::mod(42, 0), ::hp::ArithmeticalError);
    #endif // DEBUG
}

/*
BOOST_AUTO_TEST_CASE(traceback)
{
    print("normal traceback", getTraceback());
    try
    {
        exception_raising_function();
    } catch (const std::exception & e) {
        dumpTrace(e, "lol");
    }
    ASSERT(true && false, "plop", "plip", 42);
}
*/

BOOST_AUTO_TEST_SUITE_END()
