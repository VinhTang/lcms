import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ComplexPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("Mật khẩu phải có ít nhất 8 ký tự."),
                code='password_too_short',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Mật khẩu phải chứa ít nhất một chữ cái viết hoa."),
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Mật khẩu phải chứa ít nhất một chữ cái viết thường."),
                code='password_no_lower',
            )
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("Mật khẩu phải chứa ít nhất một con số."),
                code='password_no_number',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Mật khẩu phải chứa ít nhất một ký tự đặc biệt."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Mật khẩu của bạn phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt."
        )
