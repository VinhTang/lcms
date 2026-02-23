#!/bin/sh
gunicorn project.wsgi --log-file -
