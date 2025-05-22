# Warning! Removes all the database
cd /vagrant/src/django && python manage.py sqlclear recipe_mgr | python manage.py dbshell && python manage.py syncdb

cd /vagrant/scripts/cnf && ./fill_from_cnf.sh

