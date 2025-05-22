#ifndef HIPPOCRATE_DATA_INDEXER_H_
# define HIPPOCRATE_DATA_INDEXER_H_

# include <map>
# include <string>
# include <boost/noncopyable.hpp>

# include "hippocrate/tools/container.h"

/*
 * Class that associates an id for each kind of data
 * stored in a recipe
 */
class RecipeDataIndexer : private boost::noncopyable
{
public:
  static RecipeDataIndexer * get_instance();
    
  // Add a <key> to the index, and associate an id to it
  void add_to_index(const std::string&);
  // Returns an id associated to this key  (or raises an Error)
  inline unsigned long id_from_key(const std::string& key) const{
    if (!hp::has_key(this->data_key_to_id, key))
      RAISE(hp::InternalError, sprint("No such key in index : ", key, " -- Have you correctly called MainRecipeStorage.init_indexer() ?"));
    return this->data_key_to_id.at(key);
  }
  inline unsigned long operator[](const std::string& key) const{
    return this->id_from_key(key);
  }
  
  unsigned long nb_indexed() const { return this->max_id; }
  
  void reset();
  
  static RecipeDataIndexer              & instance;
  
private:
  virtual   ~RecipeDataIndexer() {}
  explicit  RecipeDataIndexer() : boost::noncopyable() { this->max_id = 0; }
  
  std::map<const std::string, long>     data_key_to_id;
  unsigned long                         max_id;
};

void export_data_indexer();


#endif /* HIPPOCRATE_DATA_INDEXER_H_ */