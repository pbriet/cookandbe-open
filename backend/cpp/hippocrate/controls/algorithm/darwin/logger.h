#ifndef _DARWIN_CONTROLLER_LOGGER_H_
# define _DARWIN_CONTROLLER_LOGGER_H_

# include <fstream>
# include "hippocrate/tools/types.h"
# include "hippocrate/tools/print.h"

# ifndef NDEBUG
#  define DARWIN_LOG(...) print(DarwinLogger::getInstance().stream, ##__VA_ARGS__) && DarwinLogger::getInstance().stream.flush()
# else
#  define DARWIN_LOG(...)
# endif

# ifdef DARWIN_ENABLE_BENCHMARK
#  define DARWIN_START_PROFILING(...)\
           DarwinProfiler::getInstance().startNew();\
           RandomGenerator::reinit_seed(42)
#  define DARWIN_END_PROFILING(...)   DarwinProfiler::getInstance().end()
#  define DARWIN_PROFILE(score)       DarwinProfiler::getInstance().log_score(score)
# else
#  ifdef DARWIN_GOOGLE_PROFILING
#   include <gperftools/profiler.h>
#   define DARWIN_START_PROFILING(...)\
           ProfilerStart("/vagrant/django/hippocrate/darwin.prof");\
           RandomGenerator::reinit_seed(42)
#   define DARWIN_END_PROFILING(...)    ProfilerStop();
#   define DARWIN_PROFILE(...)
#  else
#   define DARWIN_START_PROFILING(...)
#   define DARWIN_END_PROFILING(...)
#   define DARWIN_PROFILE(...)
#  endif
# endif


// Darwin logger is a simple singleton with one ofstream
class DarwinLogger
{
 public:
    static DarwinLogger& getInstance()
    {
        static DarwinLogger    instance;
        return instance;
    }

  std::ofstream   stream;

private:
  DarwinLogger() { this->stream.open("darwin.log");}
  explicit  DarwinLogger(DarwinLogger const&) { }
  virtual   ~DarwinLogger() { this->stream.close(); }
  void operator=(DarwinLogger const&) {};
};


class DarwinProfiler
{
 public:
    static DarwinProfiler& getInstance()
    {
        static DarwinProfiler    instance;
        return instance;
    }
    void startNew();
    void end();
    void log_score(long score);
    bool profiling_in_progress = false;
    std::ofstream   stream;

private:
  DarwinProfiler() { }
  explicit  DarwinProfiler(DarwinProfiler const&) { }
  virtual   ~DarwinProfiler() { }
  void operator=(DarwinProfiler const&) {};

  hp::Clock::time_point   last_clock;
  long                    cumulative_time;
};

#endif