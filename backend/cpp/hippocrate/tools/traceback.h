#ifndef HIPPOCRATE_TOOLS_TRACEBACK_H_
# define HIPPOCRATE_TOOLS_TRACEBACK_H_

# include <string>
# include <vector>

namespace hp {
    /*
    ** Class used to manage tracebacks.
    ** Requires -rdynamic in linker options to display readable symbols
    */
    class Traceback
    {
    public:
        // Consts
        static const unsigned int MAX_FRAMES = 100;
        
        // Représente une pile d'appels
        typedef std::vector<std::string>    Trace;
        
        // Constructor
        explicit                Traceback();
        virtual                 ~Traceback() {}
        
        // Demangle a C++ traceback symbol
        static std::string      demangle(const char * symbol);
        // Génération du traceback
        static void             generate(Trace &);
        // Conversion en chaine de caractères
        static std::string      str(long max_lines = 20, const std::string & separator = "\n");
        // Affichage en chaine de carractères
        std::string             format(size_t first = 2, const std::string & separator = "\n") const;
        
        // Pile d'appels
        Trace                   trace;
    };
} // ::hp

/*
TODO: make it works with non boost exceptions.
- By creating a custom exception hierarchy: http://code-freeze.blogspot.fr/2012/01/generating-stack-traces-from-c.html
- By twiking g++: http://blog.sjinks.pro/c-cpp/969-track-uncaught-exceptions/
                  http://stackoverflow.com/questions/11665829/how-can-i-print-stack-trace-for-caught-exceptions-in-c-code-injection-in-c
- Official backtrace doc: http://man7.org/linux/man-pages/man3/backtrace.3.html

typedef boost::error_info<struct tag_stack_str, std::string> stack_info;

template <typename EXCEPTION>
void dumpTrace(const EXCEPTION & e, const char* context) {
    std::cerr << "------------------------------------------------------------------------" << std::endl;
    // std::cerr << context << ": " << e.what() << std::endl;
    std::string const *stack = boost::get_error_info<stack_info>(e);
    if (stack) {
        std::cerr << "Stack Trace:" << std::endl << stack << std::endl;
    }
    std::cerr << stack << " ------------------------------------------------------------------------" << std::endl;
}
*/

#endif // HIPPOCRATE_TOOLS_TRACEBACK_H_
