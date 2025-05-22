#ifndef HIPPOCRATE_PRINT_H_
# define HIPPOCRATE_PRINT_H_

# include <iostream>
# include <fstream>
# include <vector>
# include <list>
# include <map>
# include <set>

# define PRINT(...) \
    Printer(__FILE__, __LINE__, true).stream_print(std::cout, __VA_ARGS__);

# define OVERLOAD_ND_CONTAINER(START, END)  \
    {                                       \
        auto    delim = "";                 \
        os << START;                        \
        for (auto element : container)      \
        {                                   \
            os << delim << element;         \
            delim = ", ";                   \
        }                                   \
        return os << END;                   \
    }

# define OVERLOAD_1D_CONTAINER(NAME, START, END)                                        \
    template <typename T>                                                               \
    inline std::ostream & operator << (std::ostream & os, const NAME<T> & container)    \
    OVERLOAD_ND_CONTAINER(START, END)

# define OVERLOAD_2D_CONTAINER(NAME, START, END)                                        \
    template <typename K, typename V>                                                   \
    inline std::ostream & operator << (std::ostream & os, const NAME<K, V> & container) \
    OVERLOAD_ND_CONTAINER(START, END)

namespace std
{
    // Specializations
    template <typename K, typename V>
    inline std::ostream &   operator << (std::ostream & os, const std::pair<K, V> & p) 
    {
        return os << p.first << " : " << p.second;
    }

    OVERLOAD_1D_CONTAINER(std::vector,  "< ", " >")
    OVERLOAD_1D_CONTAINER(std::set,     "{ ", " }")
    OVERLOAD_1D_CONTAINER(std::list,    "[ ", " ]")
    OVERLOAD_2D_CONTAINER(std::map,     "{ ", " }")
}

/*
** Internal functions used by print
*/
class Printer
{
public:
    class NoEnd
    {
        friend Printer;
        private:
            explicit NoEnd() {}
    };
    static const NoEnd      noend;

    static std::string      separator;
    static std::string      empty;

    explicit                Printer(bool addTime = false) : _stream(nullptr), _newStream(true), _file(""), _line(0), _addTime(addTime) {}
    explicit                Printer(const std::string & file, long line, bool addTime = false) : _stream(nullptr), _newStream(true), _file(file), _line(line), _addTime(addTime) {}
    virtual                 ~Printer() {}

    /*
    ** print_element functions are used to add arguments 1 by 1 to the current stream
    */
    template <typename T>
    std::ostream &
    print_element(std::ostream & os, T & t, const std::string & separator)
    {
        if (this->_newStream)
        {
            if (this->_line != 0)   os << this->_file << ":" << this->_line << " ";
            if (this->_addTime)     os << __TIME__ << " > ";
            this->_newStream = false;
        }
        else
            os << separator;
        return os << t;
    }

    /*
    ** stream_print functions are used to process variadic templates Args ...
    */
    std::ostream &
    stream_print(std::ostream & os)
    {
        return os << std::endl;
    }

    template <typename T>
    std::ostream &
    stream_print(std::ostream & os, T & t)
    {
        std::ostream    & new_os = this->print_element(os, t, Printer::separator);

        return new_os << std::endl;
    }
        
    template <typename T, typename ... Args>
    std::ostream &
    stream_print(std::ostream & os, T & t, Args & ... args)
    {
        std::ostream    & new_os = this->print_element(os, t, Printer::separator);
        return this->stream_print(new_os, args ...);
    }
    
    std::ostream &      switchStream(std::ostream & new_os)
    {
        if (this->_stream != &new_os && !this->_newStream)
            (*this->_stream) << std::endl;
        this->_newStream = true;
        this->_stream = &new_os;
        return new_os;
    }

protected:
    std::ostream            * _stream;
    bool                    _newStream;
    const std::string       _file;
    long                    _line;
    bool                    _addTime;
};

// Specializations
template <>
std::ostream &
Printer::print_element(std::ostream & os, std::ostream & new_os, const std::string & );

template <>
std::ostream &
Printer::print_element(std::ostream & os, std::stringstream & new_os, const std::string & );

template <>
std::ostream &
Printer::stream_print(std::ostream & os, const Printer::NoEnd &);

namespace boost { namespace test_tools { class output_test_stream; }}

template <>
std::ostream &
Printer::print_element(std::ostream & os, std::stringstream & new_os, const std::string & );

template <>
std::ostream &
Printer::print_element(std::ostream & os, std::ofstream & new_os, const std::string & );

template <>
std::ostream &
Printer::print_element(std::ostream & os, boost::test_tools::output_test_stream & new_os, const std::string & );

// Public functions
template <typename ... Args>
std::ostream &
print(Args && ... args)
{
  return Printer(false).stream_print<Args ...>(std::cout, args ...);
}

template <typename ... Args>
std::string
sprint(Args && ... args)
{
  std::stringstream   ss;
  
  print(ss, args ..., Printer::noend);
  return ss.str();
}

// Convenient overload for empty call
std::ostream &
print();

/*
TODO:
- Meilleur découpage des méthodes (statiques/locales)
- Personnalisation des séparateurs
- Factorisation du remplacement de flux
- Unification du fonctionnement des flux (parfois en arguments, maintenant en variables)
- Ajouter davantage de tests ! (surtout sur les dernières fonctionnalités)

Sources:
- variadic macros http://gcc.gnu.org/onlinedocs/cpp/Variadic-Macros.html
- backtrace       http://mykospark.net/2009/09/runtime-backtrace-in-c-with-name-demangling/
- exception trace http://stackoverflow.com/questions/3355683/c-stack-trace-from-unhandled-exception
                  http://stackoverflow.com/questions/4283943/getting-the-backtrace-from-the-catch-block

*/

#endif // HIPPOCRATE_PRINT_H_