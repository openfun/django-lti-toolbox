"""
sandbox URLs
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from views import LaunchURLWithAuth, SimpleLaunchURLVerification, demo_consumer

urlpatterns = [
    # / Redirects to the demo consumer
    url(
        r"^$", RedirectView.as_view(url=reverse_lazy("demo_consumer"), permanent=False),
    ),
    # Demo LTI consumer
    url(r"^consumer$", demo_consumer, name="demo_consumer"),
    # Simple LTI launch request verification
    path(
        "lti/launch-verification",
        SimpleLaunchURLVerification.as_view(),
        name="lti.launch-url-verification",
    ),
    # LTI launch request handler with authentication
    path("lti/launch-auth", LaunchURLWithAuth.as_view(), name="lti.launch-url-auth",),
    # Dynamic LTI launch request handler with authentication and a custom parameter (uuid)
    path(
        "lti/launch/<uuid:uuid>",
        LaunchURLWithAuth.as_view(),
        name="lti.launch-url-auth-with-params",
    ),
    # Django admin
    path("admin/", admin.site.urls),
]
