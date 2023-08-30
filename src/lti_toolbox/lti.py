"""LTI module that supports LTI 1.0.
"""
import re
from typing import Any, Optional

from oauthlib.oauth1 import SignatureOnlyEndpoint

from .exceptions import LTIException, LTIRequestNotVerifiedException, ParamException
from .launch_params import LaunchParams, LTIMessageType, ParamsMixins, SelectionParams
from .models import LTIConsumer, LTIPassport
from .validator import LTIRequestValidator


class LTI:
    """The LTI object abstracts an LTI request.

    It provides properties and methods to inspect a launch or selection request.
    """

    def __init__(self, request):
        """Initialize the LTI system.

        Args:
            request (HttpRequest) The request that holds the LTI parameters
        """

        self.request = request
        self._valid = None
        self._params = {}
        self._verified = False

    def _process_params(self) -> ParamsMixins:
        """Process LTI parameters based on request type."""
        is_selection_request = (
            self.request.POST.get("lti_message_type")
            == LTIMessageType.SELECTION_REQUEST.value
        )
        try:
            params = (
                SelectionParams(self.request.POST)
                if is_selection_request
                else LaunchParams(self.request.POST)
            )
        except ParamException as error:
            raise LTIException(f"Exception while processing parameters: {error}")

        return params

    def verify(self) -> bool:
        """Verify the LTI request.

        Returns:
            bool: True if the LTI request is valid.

        Raises:
            LTIException: Raised if request validation fails
        """
        params = self._process_params()
        validator = LTIRequestValidator()
        oauth_endpoint = SignatureOnlyEndpoint(validator)

        self._valid, _ = oauth_endpoint.validate_request(
            uri=self.request.build_absolute_uri(),
            http_method=self.request.method,
            body=params.urlencoded,
            headers=self.request.headers,
        )

        if self._valid is not True:
            raise LTIException("LTI verification failed")

        self._params = params
        self._verified = True

        return self._valid

    @property
    def is_valid(self) -> bool:
        """Check if the LTI request is verified and valid

        Returns:
            True if the request is verified and valid
        """
        return self._verified and self._valid

    def get_param(self, name: str, default: Any = None):
        """Retrieve an LTI parameter value given its name.

        Args:
            name: Name of the LTI parameter
            default: Default value if the parameter is not found

        Returns:
            The value of the LTI parameter if it exists, or the default value otherwise.

        """
        if not self._verified:
            raise LTIRequestNotVerifiedException()
        return self._params.get(name, default)

    def get_consumer(self) -> LTIConsumer:
        """Retrieve the LTI consumer that initiated the request."""
        consumer_key = self.get_param("oauth_consumer_key")
        passport = LTIPassport.objects.get(
            oauth_consumer_key=consumer_key, is_enabled=True
        )
        return passport.consumer

    def get_course_info(self) -> dict:
        """Retrieve course info in the LTI request.

        Returns:
            dict: A dictionnary containing course informations
                school_name: the school name
                course_name: the course name
                course_section: the course section

        """
        if self.is_edx_format:
            groups = re.match(r"^course-v[0-9]:(.*)", self.get_param("context_id"))
            if groups is not None:
                part = groups.group(1).split("+")
                length = len(part)
                return {
                    "school_name": part[0] if length >= 1 else None,
                    "course_name": part[1] if length >= 2 else None,
                    "course_run": part[2] if length >= 3 else None,
                }

        return {
            "school_name": self.get_param("tool_consumer_instance_name", None),
            "course_name": self.get_param("context_title"),
            "course_run": None,
        }

    @property
    def resource_link_title(self) -> Optional[str]:
        """Return the resource link id as default for its title."""
        return self.get_param("resource_link_title", self.get_param("resource_link_id"))

    @property
    def context_title(self) -> Optional[str]:
        """Return the context id as default for its title."""
        return self.get_param("context_title", self.get_param("context_id"))

    @property
    def roles(self):
        """LTI roles of the authenticated user.

        Returns:
            List[str]: normalized LTI roles from the session
        """
        roles = self.get_param("roles", [])
        return list(map(str.lower, roles))

    @property
    def is_edx_format(self):
        """Check if the LTI request comes from Open edX.

        Returns:
            boolean: True if the LTI request is sent by Open edX

        """
        return re.search(r"^course-v[0-9]:.*$", self.get_param("context_id"))
