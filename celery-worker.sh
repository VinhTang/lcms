#!/bin/sh
celery -A project.celeryapp:app worker -l info
