"""Test the LTI interconnection with an LTI consumer."""

from urllib.parse import urlencode

from django.test import RequestFactory, TestCase

from lti_toolbox.exceptions import LTIException, LTIRequestNotVerifiedException
from lti_toolbox.factories import LTIConsumerFactory, LTIPassportFactory
from lti_toolbox.launch_params import LTIRole
from lti_toolbox.lti import LTI
from lti_toolbox.utils import CONTENT_TYPE, sign_parameters


class LTITestCase(TestCase):
    """Test the LTI class"""

    def setUp(self):
        """Override the setUp method to instantiate and serve a request factory."""
        super().setUp()
        self.request_factory = RequestFactory()
        self._consumer = LTIConsumerFactory(slug="test_lti")
        self._passport = LTIPassportFactory(
            title="test passport", consumer=self._consumer
        )
        self._url = "http://testserver/lti/launch"

    def _verified_lti_request(self, lti_parameters):
        signed_parameters = sign_parameters(self._passport, lti_parameters, self._url)
        lti = self._lti_request(signed_parameters, self._url)
        lti.verify()
        return lti

    def _lti_request(self, signed_parameters, url):
        request = self.request_factory.post(
            url,
            data=urlencode(signed_parameters),
            content_type=CONTENT_TYPE,
        )
        return LTI(request)

    def test_verify_signature(self):
        """Test the oauth 1.0 signature verification"""

        lti_parameters = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "df7",
            "context_id": "course-v1:fooschool+mathematics+0042",
            "roles": "Instructor",
        }

        signed_parameters = sign_parameters(self._passport, lti_parameters, self._url)
        lti = self._lti_request(signed_parameters, self._url)
        self.assertFalse(lti.is_valid)
        self.assertTrue(lti.verify())
        self.assertTrue(lti.is_valid)

        # If we alter the signature (e.g. add "a" to it), the verification should fail
        signed_parameters["oauth_signature"] = "{:s}a".format(
            signed_parameters["oauth_signature"]
        )
        lti = self._lti_request(signed_parameters, self._url)
        with self.assertRaises(LTIException):
            self.assertFalse(lti.verify())
        self.assertFalse(lti.is_valid)

    def test_replay_attack(self):
        """Test a replay attack"""

        lti_parameters = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "df7",
            "context_id": "course-v1:fooschool+mathematics+0042",
            "roles": "Instructor",
        }

        signed_parameters = sign_parameters(self._passport, lti_parameters, self._url)
        lti = self._lti_request(signed_parameters, self._url)
        self.assertTrue(lti.verify())

        replayed_lti = self._lti_request(signed_parameters, self._url)
        with self.assertRaises(LTIException):
            self.assertFalse(replayed_lti.verify())

    def test_invalid_param(self):
        """Test the behaviour of LTI verification when an invalid LTI parameter is given"""

        lti_parameters = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "df7",
            "invalid_param": "hello!",
        }
        # Should always raise an LTException on failure
        with self.assertRaises(LTIException):
            self._verified_lti_request(lti_parameters)

    def test_get_param(self):
        """Test the get_param method"""
        lti_parameters = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "df7",
            "custom_param": "custom value",
        }
        signed_parameters = sign_parameters(self._passport, lti_parameters, self._url)
        lti = self._lti_request(signed_parameters, self._url)
        with self.assertRaises(LTIRequestNotVerifiedException):
            lti.get_param("custom_param")

        lti.verify()
        self.assertEqual("custom value", lti.get_param("custom_param"))

        self.assertEqual(
            "default value", lti.get_param("custom_nonexistent_param", "default value")
        )

    def test_get_consumer(self):
        """Test the retrieval of the consumer that initiated the launch request"""
        lti = self._verified_lti_request(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
            }
        )
        self.assertEqual(self._consumer.slug, lti.get_consumer().slug)

    def test_is_edx_format(self):
        """Test the detection of EdX course format"""
        lti_parameters = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "df7",
            "context_id": "course-v1:fooschool+mathematics+0042",
            "roles": "Instructor",
        }
        lti = self._verified_lti_request(lti_parameters)
        self.assertTrue(lti.is_edx_format)

        lti_parameters.update({"context_id": "foo-context"})
        lti = self._verified_lti_request(lti_parameters)
        self.assertFalse(lti.is_edx_format)

    def test_is_moodle_format(self):
        """Test the detection of Moodle course format"""
        lti_parameters = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "df7",
            "context_id": "1542",
            "roles": "Instructor",
            "tool_consumer_info_product_family_code": "moodle",
        }
        lti = self._verified_lti_request(lti_parameters)
        self.assertTrue(lti.is_moodle_format)

        lti_parameters.update({"tool_consumer_info_product_family_code": ""})
        lti = self._verified_lti_request(lti_parameters)
        self.assertFalse(lti.is_moodle_format)

    def test_course_info(self):
        """Test the detection of course information"""

        # EdX request
        lti_parameters = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "df7",
            "context_id": "course-v1:fooschool+mathematics+0042",
            "context_title": "some context",
            "roles": "Instructor",
        }
        lti = self._verified_lti_request(lti_parameters)
        course_info = lti.get_course_info()
        self.assertEqual("fooschool", course_info.get("school_name"))
        self.assertEqual("mathematics", course_info.get("course_name"))
        self.assertEqual("0042", course_info.get("course_run"))

        # Non-EdX request
        lti_parameters.update(
            {"context_id": "foo-context", "tool_consumer_instance_name": "bar-school"}
        )
        lti = self._verified_lti_request(lti_parameters)
        course_info = lti.get_course_info()
        self.assertEqual("bar-school", course_info.get("school_name"))
        self.assertEqual("some context", course_info.get("course_name"))
        self.assertIsNone(course_info.get("course_run"))

    def test_resource_link_title(self):
        """Test the retrieval of the resource_link_title"""

        lti_parameters = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "df7",
            "context_id": "course-v1:fooschool+mathematics+0042",
            "context_title": "some context",
            "roles": "Instructor",
        }
        lti = self._verified_lti_request(lti_parameters)
        # If there is no resource_link_title parameter, it defaults to resource_link_id
        self.assertEqual("df7", lti.resource_link_title)

        lti_parameters.update({"resource_link_title": "some title"})
        lti = self._verified_lti_request(lti_parameters)
        self.assertEqual("some title", lti.resource_link_title)

    def test_roles(self):
        """Test the retrieval of the roles"""
        lti = self._verified_lti_request(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
                "roles": "Instructor",
            }
        )
        self.assertEqual(["instructor"], lti.roles)

        lti = self._verified_lti_request(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
                "roles": "Student,Moderator",
            }
        )
        self.assertEqual(["student", "moderator"], lti.roles)

    def test_has_any_of_roles(self):
        # pylint: disable=protected-access
        """Test _has_any_of_roles property"""
        lti = self._verified_lti_request(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
                "roles": "Instructor",
            }
        )
        self.assertTrue(lti._has_any_of_roles({"instructor"}))
        self.assertTrue(lti._has_any_of_roles({"instructor", LTIRole.TEACHER}))
        self.assertFalse(lti._has_any_of_roles({"Instructor", LTIRole.TEACHER}))
        self.assertTrue(lti._has_any_of_roles({LTIRole.INSTRUCTOR, LTIRole.TEACHER}))

    def test_roles_check(self):
        """Test the roles-check properties"""
        lti = self._verified_lti_request(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
                "roles": "Instructor",
            }
        )
        self.assertTrue(lti.is_instructor)
        self.assertFalse(lti.is_administrator)
        self.assertFalse(lti.is_student)

        lti = self._verified_lti_request(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
                "roles": "Student,Moderator",
            }
        )
        self.assertFalse(lti.is_instructor)
        self.assertFalse(lti.is_administrator)
        self.assertTrue(lti.is_student)

        lti = self._verified_lti_request(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
                "roles": "Administrator,Instructor",
            }
        )
        self.assertTrue(lti.is_instructor)
        self.assertTrue(lti.is_administrator)
        self.assertFalse(lti.is_student)

        lti = self._verified_lti_request(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
                "roles": "WrongRole",
            }
        )
        self.assertFalse(lti.is_instructor)
        self.assertFalse(lti.is_administrator)
        self.assertFalse(lti.is_student)

    def test_can_edit_content(self):
        """Test can_edit_content property"""
        lti = self._verified_lti_request(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
                "roles": "Instructor",
            }
        )
        self.assertTrue(lti.can_edit_content)

        lti = self._verified_lti_request(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
                "roles": "Student,Moderator",
            }
        )
        self.assertFalse(lti.can_edit_content)

        lti = self._verified_lti_request(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
                "roles": "Administrator,Instructor",
            }
        )
        self.assertTrue(lti.can_edit_content)

        lti = self._verified_lti_request(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "df7",
                "roles": "WrongRole",
            }
        )
        self.assertFalse(lti.can_edit_content)

    def test_context_title(self):
        """Test the retrieval of the context_title"""
        lti_parameters = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "df7",
            "context_id": "the context id",
        }
        lti = self._verified_lti_request(lti_parameters)
        # If context_title parameter is not defined, it defaults to the context_id
        self.assertEqual("the context id", lti.context_title)

        lti_parameters.update({"context_title": "the context title"})
        lti = self._verified_lti_request(lti_parameters)
        self.assertEqual("the context title", lti.context_title)

    def test_lti_origin_url_edx(self):
        """Build origin_url for an edx request."""
        lti_parameters = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "df7",
            "context_id": "course-v1:fooschool+mathematics+0042",
            "roles": "Instructor",
        }
        lti = self._verified_lti_request(lti_parameters)

        self.assertEqual(
            lti.origin_url,
            "https://testserver/consumer-20/course/course-v1:fooschool+mathematics+0042",
        )

    def test_lti_origin_url_moodle(self):
        """Build origin_url for an edx request."""
        lti_parameters = {
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "df7",
            "context_id": "123",
            "roles": "Instructor",
            "tool_consumer_info_product_family_code": "moodle",
        }
        lti = self._verified_lti_request(lti_parameters)

        self.assertEqual(
            lti.origin_url, "https://testserver/consumer-21/course/view.php?id=123"
        )
