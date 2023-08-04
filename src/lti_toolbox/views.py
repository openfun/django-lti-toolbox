"""Views of the lti_toolbox django application."""
from abc import ABC, abstractmethod

from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from lti_toolbox.exceptions import LTIException

from .lti import LTI


@method_decorator(csrf_exempt, name="dispatch")
class BaseLTIView(ABC, View):
    """
    Abstract view for handling views from an LTI Launch request.

    This class verifies the authenticity of the incoming LTI requests.
    Subclasses must implement the _do_on_success() method to define custom
    processing of successful LTI requests.
    """

    def post(self, request, *args, **kwargs) -> HttpResponse:  # pylint: disable=W0613
        """Handler for POST requests."""
        lti_request = LTI(request)
        try:
            lti_request.verify()
            return self._do_on_success(lti_request)
        except LTIException as error:
            return self._do_on_failure(request, error)

    @abstractmethod
    def _do_on_success(self, lti_request: LTI) -> HttpResponse:
        """Process the request when the LTI launch requests is verified."""
        raise NotImplementedError()

    def _do_on_failure(  # pylint: disable=R0201
        self, request: HttpRequest, error: LTIException  # pylint: disable=W0613
    ) -> HttpResponse:
        """
        Default handler for invalid LTI launch requests.
        You are encouraged to define your own handler according to your project needs.
        """
        return HttpResponseForbidden("Invalid LTI launch request")


@method_decorator(csrf_exempt, name="dispatch")
class BaseLTIAuthView(ABC, View):
    """
    Abstract view for handling authenticated views from an LTI Launch request.

    This class verifies the authenticity of the incoming LTI requests,
    and performs user authentication.
    Subclasses must implement the _do_on_login() method to define custom
    processing of authenticated users via LTI.
    """

    def post(self, request, *args, **kwargs) -> HttpResponse:  # pylint: disable=W0613
        """Handler for POST requests."""
        lti_request = LTI(request)
        try:
            lti_request.verify()
            user = authenticate(request, lti_request=lti_request)
            if user is not None:
                login(request, user)
                return self._do_on_login(lti_request)
            return self._do_on_authentication_failure(lti_request)
        except LTIException as error:
            return self._do_on_verification_failure(request, error)

    @abstractmethod
    def _do_on_login(self, lti_request: LTI) -> HttpResponse:
        """Process the request when the user is logged in via LTI"""
        raise NotImplementedError()

    def _do_on_authentication_failure(  # pylint: disable=R0201
        self, lti_request: LTI  # pylint: disable=W0613
    ) -> HttpResponse:
        """
        Default handler for failed authentication.
        You are encouraged to define your own handler according to your project needs.
        """
        return HttpResponseForbidden()

    def _do_on_verification_failure(  # pylint: disable=R0201
        self, request: HttpRequest, error: LTIException  # pylint: disable=W0613
    ) -> HttpResponse:
        """
        Default handler for invalid LTI launch requests.
        You are encouraged to define your own handler according to your project needs.
        """
        return HttpResponseForbidden("Invalid LTI launch request")
