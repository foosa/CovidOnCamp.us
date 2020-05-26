# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
from flask import flash, Markup


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text} - {Markup(error)}", category)

def get_random_alphaNumeric_string(stringLength=8):
    import random
    import string
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))

