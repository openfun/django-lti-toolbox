"""Forms definition for the demo LTI consumer."""

from django import forms
from django.utils.translation import gettext_lazy as _

from lti_toolbox.models import LTIPassport


class PassportChoiceField(forms.ModelChoiceField):
    """Select an LTI password"""

    def label_from_instance(self, obj):
        return f"{obj.consumer.slug} - {obj.title}"


class LTIConsumerForm(forms.Form):
    """Form to configure the standalone LTI consumer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    passport = PassportChoiceField(
        queryset=LTIPassport.objects.all(), empty_label=None, label="Consumer"
    )

    user_id = forms.CharField(
        label="User ID",
        max_length=100,
        initial="jojo",
    )

    context_id = forms.CharField(
        label="Context ID",
        max_length=100,
        initial="course-v1:openfun+mathematics101+session01",
    )

    course_title = forms.CharField(
        label="Course Title", max_length=100, initial="Mathematics 101"
    )

    role = forms.ChoiceField(
        choices=(
            ("Student", _("Student")),
            ("Instructor", _("Instructor")),
        )
    )

    action = forms.ChoiceField(
        choices=(
            ("lti.launch-url-verification", "Verify LTI launch request"),
            ("lti.launch-url-auth", "Verify + authenticate user"),
            (
                "lti.launch-url-auth-with-params",
                "Verify + authenticate user + dynamic URL",
            ),
        ),
        initial="simple",
        required=True,
    )

    presentation_locale = forms.ChoiceField(
        choices=(("fr", "fr"), ("en", "en"), ("", "--none--")),
        initial="fr",
        label="Locale",
        required=False,
    )
