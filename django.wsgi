import os
import sys

path = 'C:/Users/jjh/Documents/GitHub/hengdian'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'hengdian.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()