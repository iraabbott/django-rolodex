#!/usr/bin/env python
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "testproject.settings"

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
