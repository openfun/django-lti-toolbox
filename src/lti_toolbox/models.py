"""Declare the models related to lti provider."""

import secrets
import string

from django.db import models
from django.utils.translation import gettext_lazy as _


class LTIConsumer(models.Model):
    """
    Model representing a LTI Consumer.
    """

    slug = models.SlugField(
        verbose_name=_("consumer site identifier"),
        primary_key=True,
        help_text=_("identifier for the consumer site"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        help_text=_("human readable title, to describe the LTI consumer"),
        blank=False,
    )

    url = models.URLField(
        max_length=1024,
        verbose_name=_("Consumer site URL"),
        help_text=_("URL of the LTI consumer website"),
        blank=True,
    )

    class Meta:
        """Options for the ``LTIConsumer`` model."""

        db_table = "lti_consumer"
        verbose_name = _("LTI consumer")
        verbose_name_plural = _("LTI consumers")

    def __str__(self):
        """Get the string representation of an instance."""
        return self.title


class LTIPassport(models.Model):
    """
    Model representing an LTI passport for LTI consumers to interact with the django application.

    A LTI consumer can have multiple passports.

    An LTI passport stores credentials that can be used by an LTI consumer to interact with
    the django application acting as an LTI provider.
    """

    consumer = models.ForeignKey(LTIConsumer, on_delete=models.CASCADE)

    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        help_text=_(
            "human readable title, to describe this LTI passport (i.e. : who will use it ?)"
        ),
        blank=False,
    )

    oauth_consumer_key = models.CharField(
        max_length=255,
        verbose_name=_("oauth consumer key"),
        unique=True,
        help_text=_(
            "oauth consumer key to authenticate an LTI consumer on the LTI provider"
        ),
        editable=False,
    )
    shared_secret = models.CharField(
        max_length=255,
        verbose_name=_("shared secret"),
        help_text=_("LTI Shared secret"),
        editable=False,
    )
    is_enabled = models.BooleanField(
        verbose_name=_("is enabled"),
        help_text=_("whether the passport is enabled"),
        default=True,
    )

    class Meta:
        """Options for the ``LTIPassport`` model."""

        db_table = "lti_passport"
        verbose_name = _("LTI passport")
        verbose_name_plural = _("LTI passports")

    def __str__(self):
        """Get the string representation of an instance."""
        return self.title

    # pylint: disable=arguments-differ
    def save(self, *args, **kwargs):
        """Generate the oauth consumer key and shared secret randomly upon creation.

        Parameters
        ----------
        Args:
            args (list) Passed onto parent's `save` method
            dict (kwargs) : Passed onto parent's `save` method

        """
        self.full_clean()
        if not self.oauth_consumer_key:
            self.oauth_consumer_key = self.generate_consumer_key()
        if not self.shared_secret:
            self.shared_secret = self.generate_shared_secret()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_consumer_key() -> str:
        """Generate a random consumer key."""
        oauth_consumer_key_chars = string.ascii_uppercase + string.digits
        oauth_consumer_key_size = secrets.choice(range(20, 30))
        return "".join(
            secrets.choice(oauth_consumer_key_chars)
            for _ in range(oauth_consumer_key_size)
        )

    @staticmethod
    def generate_shared_secret() -> str:
        """Generate a random consumer key."""
        secret_chars = string.ascii_letters + string.digits + "!#$%&*+-=?@^_"
        secret_size = secret_size = secrets.choice(range(40, 60))
        return "".join(secrets.choice(secret_chars) for _ in range(secret_size))
