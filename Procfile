web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn lcms.wsgi --workers 2 --timeout 120
