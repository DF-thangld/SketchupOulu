Requirement: Python 3.4

pip install -r requirements.txt

To run the application: sudo uwsgi --socket 0.0.0.0:80 --protocol=http -w wsgi:app