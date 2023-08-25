"""Test the LTI Launch parameters validator."""

from django.test import RequestFactory, TestCase

from lti_toolbox.exceptions import InvalidParamException, MissingParamException
from lti_toolbox.factories import LTIConsumerFactory, LTIPassportFactory
from lti_toolbox.launch_params import LaunchParams, SelectionParams

from .utils import sign_parameters


class LaunchParamTestCase(TestCase):
    """Test the LaunchParam class"""

    def setUp(self):
        """Override the setUp method to instanciate and serve a request factory."""
        super().setUp()
        self.request_factory = RequestFactory()

    @staticmethod
    def _launch_params(lti_parameters):
        consumer = LTIConsumerFactory(slug="test_launch_params")
        passport = LTIPassportFactory(title="test passport", consumer=consumer)
        url = "http://testserver/lti/launch"
        signed_parameters = sign_parameters(passport, lti_parameters, url)
        return LaunchParams(signed_parameters)

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

        with self.assertRaises(MissingParamException):
            self._launch_params(
                {
                    "lti_message_type": "basic-lti-launch-request",
                    "resource_link_id": "df7",
                }
            )

        with self.assertRaises(MissingParamException):
            self._launch_params(
                {
                    "lti_message_type": "basic-lti-launch-request",
                    "lti_version": "LTI-1p0",
                }
            )

        with self.assertRaises(MissingParamException):
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
        with self.assertRaises(InvalidParamException):
            LaunchParams(
                {
                    "lti_message_type": "basic-lti-launch-request",
                    "lti_version": "LTI-1p0",
                    "resource_link_id": "df7",
                    "invalid_param": "foo",
                }
            )



class SelectionParamTestCase(TestCase):
    """Test the SelectionParam class"""

    def setUp(self):
        """Override the setUp method to instantiate and serve a request factory."""
        super().setUp()
        self.request_factory = RequestFactory()

    @staticmethod
    def _selection_params(lti_parameters):
        consumer = LTIConsumerFactory(slug="test_launch_params")
        passport = LTIPassportFactory(title="test passport", consumer=consumer)
        url = "http://testserver/lti/launch"
        signed_parameters = sign_parameters(passport, lti_parameters, url)
        return SelectionParams(signed_parameters)
    
    def test_only_required_parameters(self):
        """Test validation of a minimalistic LTI Content-Item
        Selection request with only required parameters.
        """

        self._selection_params(
            {
                "lti_message_type": "ContentItemSelectionRequest",
                "lti_version": "LTI-1p0",
                "accept_media_types": "application/vnd.ims.lti.v1.ltilink",
                "accept_presentation_document_targets": "frame,iframe,window",
                "content_item_return_url": "http://testserver/",
            }
        )

    def test_missing_parameters(self):
        """Test missing required parameters."""

        with self.assertRaises(MissingParamException):
            self._selection_params(
                {
                    "lti_message_type": "ContentItemSelectionRequest",
                    "lti_version": "LTI-1p0",
                    "accept_media_types": "application/vnd.ims.lti.v1.ltilink",
                    "accept_presentation_document_targets": "frame,iframe,window",
                }
            )

        with self.assertRaises(MissingParamException):
            self._selection_params(
                {
                    "lti_version": "LTI-1p0",
                    "accept_media_types": "application/vnd.ims.lti.v1.ltilink",
                    "accept_presentation_document_targets": "frame,iframe,window",
                    "content_item_return_url": "http://test/",
                }
            )

        with self.assertRaises(MissingParamException):
            self._selection_params(
                {
                    "lti_message_type": "ContentItemSelectionRequest",
                    "accept_media_types": "application/vnd.ims.lti.v1.ltilink",
                    "accept_presentation_document_targets": "frame,iframe,window",
                    "content_item_return_url": "http://test/",
                }
            )

    def test_standard_request(self):
        """Test standard LTI Content-Item Selection request."""

        self._selection_params(
            {
                "oauth_version": "1.0",
                "oauth_nonce": "fac452792511fd88c173f2208c1ad3c9",
                "oauth_timestamp": "1649681644",
                "oauth_consumer_key": "A9H5YBAYNERTBIBVEQS4",
                "user_id": "2",
                "lis_person_sourcedid": "",
                "roles": "Instructor",
                "context_id": "2",
                "context_label": "My first course",
                "context_title": "My first course",
                "context_type": "CourseSection",
                "lis_course_section_sourcedid": "",
                "lis_person_name_given": "Admin",
                "lis_person_name_family": "User",
                "lis_person_name_full": "Admin User",
                "ext_user_username": "admin",
                "lis_person_contact_email_primary": "demo@moodle.a",
                "launch_presentation_locale": "en",
                "ext_lms": "moodle-2",
                "tool_consumer_info_product_family_code": "moodle",
                "tool_consumer_info_version": "2021051706",
                "oauth_callback": "about:blank",
                "lti_version": "LTI-1p0",
                "lti_message_type": "ContentItemSelectionRequest",
                "tool_consumer_instance_guid": "1f60aaf6991f55818465e52f3d2879b7",
                "tool_consumer_instance_name": "Sandbox",
                "tool_consumer_instance_description": "Moodle sandbox demo",
                "accept_media_types": "application/vnd.ims.lti.v1.ltilink",
                "accept_presentation_document_targets": "frame,iframe,window",
                "accept_copy_advice": "false",
                "accept_multiple": "true",
                "accept_unsigned": "false",
                "auto_create": "false",
                "can_confirm": "false",
                "content_item_return_url": "https://woop.com",
                "title": (
                    "Marsha LTI provider (never empty : fallback to moodle external tool name)"
                ),
                "text": "(current activity description if exists)",
                "oauth_signature_method": "HMAC-SHA1",
                "oauth_signature": "GEetrp41W4gCH5m1Fe6RPhf55W4=",
            }
        )

    def test_urlencoded(self):
        """Test urlencoded representation of an LTI launch request."""

        selection_params = SelectionParams(
            {
                "lti_message_type": "ContentItemSelectionRequest",
                "lti_version": "LTI-1p0",
                "accept_media_types": "application/vnd.ims.lti.v1.ltilink",
                "accept_presentation_document_targets": "frame,iframe,window",
                "content_item_return_url": "http://testserver/",
            }
        )
        expected = (
            "lti_message_type=ContentItemSelectionRequest"
            "&lti_version=LTI-1p0"
            "&accept_media_types=application%2Fvnd.ims.lti.v1.ltilink"
            "&accept_presentation_document_targets=frame%2Ciframe%2Cwindow"
            "&content_item_return_url=http%3A%2F%2Ftestserver%2F"
        )
        self.assertEqual(expected, selection_params.urlencoded)

    def test_invalid_parameter(self):
        """Test behavior with invalid parameter in LTI launch request."""
        with self.assertRaises(InvalidParamException):
            SelectionParams(
                {
                    "lti_message_type": "ContentItemSelectionRequest",
                    "lti_version": "LTI-1p0",
                    "accept_media_types": "application/vnd.ims.lti.v1.ltilink",
                    "accept_presentation_document_targets": "frame,iframe,window",
                    "content_item_return_url": "http://testserver/",
                    "invalid_param": "foo",
                }
            )
