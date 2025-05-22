cd /vagrant/angular && grunt build || return
sudo service postgresql start
sudo service gunicorn stop
sudo service nginx start
cd /vagrant/django && python manage.py runserver