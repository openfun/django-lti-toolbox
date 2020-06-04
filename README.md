# Django-lti-toolbox, a Django application to build LTI Tool Providers

## Overview

`django-lti-toolbox` is a django application that makes it easier for you to create [LTI](https://en.wikipedia.org/wiki/Learning_Tools_Interoperability) Tool Providers web applications.

This is a set of tools that let you manage LTI requests the way you want.

It is based on top of the great [OAuthLib](https://github.com/oauthlib/oauthlib) library.

## Features

- Verify LTI launch requests
- Base views to build your own LTI launch request handlers
- Sample Django authentication backend
- Manage your LTI consumers from django admin
- Demo project to quickly see it in action

## Try it with our demo project !

- Clone this repository (`git clone https://github.com/openfun/django-lti-toolbox.git`)

- `cd django-lti-toolbox`

- `make bootstrap` to initialize the dev environment

- `make run` to start the services

- Go to [http://localhost:8090/](http://localhost:8090/) and try the demo LTI consumer

- Watch django logs with `make logs`

## Contributing

This project is intended to be community-driven, so please, do not hesitate to
get in touch if you have any question related to our implementation or design
decisions.

We try to raise our code quality standards and expect contributors to follow
the recommandations from our
[handbook](https://openfun.gitbooks.io/handbook/content).

## License

This work is released under the MIT License (see [LICENSE](./LICENSE)).
