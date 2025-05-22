#ifndef ALGORITHM_DARWIN_CONFIG_H_
# define ALGORITHM_DARWIN_CONFIG_H_

# include <string>
# include <vector>
# include <map>
# include <sstream>
class DarwinConfigException : public std::exception
{
    public:
        DarwinConfigException(std::string key_) : key(key_)        {}
        virtual const char* what() const throw()
        {
           return "Unknown config key";
        }
    private:
        std::string key;
};

/*
 * Singleton containing the content of darwin configuration
 */
class DarwinConfig
{
 public:
   // Options of type long
   static const std::vector<std::string> long_options_keys;

   // Options of type double
   static const std::vector<std::string> double_options_keys;

   // Options of type string
   static const std::vector<std::string> string_options_keys;

   template <typename T>
   static T get(std::string option);

   static DarwinConfig& getInstance()
   {
       static DarwinConfig    instance;
       return instance;
   }

   std::map<std::string, long>        long_options;
   std::map<std::string, double>      double_options;
   std::map<std::string, std::string> string_options;

    // Load a YAML configuration file.
    // Returns true in case of success
    static bool load(std::string  filepath);
    static bool is_loaded(bool fully=false);
    static void reset();

private:
  DarwinConfig() {}
  explicit  DarwinConfig(DarwinConfig const&) {}
  virtual   ~DarwinConfig() {}
  void operator=(DarwinConfig const&) {};
};

void        export_darwin_config();

#endif