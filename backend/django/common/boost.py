"""
A few helpers to manipulate boost objects
"""

def to_dict(boost_dict):
    """
    Returns a Python dictionnary from a C++ dictionnary
    wrapped with indexing_suite
    """
    if type(boost_dict) is dict:
        return boost_dict
    return dict((pair.key(), pair.data()) for pair in boost_dict)


def to_list(boost_vector):
    if type(boost_vector) is list:
        return boost_vector
    return [value for value in boost_vector]

def from_dict(py_dict, boost_cls):
    """
    From a python dictionnary and a wrapped C++ map class, returns a C++ instance
    """
    res = boost_cls()
    for key, val in py_dict.items():
        res[key] = val
    return res

def from_list(py_list, boost_cls):
    """
    From a python list and a wrapped C++ vector class, returns a C++ instance
    """
    res = boost_cls()
    for val in py_list:
        res.append(val)
    return res