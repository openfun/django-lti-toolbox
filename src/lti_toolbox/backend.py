"""This module contains an authentication backend based on LTI launch request."""

import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

from lti_toolbox.lti import LTI

logger = logging.getLogger(__name__)

USER_MODEL = get_user_model()


class LTIBackend(ModelBackend):
    """
    Authentication backend used by the lti_toolbox.views.BaseLTIAuthView
    It authenticates a user from a verified LTI request and creates a User if necessary.

    You are encouraged to make your own authentication backend to add your own domain logic.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user from a LTI request

        Args:
            request: django http request
            username: The (optional) username to authenticate
            password: The (optional) password of the user to authenticate
            kwargs: additional parameters

        Returns:
            An authenticated user or None
        """

        lti_request = kwargs.get("lti_request")
        if not lti_request:
            return None

        if not lti_request.is_valid:
            raise PermissionDenied()

        username = self._get_mandatory_param(lti_request, "user_id")
        email = self._get_mandatory_param(
            lti_request, "lis_person_contact_email_primary"
        )

        logger.debug("User %s authenticated from LTI request", username)

        try:
            user = USER_MODEL.objects.get_by_natural_key(username)
        except USER_MODEL.DoesNotExist:
            user = USER_MODEL.objects.create_user(username, email=email)
            logger.debug("User %s created in database", username)
        if not user.is_active:
            logger.debug("User %s is not active", user.username)
            raise PermissionDenied()
        return user

    @staticmethod
    def _get_mandatory_param(lti_request: LTI, param: str) -> Any:
        """Get a LTI parameter or throw a exception if not defined."

        Args:
            lti_request: The verified LTI request
            param: A LTI parameter name

        Returns: The parameter value

        Raises:
            PermissionDenied if the parameter is not defined
        """
        value = lti_request.get_param(param)
        if not value:
            logger.debug("Unable to find param %s in LTI request", param)
            raise PermissionDenied()
        logger.debug("%s = %s", param, value)
        return value
