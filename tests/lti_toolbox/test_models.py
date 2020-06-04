"""Test the lti_toolbox models"""

from django.test import TestCase

from lti_toolbox.factories import LTIConsumerFactory
from lti_toolbox.models import LTIPassport


class LTIPassportTestCase(TestCase):
    """Test the LTIPassport class."""

    def test_generate_consumer_key(self):
        """Basic testing of entropy in the consumer key generator."""
        generated_keys = set()
        # basic testing for entropy
        for _ in range(1, 100):
            consumer_key = LTIPassport.generate_consumer_key()
            self.assertFalse(consumer_key in generated_keys)
            self.assertGreaterEqual(len(consumer_key), 20)
            generated_keys.add(consumer_key)

    def test_generate_secret(self):
        """Basic testing of entropy in the shared secret generator."""
        generated_secret = set()
        for _ in range(1, 100):
            secret = LTIPassport.generate_shared_secret()
            self.assertFalse(secret in generated_secret)
            self.assertGreaterEqual(len(secret), 40)
            generated_secret.add(secret)

    def test_generate_keys_on_save(self):
        """Ensure that a shared secret and a consumer key are generated on save() if not defined"""
        consumer = LTIConsumerFactory(slug="test_generate_keys_on_save")
        passport = LTIPassport(title="test_generate_keys_on_save_p1", consumer=consumer)
        self.assertEqual("", passport.shared_secret)
        self.assertEqual("", passport.oauth_consumer_key)
        passport.save()
        self.assertNotEqual("", passport.shared_secret)
        self.assertGreaterEqual(len(passport.oauth_consumer_key), 20)
        self.assertGreaterEqual(len(passport.shared_secret), 40)
        self.assertNotEqual("", passport.oauth_consumer_key)

        passport2 = LTIPassport(
            title="test_generate_keys_on_save_p2",
            consumer=consumer,
            oauth_consumer_key="custom_consumer_key",
        )
        self.assertEqual("", passport2.shared_secret)
        passport2.save()
        self.assertNotEqual("", passport2.shared_secret)
        self.assertEqual("custom_consumer_key", passport2.oauth_consumer_key)
        self.assertGreaterEqual(len(passport.shared_secret), 40)

        passport3 = LTIPassport(
            title="test_generate_keys_on_save_p3",
            consumer=consumer,
            shared_secret="custom_secret",
        )
        self.assertEqual("", passport3.oauth_consumer_key)
        passport3.save()
        self.assertNotEqual("", passport3.oauth_consumer_key)
        self.assertEqual("custom_secret", passport3.shared_secret)
        self.assertGreaterEqual(len(passport.oauth_consumer_key), 20)

        passport4 = LTIPassport(
            title="test_generate_keys_on_save_p4",
            consumer=consumer,
            oauth_consumer_key="consumer_key",
            shared_secret="custom_secret",
        )
        passport4.save()
        self.assertEqual("consumer_key", passport4.oauth_consumer_key)
        self.assertEqual("custom_secret", passport4.shared_secret)
