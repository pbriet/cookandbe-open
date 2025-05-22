#ifndef HIPPOCRATE_TOOLS_RANDOM_H_
# define HIPPOCRATE_TOOLS_RANDOM_H_

# include <map>
# include <random>

class RandomGenerator
{
 public:
    static RandomGenerator& getInstance()
    {
        static RandomGenerator    instance;
        return instance;
    }
    
  std::default_random_engine        random_engine;
  std::normal_distribution<double>  norm_distrib;

  static void reinit_seed(long value);
  static long rand();
  static bool in_percentage(double percentage);
  
  static double get_norm_distrib_value(double gauss_center, double stddev);

  /*
   * Randomly picks one value in a vector
   */
  template <typename T>
  static T pick(const std::vector<T> &values);

  /*
   * Randomly picks one key in a map
   */
  template <typename T, typename U>
  static const T & pick_key(const std::map<T, U> &values);
  
  /*
   * Randomly picks one value in a map
   */
  template <typename T, typename U>
  static const U & pick_value(const std::map<T, U> &values);
  
  /*
   * Randomly picks one of the key, given the probabilistic distribution of the values
   * total_cost is the sum of values (if <= 0, will be calculated)
   */
  template <typename T>
  static T pick_distrib_value(const std::map<T, long> &distrib, long total_cost = 0);
  
  /*
   * Same as previously, but with a vector  (considered as a dictionnary uint -> value)
   */
  template <typename T>
  static uint pick_distrib_value(const std::vector<T> &distrib, long total_cost = 0);

private:
  RandomGenerator() {}
  explicit  RandomGenerator(RandomGenerator const&) {}
  virtual   ~RandomGenerator() {}
  void operator=(RandomGenerator const&) {};
};

void export_tools();

# include "hippocrate/tools/random.hxx"

#endif // HIPPOCRATE_TOOLS_RANDOM_H_
