
#include "hippocrate/tools/exception.h"
#include "hippocrate/tools/print.h"

using namespace hp;

Exception::Exception(const Exception & e)
    : _traceback(e._traceback), _infos(e._infos)
{}

Exception::Exception(const Infos & infos)
    : _infos(infos)
{}

Exception::~Exception() throw()
{}

/*
Surcharge de la méthode std::exception::what(), permettant d'afficher une exception.

Attention ! Le stockage de display() dans un attribut n'est pas une fantaisie d'un
développeur nul en optimisation ou atteint de démence ! C'est un mal nécessaire du fait
qu'on retourne un const char * qui ne doit pas être alloué dynamiquement (car le cas échéant
il ne serait jamais libéré...)
*/
const char *
Exception::what() const throw()
{
    return this->message().c_str();
}

const std::string &
Exception::message() const
{
    std::stringstream   buffer;
    
    this->format(buffer, this->_infos, this->_traceback);
    this->_message = buffer.str();
    return this->_message;
}

void
Exception::format(std::ostream & output, const Infos & infos, const Traceback & traceback) const
{
    output << std::endl << this->_prompt << infos.format() << std::endl << std::endl;
    this->custom(output);
    output << std::endl << "Traceback:" << std::endl << traceback.format() << std::endl;
}

Exception::Infos::Infos(const std::string & filename, unsigned int line, const std::string & origin, const std::string & time, const std::string & exception)
    : filename(filename), line(line), origin(origin), time(time), exception(exception)
{}

const std::string        Exception::Infos::defaultFormat = "%E raised at %T in file %F line %L from %O()";

std::string
Exception::Infos::format(const std::string & s) const
{
    std::string                             res(s);
    std::map<std::string, std::string>      formatStrings;

    // Initialization
    formatStrings["%F"] = this->filename;
    formatStrings["%L"] = std::to_string(this->line);
    formatStrings["%O"] = this->origin;
    formatStrings["%T"] = this->time;
    formatStrings["%E"] = this->exception;

    // Replacements
    for (auto   pair : formatStrings)
    {
        auto    pos = res.find(pair.first);
        
        if (pos != std::string::npos)
            res = res.replace(pos, pair.first.size(), pair.second);
    }
    return res;
}

AssertionError::AssertionError(const Infos & infos, const std::string & expression, const std::string & message)
    : Exception(infos), _expression(expression), _message(message)
{}

ArithmeticalError::ArithmeticalError(const Infos & infos, const std::string & message)
    : Exception(infos), _message(message)
{}
