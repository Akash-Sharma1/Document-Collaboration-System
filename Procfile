web: daphne docs.asgi:channel_layer --port 5050 --bind 0.0.0.0 -v2
python manage.py collectstatic --noinput
manage.py migrate