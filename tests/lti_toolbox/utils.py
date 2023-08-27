"""This module contains helpers for testing purpose"""

from urllib.parse import unquote

from oauthlib import oauth1

CONTENT_TYPE = "application/x-www-form-urlencoded"


def sign_parameters(passport, lti_parameters, url):
    """

    Args:
        passport: The LTIPassport to use to sign the oauth request
        lti_parameters: A dictionary of parameters to sign
        url: The LTI launch URL

    Returns:
        dict: The signed parameters
    """

    signed_parameters = lti_parameters.copy()
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
        headers={"Content-Type": CONTENT_TYPE},
    )

    # Parse headers to pass to template as part of context:
    oauth_dict = dict(
        param.strip().replace('"', "").split("=")
        for param in headers["Authorization"].split(",")
    )

    signature = oauth_dict["oauth_signature"]
    oauth_dict["oauth_signature"] = unquote(signature)
    oauth_dict["oauth_nonce"] = oauth_dict.pop("OAuth oauth_nonce")
    signed_parameters.update(oauth_dict)
    return signed_parameters
