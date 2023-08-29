"""Views of the lti_toolbox django application."""
import uuid
from urllib.parse import unquote

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from oauthlib import oauth1

from lti_toolbox.exceptions import LTIException
from lti_toolbox.factories import LTIConsumerFactory, LTIPassportFactory
from lti_toolbox.lti import LTI
from lti_toolbox.models import LTIPassport
from lti_toolbox.views import BaseLTIAuthView, BaseLTIView

from forms import LTIConsumerForm


class SimpleLaunchURLVerification(BaseLTIView):
    """Example view to handle LTI launch request verification."""

    def _do_on_success(self, lti_request: LTI, *args, **kwargs) -> HttpResponse:
        # Render a template with some debugging information
        context = {
            "message": "LTI request verified successfully",
        }
        return render(self.request, "demo/debug_infos.html", context)

    def _do_on_failure(self, request: HttpRequest, error: LTIException) -> HttpResponse:
        context = {
            "message": "INVALID LTI request (check your django logs for more details)",
            "message_class": "danger",
        }
        return render(self.request, "demo/debug_infos.html", context, status=403)


class LaunchURLWithAuth(BaseLTIAuthView):
    """
    Example view to handle LTI launch request with user authentication.

    It relies on the `lti_toolbox.backend.LTIBackend` authentication backend that
    has been defined in the `AUTHENTICATION_BACKENDS` setting.
    """

    def _do_on_login(self, lti_request: LTI) -> HttpResponse:
        """Process the request when the user is logged in via LTI"""
        context = {
            "message": "LTI request verified + user authenticated successfully",
            "debug_infos": {
                "View parameters": self.kwargs,
                "Authenticated user": {
                    "id": self.request.user.id,
                    "username": self.request.user.username,
                    "email": self.request.user.email,
                },
            },
        }
        return render(self.request, "demo/debug_infos.html", context)


##################################################################################
# You can ignore the rest of the file since its related to the demo LTI consumer #
##################################################################################


@csrf_exempt
def demo_consumer(request: HttpRequest) -> HttpResponse:
    """Display the demo LTI consumer"""

    # Ensure that at least the demo consumer exists with a passport
    consumer = LTIConsumerFactory(slug="dev_consumer", title="Dev consumer")
    passport = LTIPassportFactory(title="Dev passport", consumer=consumer)

    if request.method == "POST":
        form = LTIConsumerForm(request.POST)
        if form.is_valid():
            launch_url = request.build_absolute_uri(_get_launch_url(form.cleaned_data))
            lti_params = _generate_signed_parameters(form, launch_url, passport)
            return render(
                request,
                "demo/consumer.html",
                {"form": form, "lti_params": lti_params, "launch_url": launch_url},
            )
    else:
        form = LTIConsumerForm()

    return render(request, "demo/consumer.html", {"form": form})


def _generate_signed_parameters(form: LTIConsumerForm, url: str, passport: LTIPassport):

    user_id = form.cleaned_data["user_id"]

    lti_parameters = {
        "lti_message_type": "basic-lti-launch-request",
        "lti_version": "LTI-1p0",
        "resource_link_id": str(uuid.uuid4()),
        "lis_person_contact_email_primary": f"{user_id}@example.com",
        "lis_person_sourcedid": user_id,
        "user_id": form.cleaned_data["user_id"],
        "context_id": form.cleaned_data["context_id"],
        "context_title": form.cleaned_data["course_title"],
        "roles": form.cleaned_data["role"],
    }
    if form.cleaned_data["presentation_locale"]:
        lti_parameters["launch_presentation_locale"] = form.cleaned_data[
            "presentation_locale"
        ]

    oauth_client = oauth1.Client(
        client_key=passport.oauth_consumer_key, client_secret=passport.shared_secret
    )
    # Compute Authorization header which looks like:
    # Authorization: OAuth oauth_nonce="80966668944732164491378916897",
    # oauth_timestamp="1378916897", oauth_version="1.0", oauth_signature_method="HMAC-SHA1",
    # oauth_consumer_key="", oauth_signature="frVp4JuvT1mVXlxktiAUjQ7%2F1cw%3D"
    _uri, headers, _body = oauth_client.sign(
        url,
        http_method="POST",
        body=lti_parameters,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Parse headers to pass to template as part of context:
    oauth_dict = dict(
        param.strip().replace('"', "").split("=")
        for param in headers["Authorization"].split(",")
    )

    signature = oauth_dict["oauth_signature"]
    oauth_dict["oauth_signature"] = unquote(signature)
    oauth_dict["oauth_nonce"] = oauth_dict.pop("OAuth oauth_nonce")
    lti_parameters.update(oauth_dict)
    return lti_parameters


def _get_launch_url(cleaned_data):
    if cleaned_data["action"] == "lti.launch-url-auth-with-params":
        view_kwargs = {
            "uuid": uuid.uuid5(uuid.NAMESPACE_DNS, cleaned_data["context_id"])
        }
    else:
        view_kwargs = {}
    return reverse(cleaned_data["action"], kwargs=view_kwargs)
