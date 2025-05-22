#ifndef HIPPOCRATE_TOOLS_PYTHON_H_
# define HIPPOCRATE_TOOLS_PYTHON_H_

# include <boost/utility.hpp>
# include <boost/python/handle.hpp>
# include <boost/python/object.hpp>

namespace hp
{
  namespace python
  {
    /*
    ** Used to unlock the GIL in current scope (ExceptionSafe)
    */
    class unlocker : private boost::noncopyable
    {
    public:
      // Used to unlock/lock the GIL upon entering/exiting the scope
      explicit                unlocker();
      virtual                 ~unlocker();
    private:
      PyThreadState           * _threadState;
    };

    /*
    ** Used to lock the GIL in current scope (ExceptionSafe)
    */
    class locker : private boost::noncopyable
    {
    public:
      // Used to lock/unlock the GIL upon entering/exiting the scope
      explicit                locker();
      virtual                 ~locker();
      // Manual unlock
      void                    unlock();
    private:
      bool                    _locked;
      PyGILState_STATE        _gstate;
    };
  }
}

#endif // HIPPOCRATE_TOOLS_PYTHON_H_