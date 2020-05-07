web: daphne docs.asgi:channel_layer --port $5000 --bind 0.0.0.0 -v2
worker: python manage.py runworker -v2
python manage.py collectstatic --noinput
manage.py migrate