#!/bin/sh
celery -A project.celeryapp:app beat -S redbeat.RedBeatScheduler -l info
