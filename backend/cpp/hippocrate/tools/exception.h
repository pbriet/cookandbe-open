#ifndef HIPPOCRATE_TOOLS_EXCEPTION_H
# define HIPPOCRATE_TOOLS_EXCEPTION_H

# include <string>
# include <sstream>
# include <exception>

# include "hippocrate/tools/print.h"
# include "hippocrate/tools/traceback.h"

// Macros simplifiant la manupulation des hp::Exception
# define INFOS(EXCEPTION)           hp::Exception::Infos(__FILE__, __LINE__, __FUNCTION__, __TIME__, EXCEPTION)
# define RAISE(ExceptionClass, ...) throw ExceptionClass(INFOS(#ExceptionClass), ##__VA_ARGS__);

namespace hp {
    /*
    ** Classe principale de laquelle doivent dériver toutes les exceptions d'Hippocrate.
    ** Contient un traceback et un système d'affichage de message.
    */
    struct Exception : public std::exception
    {
    public:
        /*
        ** Cette classe sert à regrouper l'ensemble des informations obtenues concernant la ligne déclenchant une exception.
        ** Elle s'utilise principalement via la macro RAISE(...) qui se charge de l'initialiser.
        */
        struct Infos
        {
            // Default format used to generate the info string
            static const std::string        defaultFormat;

            // Constructors
            explicit        Infos(const std::string & filename,
                                  unsigned int      line,
                                  const std::string & origin,
                                  const std::string & time,
                                  const std::string & exception);
            virtual         ~Infos() {}
            
            // Format function generating info string
            std::string     format(const std::string & s = defaultFormat) const;            

            // Public attributes
            std::string     filename;
            unsigned int    line;
            std::string     origin;
            std::string     time;
            std::string     exception;
        };

        // Constructeur par copie nécessaire pour le stringstream
        explicit                    Exception(const Exception & e);
        // Destructeur virtuel
        virtual                     ~Exception() throw();
        // Surcharge d'affichage de l'exception, nécessaire du fait de la derivation de std::exception
        virtual const char *        what() const throw() override;
        // Récupération du message
        const std::string  &        message() const;

    protected:
        // Constructeurs à appeler dans les classes filles
        explicit                    Exception(const Infos & infos);
        // Génération de la chaine de sortie
        virtual void                format(std::ostream & output, const Infos & infos, const Traceback & traceback) const;
        // Personnalisation du message (à spécialiser dans les classes filles)
        virtual std::ostream &      custom(std::ostream & output) const { return output; }

        // Attribut utilisé pour la construction du message
        Traceback                   _traceback;
        Infos                       _infos;
        std::string                 _prompt = "*!* ";

    private:
        // Attributs à usage interne, do not touch !
        mutable std::string         _message;
    };
} // ::hp

namespace hp {
    struct AssertionError : public Exception
    {
        explicit                    AssertionError(const Infos & infos, const std::string & expression, const std::string & message);
        virtual                     ~AssertionError() throw () {}
        virtual std::ostream &      custom(std::ostream & output) const override { return print(output, "Assertion Failed:", _expression, "\n", _message); }
        std::string                 _expression;
        std::string                 _message;
    };

    struct NotImplemented : public Exception
    {
        explicit                    NotImplemented(const Infos & infos) : Exception(infos) {}
        virtual                     ~NotImplemented() throw () {}
        virtual std::ostream &      custom(std::ostream & output) const override { return print(output, this->_infos.origin, "not implemented"); }
    };

    template <typename CONTAINER>
    struct ValueError : public Exception
    {
        typedef typename CONTAINER::value_type VALUE;
        explicit                    ValueError(const Infos & infos, const CONTAINER & c, const VALUE & v) : Exception(infos), container(c), value(v) {}
        virtual                     ~ValueError() throw () {}
        virtual std::ostream &      custom(std::ostream & output) const override { return print(output, value, "not in", container); }
        const CONTAINER             container;
        const VALUE                 value;
    };

    template <typename CONTAINER>
    struct KeyError : public Exception
    {
        typedef typename CONTAINER::key_type KEY;
        explicit                    KeyError(const Infos & infos, const CONTAINER & c, const KEY & k) : Exception(infos), container(c), key(k) {}
        virtual                     ~KeyError() throw () {}
        virtual std::ostream &      custom(std::ostream & output) const override { return print(output, "key error", key, "in", container); }
        const CONTAINER             container;
        const KEY                   key;
    };

    template <typename CONTAINER>
    struct IndexError : public Exception
    {
        explicit                    IndexError(const Infos & infos, const CONTAINER & c, const size_t & i) : Exception(infos), container(c), index(i) {}
        virtual                     ~IndexError() throw () {}
        virtual std::ostream &      custom(std::ostream & output) const override { return print(output, "index", index, "out of range in", container); }
        const CONTAINER             container;
        const size_t                index;
    };

    struct InternalError : public Exception
    {
        template <typename ... Args>
        InternalError(const Infos & infos, const Args & ... args);
                                    // InternalError(const Infos & infos, const std::string & message);
        virtual                     ~InternalError() throw () {}
        virtual std::ostream &      custom(std::ostream & output) const override { return print(output, "internal error:", _message); }
        std::string                 _message;
    };

    struct ArithmeticalError : public Exception
    {
                                    ArithmeticalError(const Infos & infos, const std::string & message);
        virtual                     ~ArithmeticalError() throw () {}
        virtual std::ostream &      custom(std::ostream & output) const override { return print(output, "arithmetical error:", _message); }
        std::string                 _message;
    };
} // ::hp

# include "hippocrate/tools/exception.hxx"

#endif // HIPPOCRATE_TOOLS_EXCEPTION_H
