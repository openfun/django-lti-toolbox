"""
sandbox URLs
"""
from django.contrib import admin
from django.urls import path, re_path, reverse_lazy
from django.views.generic import RedirectView

from views import LaunchURLWithAuth, SimpleLaunchURLVerification, demo_consumer

urlpatterns = [
    # / Redirects to the demo consumer
    re_path(
        r"^$", RedirectView.as_view(url=reverse_lazy("demo_consumer"), permanent=False),
    ),
    # Demo LTI consumer
    re_path(r"^consumer$", demo_consumer, name="demo_consumer"),
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
