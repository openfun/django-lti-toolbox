"""Factories for the ``lti_toolbox``."""
import factory
from factory.django import DjangoModelFactory

from . import models


class LTIConsumerFactory(DjangoModelFactory):
    """Factory to create LTI consumer."""

    class Meta:
        model = models.LTIConsumer
        django_get_or_create = ("slug",)

    slug = factory.Sequence(lambda n: f"consumer{n}")
    title = factory.Sequence(lambda n: f"Consumer {n}")
    url = factory.Sequence(lambda n: f"https://www.example.com/consumer-{n}/")


class LTIPassportFactory(DjangoModelFactory):
    """Factory to create LTI passport."""

    class Meta:
        model = models.LTIPassport
        django_get_or_create = (
            "title",
            "consumer",
        )

    title = factory.Sequence(lambda n: f"passport {n}")

    consumer = factory.SubFactory(LTIConsumerFactory)
