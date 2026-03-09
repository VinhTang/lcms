import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lcms.settings')
django.setup()

from django.apps import apps
histories = []
for model in apps.get_models():
    if hasattr(model, 'history') and hasattr(model.history, 'all'):
        print(f"Fetching for {model}")
        qs = model.history.all()
        logs = qs.order_by('-history_date')[:100]
        # try to iterate to force evaluation
        for log in logs:
            if log.history_type == '~':
                prev = getattr(log, 'prev_record', None)
                if prev:
                    try:
                        delta = log.diff_against(prev)
                    except Exception as e:
                        print(f"DIFF ERROR: {e}")

print("Done")
