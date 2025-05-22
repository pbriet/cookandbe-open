#/bin/sh
./manage.py migrate --noinput --fake abtest
./manage.py migrate --noinput --fake articles
./manage.py migrate --noinput --fake blogs
./manage.py migrate --noinput --fake diet_mgr
./manage.py migrate --noinput --fake discussion
./manage.py migrate --noinput --fake newsletters
./manage.py migrate --noinput --fake notify_mgr
./manage.py migrate --noinput --fake nutrient
./manage.py migrate --noinput --fake paybox
./manage.py migrate --noinput --fake planning_mgr
./manage.py migrate --noinput --fake polls
./manage.py migrate --noinput --fake pro
./manage.py migrate --noinput --fake profile_mgr
./manage.py migrate --noinput --fake recipe_mgr
./manage.py migrate --noinput --fake shopping_mgr
./manage.py migrate --noinput --fake user_mgr
