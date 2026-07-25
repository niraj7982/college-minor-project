import sys
from django.template.loader import get_template
from django.template.exceptions import TemplateSyntaxError

try:
    template = get_template('core/view_attendance_debug.html')
    print("SUCCESS: Template loaded correctly.")
except TemplateSyntaxError as e:
    print(f"ERROR: {e}")
    # Print more details about exception if available
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"UNKNOWN ERROR: {e}")
    import traceback
    traceback.print_exc()
