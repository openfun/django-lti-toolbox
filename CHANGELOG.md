# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic 
Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Accept Content-Item selection request used in a deep linking context

### Fixed

- Use modern python method decorator for all LTI view classes

## [1.0.1] - 2022-02-03

### Fixed

- Replace url method by re_path for django 4.0 compatibility

## [1.0.0] - 2021-01-13

### Added

- Add an url field to the LTIConsumer model

## [1.0.0b1] - 2020-06-11

### Added

- Import `lti_toolbox` library and tests from
  [Ashley](https://github.com/openfun/ashley)

[Unreleased]: https://github.com/openfun/django-lti-toolbox/compare/v1.0.1...master
[1.0.1]: https://github.com/openfun/django-lti-toolbox/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/openfun/django-lti-toolbox/compare/v1.0.0b1...v1.0.0
[1.0.0b1]: https://github.com/openfun/django-lti-toolbox/compare/814377082b89abd6c7e47022462aefee2399e53d...v1.0.0b1
