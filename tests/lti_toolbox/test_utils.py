"""Test the utils functions."""

from unittest import mock

from django.test import TestCase

from lti_toolbox.factories import LTIConsumerFactory
from lti_toolbox.models import LTIPassport
from lti_toolbox.utils import sign_parameters


class SignParametersTestCase(TestCase):
    """Test the sign_parameters utils function"""

    @mock.patch(
        "oauthlib.oauth1.rfc5849.generate_nonce",
        return_value="59474787080480293391616018589",
    )
    @mock.patch("oauthlib.oauth1.rfc5849.generate_timestamp", return_value="1616018589")
    def test_sign_parameters(self, mock_timestamp, mock_nonce):
        """Test the oauth 1.0 signature."""

        consumer = LTIConsumerFactory(
            slug="test_lti", title="test consumer", url="http://testserver.com"
        )

        mocked_passport = LTIPassport(
            title="test_generate_keys_on_save_p2",
            consumer=consumer,
            oauth_consumer_key="custom_consumer_key",
            shared_secret="random_shared_secret",  # noqa: S106
        )
        mocked_passport.save()

        parameters = {"test": "your_value"}

        signed_parameters = sign_parameters(
            mocked_passport, parameters, "http://testserver.com/"
        )

        self.assertEqual(
            mock_timestamp.return_value, signed_parameters.get("oauth_timestamp")
        )
        self.assertEqual(mock_nonce.return_value, signed_parameters.get("oauth_nonce"))
        self.assertEqual(
            "jyv1bLSHm94AFbT4plaehDnDMHE=", signed_parameters.get("oauth_signature")
        )
        self.assertEqual("your_value", signed_parameters.get("test"))

        oauth_keys = {
            "oauth_consumer_key",
            "oauth_signature",
            "oauth_timestamp",
            "oauth_version",
            "oauth_signature_method",
            "oauth_nonce",
        }
        self.assertTrue(all(k in signed_parameters for k in oauth_keys))
        self.assertTrue(all(k in signed_parameters for k in parameters))
