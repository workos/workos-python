# Changelog

## [6.0.7](https://github.com/workos/workos-python/compare/v6.0.6...v6.0.7) (2026-04-23)


### Bug Fixes

* export missing types and update event tests ([#631](https://github.com/workos/workos-python/issues/631)) ([0bd6cf8](https://github.com/workos/workos-python/commit/0bd6cf87b69bc95d4a3fd1fabba4cf94f59baf15))

## [6.0.6](https://github.com/workos/workos-python/compare/v6.0.5...v6.0.6) (2026-04-22)


### Bug Fixes

* restore typed `EventSchema` discriminated union dispatcher ([#629](https://github.com/workos/workos-python/issues/629)) ([af95901](https://github.com/workos/workos-python/commit/af95901ed8e607622795a19b15c4a7bf88eca4f7))

## [6.0.5](https://github.com/workos/workos-python/compare/v6.0.4...v6.0.5) (2026-04-20)


### Bug Fixes

* do not JSON parse arbitrary bodies ([#627](https://github.com/workos/workos-python/issues/627)) ([1a8ef00](https://github.com/workos/workos-python/commit/1a8ef00c3b56ecd155853f107a4307ada7caab52))
* restore typing to events ([bbff53f](https://github.com/workos/workos-python/commit/bbff53f3be5af897d6ae917e7a1a8e256d5643e4))

## [6.0.4](https://github.com/workos/workos-python/compare/v6.0.3...v6.0.4) (2026-04-16)


### Bug Fixes

* add documentation on sealing sessions ([#625](https://github.com/workos/workos-python/issues/625)) ([5ae90d0](https://github.com/workos/workos-python/commit/5ae90d024a0a5532c8bb54a21a4190a3de564bea))
* Remove extractVersion from matchUpdateTypes rules ([#623](https://github.com/workos/workos-python/issues/623)) ([09a2e5d](https://github.com/workos/workos-python/commit/09a2e5d1e7666eb6b435c49ed3ba1e63d8ae274e))

## [6.0.3](https://github.com/workos/workos-python/compare/v6.0.2...v6.0.3) (2026-04-15)


### Bug Fixes

* forward Radar context from authenticate_with_code_pkce ([#620](https://github.com/workos/workos-python/issues/620)) ([32aea77](https://github.com/workos/workos-python/commit/32aea77883b80da00829e9c200586eaeb371daf3))

## [6.0.2](https://github.com/workos/workos-python/compare/v6.0.1...v6.0.2) (2026-04-14)


### Bug Fixes

* slight rename ([2b2e9e2](https://github.com/workos/workos-python/commit/2b2e9e26ec6615a3dd8bc4a6c2fc86dadbb4cbb0))

## [6.0.1](https://github.com/workos/workos-python/compare/v6.0.0...v6.0.1) (2026-04-13)


### Bug Fixes

* one more regen ([187f83f](https://github.com/workos/workos-python/commit/187f83fa9efce38b8665e9e25d7c214787dba204))
* regenerate methods to include missing params ([#610](https://github.com/workos/workos-python/issues/610)) ([6792792](https://github.com/workos/workos-python/commit/6792792cc5ad51df50fadd0248b797ffe74ab095))

## [6.0.0](https://github.com/workos/workos-python/compare/v5.46.0...v6.0.0) (2026-04-13)


### Top-level notices

- v6 is a breaking release and now requires Python 3.10 or newer.
- The SDK now uses generated sync and async clients with top-level imports from `workos`.
- `client.portal` has been renamed to `client.admin_portal`, and `client.fga` is not available in v6.

### What's changed

- Rebuilt the Python SDK around a generated client/runtime with updated request handling, pagination, typed models, and error surfaces.
- Reorganized package exports and service modules to support the new v6 client shape across the SDK.
- Added release validation coverage, including package smoke tests and the runtime dependency updates needed for packaged installs.

See the [V6 migration guide]([docs/V6_MIGRATION_GUIDE.md](https://github.com/workos/workos-python/blob/main/docs/V6_MIGRATION_GUIDE.md)) before upgrading from v5.

## [5.46.0](https://github.com/workos/workos-python/compare/v5.45.0...v5.46.0) (2026-03-16)


### Features

* make vault events available in SDK ([#588](https://github.com/workos/workos-python/issues/588)) ([75322fb](https://github.com/workos/workos-python/commit/75322fb2863ad28b333184348c88fae11031ffdf))


### Bug Fixes

* Allow organization_name to be empty on organization membership events ([#595](https://github.com/workos/workos-python/issues/595)) ([865aeb5](https://github.com/workos/workos-python/commit/865aeb514daf701c7d899963e0d247d48b565b4e))
* **deps:** update dependency pyjwt to v2.12.0 [security] ([#589](https://github.com/workos/workos-python/issues/589)) ([0d50534](https://github.com/workos/workos-python/commit/0d5053403ea2c56203793becaab43fc50d66db43))

## [5.45.0](https://github.com/workos/workos-python/compare/v5.44.0...v5.45.0) (2026-03-09)


### Features

* return organization_name on OrganizationMembership ([#574](https://github.com/workos/workos-python/issues/574)) ([dae4dab](https://github.com/workos/workos-python/commit/dae4daba638660be13b6fd8bcaff03ce63ed6f00))


### Bug Fixes

* list_client_secrets returns raw list, not paginated response ([#586](https://github.com/workos/workos-python/issues/586)) ([ccc8cd5](https://github.com/workos/workos-python/commit/ccc8cd5f82802cdd275d8fab06390747b33544cd))

## [5.44.0](https://github.com/workos/workos-python/compare/v5.43.0...v5.44.0) (2026-03-06)


### Features

* Add Connect Applications and Client Secrets module ([#585](https://github.com/workos/workos-python/issues/585)) ([1ad1623](https://github.com/workos/workos-python/commit/1ad16239d88f46bb76e7b1bce9afc1eb01791958))
* add cross app auth method ([#577](https://github.com/workos/workos-python/issues/577)) ([c67972f](https://github.com/workos/workos-python/commit/c67972f662666b08e350d2314912d746043c2ad2))
* add resource_type_slug to permissions, environment and organization roles ([#576](https://github.com/workos/workos-python/issues/576)) ([1004bd7](https://github.com/workos/workos-python/commit/1004bd7b5591169f8165b3cc59240396992ae325))
* **user-management:** add directory_managed to OrganizationMembership ([#583](https://github.com/workos/workos-python/issues/583)) ([f0e716e](https://github.com/workos/workos-python/commit/f0e716ebf5af235c3556e746b77171bf280489e3))

## [5.43.0](https://github.com/workos/workos-python/compare/v5.42.1...v5.43.0) (2026-03-05)


### Features

* update authorization module for fga ([#581](https://github.com/workos/workos-python/issues/581)) ([aa5f1d8](https://github.com/workos/workos-python/commit/aa5f1d8adf610a565f90ddb9b1fc346c83c4ae29))


### Bug Fixes

* Remove Coana workflow files ([#580](https://github.com/workos/workos-python/issues/580)) ([bb8d2f1](https://github.com/workos/workos-python/commit/bb8d2f1ba3a904383793426114d9ff93297d1658))
* update renovate rules ([#572](https://github.com/workos/workos-python/issues/572)) ([401976b](https://github.com/workos/workos-python/commit/401976b79b0fe130c49435b72eb27de641635795))
