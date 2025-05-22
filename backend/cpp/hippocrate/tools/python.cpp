
#include "hippocrate/tools/python.h"

using namespace hp::python;

unlocker::unlocker() : boost::noncopyable()
{
    this->_threadState = PyEval_SaveThread();
}

unlocker::~unlocker()
{
    PyEval_RestoreThread(this->_threadState);
}

locker::locker() : boost::noncopyable(), _locked(true)
{
    this->_gstate = PyGILState_Ensure();
}

void
locker::unlock()
{
    if (this->_locked)
    {
        PyGILState_Release(this->_gstate);
        this->_locked = false;
    }
}

locker::~locker()
{
    this->unlock();
}
