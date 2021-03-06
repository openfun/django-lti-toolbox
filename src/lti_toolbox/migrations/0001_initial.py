# Generated by Django 2.2.10 on 2020-02-26 18:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LTIConsumer",
            fields=[
                (
                    "slug",
                    models.SlugField(
                        help_text="identifier for the consumer site",
                        primary_key=True,
                        serialize=False,
                        verbose_name="consumer site identifier",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="human readable title, to describe the LTI consumer",
                        max_length=255,
                        verbose_name="Title",
                    ),
                ),
            ],
            options={
                "verbose_name": "LTI consumer",
                "verbose_name_plural": "LTI consumers",
                "db_table": "lti_consumer",
            },
        ),
        migrations.CreateModel(
            name="LTIPassport",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="human readable title, to describe this LTI passport (i.e. : who will use it ?)",
                        max_length=255,
                        verbose_name="Title",
                    ),
                ),
                (
                    "oauth_consumer_key",
                    models.CharField(
                        editable=False,
                        help_text="oauth consumer key to authenticate an LTI consumer on the LTI provider",
                        max_length=255,
                        unique=True,
                        verbose_name="oauth consumer key",
                    ),
                ),
                (
                    "shared_secret",
                    models.CharField(
                        editable=False,
                        help_text="LTI Shared secret",
                        max_length=255,
                        verbose_name="shared secret",
                    ),
                ),
                (
                    "is_enabled",
                    models.BooleanField(
                        default=True,
                        help_text="whether the passport is enabled",
                        verbose_name="is enabled",
                    ),
                ),
                (
                    "consumer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="lti_toolbox.LTIConsumer",
                    ),
                ),
            ],
            options={
                "verbose_name": "LTI passport",
                "verbose_name_plural": "LTI passports",
                "db_table": "lti_passport",
            },
        ),
    ]
