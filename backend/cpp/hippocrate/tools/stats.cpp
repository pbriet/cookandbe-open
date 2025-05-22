
#include "hippocrate/tools/stats.h"
#include "hippocrate/tools/debug.h"

#include <boost/python.hpp>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>

void
hp::stats::Call::add(uint64_t call_time) {
  if (this->count == 0) {
    this->max_time = this->min_time = call_time;
  }
  this->total_time += call_time;
  if (call_time > this->max_time)
    this->max_time = call_time;
  if (call_time < this->min_time)
    this->min_time = call_time;
  ++this->count;
}

hp::stats::autosave::~autosave() {
  // ASSERT(this->start_time > hp::Clock::time_point(), "autosave time not initialized");
  hp::milliseconds elapsed_time = std::chrono::duration_cast<hp::milliseconds>(hp::Clock::now() - this->start_time);
  this->container[this->key].add(elapsed_time.count());
}

void export_tools_stats()
{
  using namespace boost::python;

  class_<hp::stats::Call>("HpStatsCall")
    .def_readonly("total_time",      &hp::stats::Call::total_time)
    .def_readonly("min_time",        &hp::stats::Call::min_time)
    .def_readonly("max_time",        &hp::stats::Call::max_time)
    .def_readonly("count",           &hp::stats::Call::count)
    .def_readonly("average_time",    &hp::stats::Call::average_time);

  class_<std::map<const std::string, hp::stats::Call> >("HpStatsCallDict")
      .def(map_indexing_suite<std::map<const std::string, hp::stats::Call> >() );
}
