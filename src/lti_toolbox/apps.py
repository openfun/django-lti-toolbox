"""lti_toolbox application."""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LtiProviderAppConfig(AppConfig):
    """Configuration class for the lti_toolbox app."""

    verbose_name = _("LTI Toolbox")
    name = "lti_toolbox"
