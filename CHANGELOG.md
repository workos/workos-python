# Changelog

## [9.0.0](https://github.com/workos/workos-python/compare/v8.1.0...v9.0.0) (2026-06-17)


### ⚠ BREAKING CHANGES

* **organization_membership:** Add new OrganizationMembershipService with membership and group operations ([#662](https://github.com/workos/workos-python/issues/662))
* **vault:** Add new Vault service with encryption and object storage APIs ([#662](https://github.com/workos/workos-python/issues/662))
* **radar:** Remove device_fingerprint and bot_score parameters from assess request ([#662](https://github.com/workos/workos-python/issues/662))
* **authorization:** Remove search parameter and add resource/role filtering ([#662](https://github.com/workos/workos-python/issues/662))
* **api_keys:** Add expires_at field to API key models ([#662](https://github.com/workos/workos-python/issues/662))
* **audit_logs:** Rename audit log models and update service references ([#662](https://github.com/workos/workos-python/issues/662))
* **webhooks:** Rename WebhookEndpointJson to WebhookEndpoint ([#662](https://github.com/workos/workos-python/issues/662))
* **user_management:** Remove organization membership methods, move to new service ([#662](https://github.com/workos/workos-python/issues/662))
* **api_keys:** Restructure API key models for dual ownership
* **common:** Add user API key event models and refactor BYOK key provider
* **authorization:** Refactor role assignment models and add list endpoints
* release new version of Python SDK library ([#599](https://github.com/workos/workos-python/issues/599))

### Features

* add `get_jwks_url` helper to UserManagement ([#644](https://github.com/workos/workos-python/issues/644)) ([53134d3](https://github.com/workos/workos-python/commit/53134d32f168dd0da606672125e8cdd221832761))
* Add ability to accept invitations ([#552](https://github.com/workos/workos-python/issues/552)) ([47b34e9](https://github.com/workos/workos-python/commit/47b34e98846e07dd04daef8d3684055a834c45ce))
* Add Connect Applications and Client Secrets module ([#585](https://github.com/workos/workos-python/issues/585)) ([1ad1623](https://github.com/workos/workos-python/commit/1ad16239d88f46bb76e7b1bce9afc1eb01791958))
* add cross app auth method ([#577](https://github.com/workos/workos-python/issues/577)) ([c67972f](https://github.com/workos/workos-python/commit/c67972f662666b08e350d2314912d746043c2ad2))
* add resource_type_slug to permissions, environment and organization roles ([#576](https://github.com/workos/workos-python/issues/576)) ([1004bd7](https://github.com/workos/workos-python/commit/1004bd7b5591169f8165b3cc59240396992ae325))
* add support for totp_secret ([#273](https://github.com/workos/workos-python/issues/273)) ([2171558](https://github.com/workos/workos-python/commit/2171558a4ce8bb81ca1dca39d45c0e4af96ab9ff))
* **api_keys:** Add create_api_key_expire operation ([#665](https://github.com/workos/workos-python/issues/665)) ([4af7da4](https://github.com/workos/workos-python/commit/4af7da4926835b6bbf8a3bad604fcd32a8627766))
* **api_keys:** Add expires_at field to API key models ([#662](https://github.com/workos/workos-python/issues/662)) ([ab992b5](https://github.com/workos/workos-python/commit/ab992b5a069a129f3ba3ffe0845ccc4b310ef098))
* **api_keys:** Restructure API key models for dual ownership ([8b5e91d](https://github.com/workos/workos-python/commit/8b5e91d7038485ee012ea6f784a1ed27c5fc25cd))
* **audit_logs:** Add SNOWFLAKE to AuditLogConfigurationLogStreamType enum ([#665](https://github.com/workos/workos-python/issues/665)) ([4af7da4](https://github.com/workos/workos-python/commit/4af7da4926835b6bbf8a3bad604fcd32a8627766))
* **audit_logs:** Rename audit log models and update service references ([#662](https://github.com/workos/workos-python/issues/662)) ([ab992b5](https://github.com/workos/workos-python/commit/ab992b5a069a129f3ba3ffe0845ccc4b310ef098))
* **authorization:** Refactor role assignment models and add list endpoints ([8b5e91d](https://github.com/workos/workos-python/commit/8b5e91d7038485ee012ea6f784a1ed27c5fc25cd))
* **authorization:** Remove DOMAIN_SIGN_UP_RATE_LIMIT from RadarStandaloneResponseControl enum ([#665](https://github.com/workos/workos-python/issues/665)) ([4af7da4](https://github.com/workos/workos-python/commit/4af7da4926835b6bbf8a3bad604fcd32a8627766))
* **authorization:** Remove search parameter and add resource/role filtering ([#662](https://github.com/workos/workos-python/issues/662)) ([ab992b5](https://github.com/workos/workos-python/commit/ab992b5a069a129f3ba3ffe0845ccc4b310ef098))
* **common:** Add ApiKeyUpdated event models ([#665](https://github.com/workos/workos-python/issues/665)) ([4af7da4](https://github.com/workos/workos-python/commit/4af7da4926835b6bbf8a3bad604fcd32a8627766))
* **common:** Add new models for pipes events and enhancements ([#662](https://github.com/workos/workos-python/issues/662)) ([ab992b5](https://github.com/workos/workos-python/commit/ab992b5a069a129f3ba3ffe0845ccc4b310ef098))
* **common:** Add user API key event models and refactor BYOK key provider ([8b5e91d](https://github.com/workos/workos-python/commit/8b5e91d7038485ee012ea6f784a1ed27c5fc25cd))
* **common:** Make expires_at required in ApiKeyCreatedData and ApiKeyRevokedData ([#665](https://github.com/workos/workos-python/issues/665)) ([4af7da4](https://github.com/workos/workos-python/commit/4af7da4926835b6bbf8a3bad604fcd32a8627766))
* **common:** Remove DsyncDeactivated models and add DsyncToken events ([#665](https://github.com/workos/workos-python/issues/665)) ([4af7da4](https://github.com/workos/workos-python/commit/4af7da4926835b6bbf8a3bad604fcd32a8627766))
* **connect:** Add name field to UserObject model ([#665](https://github.com/workos/workos-python/issues/665)) ([4af7da4](https://github.com/workos/workos-python/commit/4af7da4926835b6bbf8a3bad604fcd32a8627766))
* **docs:** Publish pdoc-generated API reference to GitHub Pages ([#651](https://github.com/workos/workos-python/issues/651)) ([05831ea](https://github.com/workos/workos-python/commit/05831ea7ce339448cb9f1986b41e5e34bf8442e7))
* **generated:** Add Groups API and Waitlist User events support ([#640](https://github.com/workos/workos-python/issues/640)) ([a10d02b](https://github.com/workos/workos-python/commit/a10d02b1bc88c20cab2b83c006aceae968b86bca))
* **generated:** use explicit re-export form in service __init__.py ([#645](https://github.com/workos/workos-python/issues/645)) ([7ecb2e9](https://github.com/workos/workos-python/commit/7ecb2e9fafa030afdf27061b2b45f9d59fe2e900))
* make vault events available in SDK ([#588](https://github.com/workos/workos-python/issues/588)) ([75322fb](https://github.com/workos/workos-python/commit/75322fb2863ad28b333184348c88fae11031ffdf))
* organization_domain events ([#457](https://github.com/workos/workos-python/issues/457)) ([795eb8f](https://github.com/workos/workos-python/commit/795eb8f311a34a52aa537581da3fcd12346f51b2))
* **organization_membership:** Add new OrganizationMembershipService with membership and group operations ([#662](https://github.com/workos/workos-python/issues/662)) ([ab992b5](https://github.com/workos/workos-python/commit/ab992b5a069a129f3ba3ffe0845ccc4b310ef098))
* **radar:** Remove device_fingerprint and bot_score parameters from assess request ([#662](https://github.com/workos/workos-python/issues/662)) ([ab992b5](https://github.com/workos/workos-python/commit/ab992b5a069a129f3ba3ffe0845ccc4b310ef098))
* release new version of Python SDK library ([#599](https://github.com/workos/workos-python/issues/599)) ([9aaec74](https://github.com/workos/workos-python/commit/9aaec749b8646ecb5cea095f96ee701fcb2f71f7))
* return organization_name on OrganizationMembership ([#574](https://github.com/workos/workos-python/issues/574)) ([dae4dab](https://github.com/workos/workos-python/commit/dae4daba638660be13b6fd8bcaff03ce63ed6f00))
* Support screen_hint in user_management.get_authorization_url ([#396](https://github.com/workos/workos-python/issues/396)) ([4b3c7bf](https://github.com/workos/workos-python/commit/4b3c7bf3831cd7014e76b36973fd124d2bea17cd))
* update authorization module for fga ([#581](https://github.com/workos/workos-python/issues/581)) ([aa5f1d8](https://github.com/workos/workos-python/commit/aa5f1d8adf610a565f90ddb9b1fc346c83c4ae29))
* **user_management:** Add name field to User, CreateUser, and UpdateUser models ([#665](https://github.com/workos/workos-python/issues/665)) ([4af7da4](https://github.com/workos/workos-python/commit/4af7da4926835b6bbf8a3bad604fcd32a8627766))
* **user_management:** Add user API key management endpoints ([8b5e91d](https://github.com/workos/workos-python/commit/8b5e91d7038485ee012ea6f784a1ed27c5fc25cd))
* **user_management:** Remove organization membership methods, move to new service ([#662](https://github.com/workos/workos-python/issues/662)) ([ab992b5](https://github.com/workos/workos-python/commit/ab992b5a069a129f3ba3ffe0845ccc4b310ef098))
* **user_management:** Remove return_to parameter from revoke_session ([#665](https://github.com/workos/workos-python/issues/665)) ([4af7da4](https://github.com/workos/workos-python/commit/4af7da4926835b6bbf8a3bad604fcd32a8627766))
* **user-management:** add directory_managed to OrganizationMembership ([#583](https://github.com/workos/workos-python/issues/583)) ([f0e716e](https://github.com/workos/workos-python/commit/f0e716ebf5af235c3556e746b77171bf280489e3))
* **vault:** Add new Vault service with encryption and object storage APIs ([#662](https://github.com/workos/workos-python/issues/662)) ([ab992b5](https://github.com/workos/workos-python/commit/ab992b5a069a129f3ba3ffe0845ccc4b310ef098))
* **webhooks:** Rename WebhookEndpointJson to WebhookEndpoint ([#662](https://github.com/workos/workos-python/issues/662)) ([ab992b5](https://github.com/workos/workos-python/commit/ab992b5a069a129f3ba3ffe0845ccc4b310ef098))
* **workos-python:** Add `connection` to `get_authorization_url` ([#61](https://github.com/workos/workos-python/issues/61)) ([542e36d](https://github.com/workos/workos-python/commit/542e36d3f5d265c7f5d80cc086b9673fad17a615))
* **workos-python:** Implement `__str__` for `BaseRequestException` ([#57](https://github.com/workos/workos-python/issues/57)) ([2cecd7b](https://github.com/workos/workos-python/commit/2cecd7b30c43e98c41fc8dd4f3114e5fd0955a4f))


### Bug Fixes

* add documentation on sealing sessions ([#625](https://github.com/workos/workos-python/issues/625)) ([5ae90d0](https://github.com/workos/workos-python/commit/5ae90d024a0a5532c8bb54a21a4190a3de564bea))
* Allow organization_name to be empty on organization membership events ([#595](https://github.com/workos/workos-python/issues/595)) ([865aeb5](https://github.com/workos/workos-python/commit/865aeb514daf701c7d899963e0d247d48b565b4e))
* **deps:** update dependency cryptography to v48 ([#659](https://github.com/workos/workos-python/issues/659)) ([1ccc411](https://github.com/workos/workos-python/commit/1ccc4119ab6aa862b8af740b17667fb5a8a88928))
* **deps:** update dependency pyjwt to v2.12.0 [security] ([#589](https://github.com/workos/workos-python/issues/589)) ([0d50534](https://github.com/workos/workos-python/commit/0d5053403ea2c56203793becaab43fc50d66db43))
* do not JSON parse arbitrary bodies ([#627](https://github.com/workos/workos-python/issues/627)) ([1a8ef00](https://github.com/workos/workos-python/commit/1a8ef00c3b56ecd155853f107a4307ada7caab52))
* Don't validate `aud` claim ([#409](https://github.com/workos/workos-python/issues/409)) ([3cef282](https://github.com/workos/workos-python/commit/3cef282c79deb96fd01597d23e6ccf305daf82c4))
* export missing types and update event tests ([#631](https://github.com/workos/workos-python/issues/631)) ([0bd6cf8](https://github.com/workos/workos-python/commit/0bd6cf87b69bc95d4a3fd1fabba4cf94f59baf15))
* forward Radar context from authenticate_with_code_pkce ([#620](https://github.com/workos/workos-python/issues/620)) ([32aea77](https://github.com/workos/workos-python/commit/32aea77883b80da00829e9c200586eaeb371daf3))
* **generated:** Remove service-specific pagination order enums across SDK ([8b5e91d](https://github.com/workos/workos-python/commit/8b5e91d7038485ee012ea6f784a1ed27c5fc25cd))
* Harden webhook, vault, session, and base client paths ([#654](https://github.com/workos/workos-python/issues/654)) ([d21f3b4](https://github.com/workos/workos-python/commit/d21f3b422b4cf14f8f4a58768bdadff1c3fd49d5))
* Install ruff globally in setup script for code generation ([b12b1d3](https://github.com/workos/workos-python/commit/b12b1d3351bb209c6770c27d28677288c4458d38))
* list Slack as an auth provider for the authorization URL ([#633](https://github.com/workos/workos-python/issues/633)) ([87fc5ab](https://github.com/workos/workos-python/commit/87fc5abf661514a5c54866bec41521b1909ccb38))
* list_client_secrets returns raw list, not paginated response ([#586](https://github.com/workos/workos-python/issues/586)) ([ccc8cd5](https://github.com/workos/workos-python/commit/ccc8cd5f82802cdd275d8fab06390747b33544cd))
* one more regen ([187f83f](https://github.com/workos/workos-python/commit/187f83fa9efce38b8665e9e25d7c214787dba204))
* parse email verification id in exception ([#485](https://github.com/workos/workos-python/issues/485)) ([b9a93d4](https://github.com/workos/workos-python/commit/b9a93d4a3853ce9f20d2e85b6dcde761b80dcdf1))
* regenerate methods to include missing params ([#610](https://github.com/workos/workos-python/issues/610)) ([6792792](https://github.com/workos/workos-python/commit/6792792cc5ad51df50fadd0248b797ffe74ab095))
* Remove Coana workflow files ([#580](https://github.com/workos/workos-python/issues/580)) ([bb8d2f1](https://github.com/workos/workos-python/commit/bb8d2f1ba3a904383793426114d9ff93297d1658))
* Remove extractVersion from matchUpdateTypes rules ([#623](https://github.com/workos/workos-python/issues/623)) ([09a2e5d](https://github.com/workos/workos-python/commit/09a2e5d1e7666eb6b435c49ed3ba1e63d8ae274e))
* **renovate:** explicitly enable minor and patch updates ([#663](https://github.com/workos/workos-python/issues/663)) ([ff8ad1b](https://github.com/workos/workos-python/commit/ff8ad1ba5ef2d2222802dfc2f8de337551740ad4))
* restore typed `EventSchema` discriminated union dispatcher ([#629](https://github.com/workos/workos-python/issues/629)) ([af95901](https://github.com/workos/workos-python/commit/af95901ed8e607622795a19b15c4a7bf88eca4f7))
* restore typing to events ([bbff53f](https://github.com/workos/workos-python/commit/bbff53f3be5af897d6ae917e7a1a8e256d5643e4))
* set canonical User-Agent header format ([#643](https://github.com/workos/workos-python/issues/643)) ([f9cf9a1](https://github.com/workos/workos-python/commit/f9cf9a1240556c31a0d028e74a255704d2e88380))
* slight rename ([2b2e9e2](https://github.com/workos/workos-python/commit/2b2e9e26ec6615a3dd8bc4a6c2fc86dadbb4cbb0))
* update renovate rules ([#572](https://github.com/workos/workos-python/issues/572)) ([401976b](https://github.com/workos/workos-python/commit/401976b79b0fe130c49435b72eb27de641635795))

## [8.1.0](https://github.com/workos/workos-python/compare/v8.0.0...v8.1.0) (2026-06-17)

### Bug Fixes

* **renovate:** explicitly enable minor and patch updates ([#663](https://github.com/workos/workos-python/issues/663)) ([ff8ad1b](https://github.com/workos/workos-python/commit/ff8ad1ba5ef2d2222802dfc2f8de337551740ad4))

- [#665](https://github.com/workos/workos-python/pull/665) feat(generated)!: regenerate from spec (9 changes)

  **⚠️ Breaking**
  - **[api_keys](https://workos.com/docs/reference/authkit/api-keys)**:
    - Made `expires_at` required in API key models
  - **[directory_sync](https://workos.com/docs/reference/directory-sync)**:
    - Removed model `DsyncDeactivated`
    - Removed model `DsyncDeactivatedData`
    - Removed model `DsyncDeactivatedDataDomain`
    - Removed enum `DsyncDeactivatedDataType`
    - Removed enum `DsyncDeactivatedDataState`
  - **[radar](https://workos.com/docs/reference/radar)**:
    - Removed `domain_sign_up_rate_limit` from `RadarStandaloneResponseControl`
  - **[user_management](https://workos.com/docs/reference/authkit/user)**:
    - Removed `return_to` from `RevokeSession`

  **Features**
  - **[api_keys](https://workos.com/docs/reference/authkit/api-keys)**:
    - Added model `ExpireApiKey`
    - Added model `ApiKeyUpdated`
    - Added model `ApiKeyUpdatedData`
    - Added model `ApiKeyUpdatedDataOwner`
    - Added model `UserApiKeyUpdatedDataOwner`
    - Added model `ApiKeyUpdatedDataPreviousAttribute`
    - Added endpoint `POST /api_keys/{id}/expire`
  - **[audit_logs](https://workos.com/docs/reference/audit-logs)**:
    - Added `Snowflake` to `AuditLogConfigurationLogStreamType`
  - **[connect](https://workos.com/docs/reference/workos-connect/standalone)**:
    - Added `name` to `UserObject`
  - **[directory_sync](https://workos.com/docs/reference/directory-sync)**:
    - Added model `DsyncTokenCreated`
    - Added model `DsyncTokenCreatedData`
    - Added model `DsyncTokenRevoked`
    - Added model `DsyncTokenRevokedData`
  - **[user_management](https://workos.com/docs/reference/authkit/user)**:
    - Added `name` to user management models
  - **[webhooks](https://workos.com/docs/reference/webhooks)**:
    - Added `api_key.updated` to `CreateWebhookEndpointEvents`
    - Added `api_key.updated` to `UpdateWebhookEndpointEvents`

## [8.0.0](https://github.com/workos/workos-python/compare/v7.0.1...v8.0.0) (2026-05-26)

### Bug Fixes

* **deps:** update dependency cryptography to v48 ([#659](https://github.com/workos/workos-python/issues/659)) ([1ccc411](https://github.com/workos/workos-python/commit/1ccc4119ab6aa862b8af740b17667fb5a8a88928))

* [#662](https://github.com/workos/workos-python/pull/662) feat(generated)!: regenerate from spec (10 changes)

  **⚠️ Breaking**
  * **user_management:** Remove organization membership methods, move to new service
    * Removed `list_organization_memberships`, `create_organization_membership`, `get_organization_membership`, `update_organization_membership`, `delete_organization_membership`, `deactivate_organization_membership`, and `reactivate_organization_membership` methods from UserManagement.
    * Removed `RoleSingle` and `RoleMultiple` dataclasses from UserManagement.
    * Organization membership management is now handled by the new `OrganizationMembershipService`.
    * Client accessor renamed from `client.user_management_organization_membership_groups` to `client.organization_membership`.
  * **organization_membership:** Add new OrganizationMembershipService with membership and group operations
    * Created new `OrganizationMembershipService` with `list_organization_memberships`, `create_organization_membership`, `get_organization_membership`, `update_organization_membership`, `delete_organization_membership`, `deactivate_organization_membership`, `reactivate_organization_membership`, and `list_organization_membership_groups` methods.
    * Added `RoleSingle` and `RoleMultiple` dataclasses to support role assignment.
    * Added `AsyncOrganizationMembershipService` for async operations.
  * **vault:** Replace hand-maintained Vault module with generated Vault service
    * The old `workos.vault` module (`vault.py`) has been replaced by a generated `vault/_resource.py` service. Method renames:
      * `read_object` → `get_kv`
      * `read_object_by_name` → `get_name`
      * `get_object_metadata` → removed (no direct equivalent)
      * `list_objects` → `list_kv`
      * `list_object_versions` → `list_kv_versions`
      * `create_object` → `create_kv`
      * `update_object` → `update_kv`
      * `delete_object` → `delete_kv`
      * `create_data_key(key_context=...)` → `create_data_key(context=...)`
      * `decrypt_data_key` → `create_decrypt`
    * Removed types: `DataKey`, `DataKeyPair`, `ObjectDigest`, `ObjectUpdateBy`. Replaced by new generated models (`CreateDataKeyResponse`, `DecryptResponse`, `ObjectMetadata`, `ObjectSummary`, `ObjectWithoutValue`, `VaultObject`, etc.).
    * Added new methods: `create_rekey`, `list_kv_metadata`.
    * Added `AsyncVault` for async operations.
    * Client-side `encrypt`/`decrypt` (AES-GCM) methods are preserved with the same signatures.
  * **connect:** `ConnectApplication` is now a discriminated union
    * `ConnectApplication` was a single dataclass; it is now a discriminated union dispatcher based on `application_type`.
    * All Connect methods (`list_applications`, `create_application`, `get_application`, `update_application`) now return `ConnectApplicationVariant` (a union of `ConnectApplicationM2M`, `ConnectApplicationOAuth`, or `ConnectApplicationUnknown`).
    * Code using `isinstance(x, ConnectApplication)` or accessing type-specific fields without checking the variant will need updating.
  * **radar:** Remove device_fingerprint and bot_score parameters from assess request
    * Removed `device_fingerprint` and `bot_score` optional parameters from `Radar.create_attempt` and `AsyncRadar.create_attempt` methods.
    * Removed these fields from `RadarStandaloneAssessRequest` model.
  * **radar:** Rename radar list/action enums and remove enum values
    * Renamed `RadarAction` to `RadarListAction` and `RadarType` to `RadarListType` (affects `add_list_entry` and `remove_list_entry` method signatures).
    * `RadarStandaloneResponseBlocklistType` is now a lazy re-export alias of `RadarListType`.
    * Removed `credential_stuffing` and `ip_sign_up_rate_limit` values from `RadarStandaloneResponseControl` enum.
    * Removed `login`, `signup`, `sign_up`, and `sign_in` values from `RadarStandaloneAssessRequestAction` enum; only `sign-up` and `sign-in` remain.
  * **authorization:** Remove search parameter and add resource/role filtering
    * Removed `search` parameter from `Authorization.list_resources` and `AsyncAuthorization.list_resources`.
    * Added `resource_id`, `resource_external_id`, `resource_type_slug` parameters to `list_role_assignments` method.
    * Added `role_slug` parameter to `list_role_assignments_for_resource_by_external_id` and `list_role_assignments_for_resource` methods.
  * **api_keys:** Add expires_at field to API key models
    * Added `expires_at` optional field to `CreateOrganizationApiKey` model.
    * Added `expires_at` optional field to `CreateUserApiKey` model.
    * Added `expires_at` to organizational and user API key models (OrganizationApiKey, OrganizationApiKeyWithValue, UserApiKey, UserApiKeyWithValue).
    * Added `expires_at` parameter to `create_organization_api_key` and `create_user_api_key` methods.
  * **audit_logs:** Rename audit log models and update service references
    * Renamed `AuditLogActionJson` to `AuditLogAction`.
    * Renamed `AuditLogExportJson` to `AuditLogExport`.
    * Renamed `AuditLogSchemaJson` to `AuditLogSchema`.
    * Renamed `AuditLogSchemaJsonActor` to `AuditLogSchemaActorInput` and `AuditLogSchemaJsonTarget` to `AuditLogSchemaTargetInput`.
    * Added new `AuditLogSchemaInput` model (used for schema creation payloads).
    * Renamed `AuditLogsRetentionJson` to `AuditLogsRetention`.
    * Updated all service methods to use new model names.
  * **webhooks:** Rename WebhookEndpointJson to WebhookEndpoint
    * Renamed `WebhookEndpointJson` model to `WebhookEndpoint`.
    * Updated all service methods to use the new model name.
    * Updated webhook endpoint status references.

  **Features**
  * **common:** Add new models for pipes events and enhancements
    * Added `Actor` model representing the user or API key that performed an action.
    * Added `Error` model for error response bodies.
    * Added `PipeConnectedAccount` model with state enumeration.
    * Added pipe event models: `PipesConnectedAccountConnected`, `PipesConnectedAccountDisconnected`, `PipesConnectedAccountReauthorizationNeeded`.
    * Added webhook event enum values for pipes connected account events.
    * Renamed `AuditLogExportJsonState` to `AuditLogExportState`.
    * Renamed `WebhookEndpointJsonStatus` to `WebhookEndpointStatus`.
    * Updated `UserManagementAuthenticationScreenHint` to use `RadarStandaloneAssessRequestAction` type alias.

## [7.0.1](https://github.com/workos/workos-python/compare/v7.0.0...v7.0.1) (2026-05-11)


### Bug Fixes

* Harden webhook, vault, session, and base client paths ([#654](https://github.com/workos/workos-python/issues/654)) ([d21f3b4](https://github.com/workos/workos-python/commit/d21f3b422b4cf14f8f4a58768bdadff1c3fd49d5))

## [7.0.0](https://github.com/workos/workos-python/compare/v6.2.0...v7.0.0) (2026-05-07)


### ⚠ BREAKING CHANGES

* **api_keys:** Restructure API key models for dual ownership
* **common:** Add user API key event models and refactor BYOK key provider
* **authorization:** Refactor role assignment models and add list endpoints

### Features

* **api_keys:** Restructure API key models for dual ownership ([8b5e91d](https://github.com/workos/workos-python/commit/8b5e91d7038485ee012ea6f784a1ed27c5fc25cd))
* **authorization:** Refactor role assignment models and add list endpoints ([8b5e91d](https://github.com/workos/workos-python/commit/8b5e91d7038485ee012ea6f784a1ed27c5fc25cd))
* **common:** Add user API key event models and refactor BYOK key provider ([8b5e91d](https://github.com/workos/workos-python/commit/8b5e91d7038485ee012ea6f784a1ed27c5fc25cd))
* **docs:** Publish pdoc-generated API reference to GitHub Pages ([#651](https://github.com/workos/workos-python/issues/651)) ([05831ea](https://github.com/workos/workos-python/commit/05831ea7ce339448cb9f1986b41e5e34bf8442e7))
* **user_management:** Add user API key management endpoints ([8b5e91d](https://github.com/workos/workos-python/commit/8b5e91d7038485ee012ea6f784a1ed27c5fc25cd))


### Bug Fixes

* **generated:** Remove service-specific pagination order enums across SDK ([8b5e91d](https://github.com/workos/workos-python/commit/8b5e91d7038485ee012ea6f784a1ed27c5fc25cd))

## [6.2.0](https://github.com/workos/workos-python/compare/v6.1.0...v6.2.0) (2026-05-01)


### Features

* add `get_jwks_url` helper to UserManagement ([#644](https://github.com/workos/workos-python/issues/644)) ([53134d3](https://github.com/workos/workos-python/commit/53134d32f168dd0da606672125e8cdd221832761))
* **generated:** use explicit re-export form in service __init__.py ([#645](https://github.com/workos/workos-python/issues/645)) ([7ecb2e9](https://github.com/workos/workos-python/commit/7ecb2e9fafa030afdf27061b2b45f9d59fe2e900))


### Bug Fixes

* set canonical User-Agent header format ([#643](https://github.com/workos/workos-python/issues/643)) ([f9cf9a1](https://github.com/workos/workos-python/commit/f9cf9a1240556c31a0d028e74a255704d2e88380))

## [6.1.0](https://github.com/workos/workos-python/compare/v6.0.8...v6.1.0) (2026-04-28)


### Features

* **generated:** Add Groups API and Waitlist User events support ([#640](https://github.com/workos/workos-python/issues/640)) ([a10d02b](https://github.com/workos/workos-python/commit/a10d02b1bc88c20cab2b83c006aceae968b86bca))


### Bug Fixes

* Install ruff globally in setup script for code generation ([b12b1d3](https://github.com/workos/workos-python/commit/b12b1d3351bb209c6770c27d28677288c4458d38))

## [6.0.8](https://github.com/workos/workos-python/compare/v6.0.7...v6.0.8) (2026-04-24)


### Bug Fixes

* list Slack as an auth provider for the authorization URL ([#633](https://github.com/workos/workos-python/issues/633)) ([87fc5ab](https://github.com/workos/workos-python/commit/87fc5abf661514a5c54866bec41521b1909ccb38))

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
