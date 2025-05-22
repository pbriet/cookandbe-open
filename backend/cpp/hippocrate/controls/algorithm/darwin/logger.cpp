
#include <math.h>
#include "hippocrate/tools/debug.h"
#include "hippocrate/controls/algorithm/darwin/logger.h"
#include "hippocrate/controls/algorithm/darwin/config.h"

void DarwinProfiler::startNew()
{
  ASSERT(!(this->profiling_in_progress), "Starting multiple profilers simultaneously");
  this->profiling_in_progress = true;
  const char    filename_format[] = "%Y-%m-%d_%Hh%Mm%Ss";
  const char    time_format[] = "%Y-%m-%d %H:%M:%S";
  const int     filename_buffer_length = 21;
  const int     time_buffer_length = 20;
  // Retrieve current time
  time_t        timevalue;
  struct tm *   timeinfo;
  char          filename_buffer[filename_buffer_length], time_buffer[time_buffer_length];
  time(&timevalue);
  timeinfo = localtime(&timevalue);
  strftime(time_buffer, time_buffer_length, time_format, timeinfo);
  strftime(filename_buffer, filename_buffer_length, filename_format, timeinfo);


  std::stringstream     filename;
  filename << "hippocrate/benchmark/darwin_score_" << filename_buffer << ".yml";
  print("Writing results in", filename.str());
  this->stream.open(filename.str());

  print(this->stream, "time:", time_buffer);
  print(this->stream, "options:");
  for (auto option_key: DarwinConfig::string_options_keys)
    print(this->stream, "  ", option_key, ": ", DarwinConfig::get<std::string>(option_key));
  for (auto option_key: DarwinConfig::long_options_keys)
    print(this->stream, "  ", option_key, ": ", DarwinConfig::get<long>(option_key));
  for (auto option_key: DarwinConfig::double_options_keys)
    print(this->stream, "  ", option_key, ": ", DarwinConfig::get<double>(option_key));
  
  print(this->stream, "data:");
  this->stream.flush();
  this->cumulative_time = 0;
  this->last_clock = hp::Clock::now();
}

void DarwinProfiler::log_score(long score)
{
  hp::Clock::time_point t = hp::Clock::now();
  hp::milliseconds elapsed_time = std::chrono::duration_cast<hp::milliseconds>(t - this->last_clock);
  this->cumulative_time += elapsed_time.count();
  print(this->stream, "  -", "[", this->cumulative_time, ", ", score, "]");
  this->last_clock = hp::Clock::now();
}

void DarwinProfiler::end()
{
  this->stream.close();
  ASSERT(this->profiling_in_progress, "Darwin profiler : not in progress before end ?");
  this->profiling_in_progress = false;
}