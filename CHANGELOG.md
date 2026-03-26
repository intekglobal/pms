# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## V0.3.0 - 2026-03-27

- Deployment:
  - Enable VPN connection on `dev`: this will be dynamically configured through environment variables.
- Project:
  - Add `CHANGELOG.md` file.

## V0.2.3 - 2026-03-26

- Fixes:
  - NexHealthSDK:
    - Remove (as requested) existing-patient validation&mdash;instead of fixing it&mdash;used in `create_patient` to fix error impeding creating patients with same phone number and same date of birth &mdash; which is completely valid.

## V0.2.2 - 2026-03-26

- Fixes:
  - PMS:
    - Update `Patient` class's `provider_id` definition to accept `None`, as this can happen with patients created through the PMS/HRS.

## V0.2.1 - 2026-03-26

- Fixes:
  - NexHealthSDK:
    - Convert `date_of_birth` to a string in `create_patient` when generating `NexHealth`'s `/patients` *POST* call payload, otherwise it will error due to not being able to generate the JSON payload.

## V0.2.0 - 2026-03-26

- Features:
  - Recalls:
    - Introduce the new `/recalls` endpoint
    - Create submodule `routers/recalls`.
    - Add endpoint `/recalls/patients-with-procedures`
- Miscellaneous:
  - Create new miscellaneous utility function `calculate_age`.
- NexHealthSDK:
  - Create method `get_provider` used to interact with `NexHealth`'s `/providers/{id}` *GET* endpoint and used by the new PMS *GET* endpoint `/provider/{id}`.
- PMS:
  - Add *GET* endpoint `/provider/{id}`.
  - Update `Patient` class to include `appointments` data, which if provided, it is a list of `BaseAppointment` instances.
- Project:
  - Update date-string variables to `date` or `datetime` as necessary, for better validation and handling of arguments/parameters.
  - Add new `dependencies` module.
  - Add new submodules `pms_utilities` and `recalls_classes`.
  - Create subpackages `classes`, `lib`, `lib/utilities` and `routers`.
- Types:
  - Add new `NexHealth` types `NexHealthProviderIncludeQueryType` and `NexHealthProviderIncludeQueryValueType` used in the implementation of the new PMS *GET* endpoint `/provider/{id}`.

## V0.1.0 - 2026-03-18

- Features:
  - Deployment:
    - Add `GitHub` workflow configuration files: `build-and-push.yml`, `deploy.yml`, `dev-server.yml`, `qa-server.yml`.
  - Containerization:
    - Add `Dockerfile` and `docker-compose.yml` files.
- Project:
  - Add initial `pyproject.toml` file which is required for the new deployment functionality.

## *No version* - 2026-03-17

- Features:
  - PMS:
    - Create all the necessary PMS endpoints: `/get_patients`, `/create_patient`, `/get_appointments`, and so on.
    - Create `NexHealthSDK` to handle requests to `NexHealth`.
- Project:
  - Initialize the `Fast API` application that is going to be core functionality of the project.
  - Create the initial utilities: `miscellaneous_utilities`, `nexhealth_utilities` and `requests_utilities`.
  - Create the initial class files: `ehr_abs_class`, `nexhealth`, `nexhealth_sdk`, `pms`, `requests`.
  - Create the initial type definition files: `miscellaneous_types` and `nexhealth_types`.
  - Define and configure the `settings` file/module.
  - Add project-expected files: `.gitignore`, `README.md`, `requirements.txt`.
