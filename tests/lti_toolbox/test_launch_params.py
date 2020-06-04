"""Test the LTI Launch parameters validator."""

from django.test import RequestFactory, TestCase

from lti_toolbox.exceptions import (
    InvalidLaunchParamException,
    MissingLaunchParamException,
)
from lti_toolbox.factories import LTIConsumerFactory, LTIPassportFactory
from lti_toolbox.launch_params import LaunchParams

from .utils import sign_parameters


class LaunchParamTestCase(TestCase):
    """Test the LaunchParam class"""

    def setUp(self):
        """Override the setUp method to instanciate and serve a request factory."""
        super().setUp()
        self.request_factory = RequestFactory()

    def test_only_required_parameters(self):
        """Test validation of a minimalistic LTI launch request with only required parameters."""

        self._launch_params(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
            }
        )

    def test_missing_parameters(self):
        """Test missing required parameters."""

        with self.assertRaises(MissingLaunchParamException):
            self._launch_params(
                {
                    "lti_message_type": "basic-lti-launch-request",
                    "resource_link_id": "df7",
                }
            )

        with self.assertRaises(MissingLaunchParamException):
            self._launch_params(
                {
                    "lti_message_type": "basic-lti-launch-request",
                    "resource_link_id": "df7",
                }
            )

        with self.assertRaises(MissingLaunchParamException):
            self._launch_params({"lti_version": "LTI-1p0", "resource_link_id": "df7"})

    def test_standard_request(self):
        """Test standard LTI launch request."""

        self._launch_params(
            {
                "resource_link_id": "test-lms-3d09baddc21a365b7da5ae4d0aa5cb95",
                "lis_person_contact_email_primary": "jean-michel.test@example.com",
                "user_id": "cc09206e612fbdd5636f845dbf9676b3",
                "roles": "Instructor",
                "lis_result_sourcedid": "course-v1%3Atest%2B41018%2Bsession01:test-lms"
                "-3d09baddc21a365b7da5ae4d0aa5cb95:cc09206e612fbdd5636f845dbf9676b3",
                "context_id": "course-v1:test+41018+session01",
                "lti_version": "LTI-1p0",
                "launch_presentation_return_url": "",
                "lis_person_sourcedid": "jeanmich-t",
                "lti_message_type": "basic-lti-launch-request",
            }
        )

    def test_custom_parameters(self):
        """Test LTI launch request with additional custom launch parameters."""

        self._launch_params(
            {
                "resource_link_id": "test-lms-3d09baddc21a365b7da5ae4d0aa5cb95",
                "lis_person_contact_email_primary": "jean-michel.test@example.com",
                "user_id": "cc09206e612fbdd5636f845dbf9676b3",
                "roles": "Instructor",
                "lis_result_sourcedid": "course-v1%3Atest%2B41018%2Bsession01:test-lms"
                "-3d09baddc21a365b7da5ae4d0aa5cb95:cc09206e612fbdd5636f845dbf9676b3",
                "context_id": "course-v1:test+41018+session01",
                "lti_version": "LTI-1p0",
                "launch_presentation_return_url": "",
                "lis_person_sourcedid": "jeanmich-t",
                "lti_message_type": "basic-lti-launch-request",
                "custom_cohort_name": "cohort1",
                "custom_cohort_id": "ee4173aab07ea655999339f8d4fde0a2",
            }
        )

    def test_urlencoded(self):
        """Test urlencoded representation of a LTI launch request."""

        launch_params = LaunchParams(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
            }
        )
        expected = (
            "lti_message_type=basic-lti-launch-request"
            "&lti_version=LTI-1p0"
            "&resource_link_id=df7"
        )
        self.assertEqual(expected, launch_params.urlencoded)

    def test_invalid_parameter(self):
        """Test behavior with invalid parameter in LTI launch request."""
        with self.assertRaises(InvalidLaunchParamException):
            LaunchParams(
                {
                    "lti_message_type": "basic-lti-launch-request",
                    "lti_version": "LTI-1p0",
                    "resource_link_id": "df7",
                    "invalid_param": "foo",
                }
            )

    @staticmethod
    def _launch_params(lti_parameters):
        consumer = LTIConsumerFactory(slug="test_launch_params")
        passport = LTIPassportFactory(title="test passport", consumer=consumer)
        url = "http://testserver/lti/launch"
        signed_parameters = sign_parameters(passport, lti_parameters, url)
        return LaunchParams(signed_parameters)
