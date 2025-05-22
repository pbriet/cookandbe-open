#ifndef HIPPOCRATE_TOOLS_STATS
# define HIPPOCRATE_TOOLS_STATS

# include <map>
# include <string>

# include "hippocrate/tools/types.h"

# ifdef DARWIN_ENABLE_BENCHMARK
#  define HP_STATS_ENABLED  1
# else
#  define HP_STATS_ENABLED  0
# endif

# if HP_STATS_ENABLED == 0
#  define HP_STAT_AUTOSAVE(CONTAINER, KEY)
# else
#  define HP_STAT_AUTOSAVE(CONTAINER, KEY) hp::stats::autosave   __stat(CONTAINER, KEY);
# endif

namespace hp {
  namespace stats {
  
    // Statistics container
    struct Call {
      uint64_t  total_time = 0;
      uint64_t  min_time = 0;
      uint64_t  max_time = 0;
      uint64_t  count = 0;
      
      void      add(uint64_t call_time);
      uint64_t  average_time() const { return (this->count > 0) ? this->total_time / this->count : 0; }
    };
    
    typedef std::map<const std::string, hp::stats::Call>  CallDict;
    
    // Automatically stores statistics into a container when entering/leaving the scope
    class autosave {
      public:
        explicit  autosave(CallDict & container, const std::string & key) : container(container), key(key), start_time(hp::Clock::now()) {}
        virtual   ~autosave();
        
      protected:
        CallDict                & container;
        const std::string       key;
        hp::Clock::time_point   start_time;
    };
  }
}

void export_tools_stats();

#endif