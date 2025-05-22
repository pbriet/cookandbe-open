#ifndef PROBLEM_HXX_
# define PROBLEM_HXX_

# include "hippocrate/models/problem.h"
# include "hippocrate/tools/python.h"

template <typename AlgorithmT>
Solution  Problem::solve()
{
  hp::python::unlocker autolock;

  return AlgorithmT(this).solve();
}

#endif
