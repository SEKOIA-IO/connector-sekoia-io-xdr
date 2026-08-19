# Operations mapping

This table lists all operations currently exposed by the connector (from sekoia-io-xdr/info.json), their operation title, HTTP method, endpoint template, and associated playbook action source from [automation-library/Sekoia.io/action_*.json](https://github.com/SEKOIA-IO/automation-library/tree/develop/Sekoia.io).

| Operation | Operation Title | HTTP Method | Endpoint | Playbook action JSON | Playbook action name | Playbook action slug |
| --- | --- | --- | --- | --- | --- | --- |
| activate_countermeasure | Activate a Countermeasure | PATCH | https://app.sekoia.io/api/v1/sic/alerts/countermeasures/{cm_uuid}/activate | action_activate_a_countermeasure.json | Activate Countermeasure | activate_countermeasure |
| add_comment_to_alert | Add Comment to Alert | POST | https://app.sekoia.io/api/v1/sic/alerts/{uuid}/comments | action_post_a_comment_on_an_alert.json | Comment Alert | comment_alert |
| add_to_ioc_collection | Add IOC to IOC Collection | POST | https://app.sekoia.io/api/v2/inthreat/ioc-collections/{ioc_collection_id}/indicators/text | action_add_ioc_to_ioc_collection.json | Add IOC to IOC Collection | add_to_ioc_collection |
| comment_case | Comment Case | POST | https://app.sekoia.io/api/v1/sic/cases/{uuid}/comments | action_post_a_comment_on_a_case.json | Comment case | comment_case |
| create_content_proposal | Create Content Proposal | POST | https://app.sekoia.io/api/v2/inthreat/bundles | action_inthreat_post_bundle.json | Create Content Proposal | create_content_proposal |
| create_content_proposal_from_pdf | Create Content Proposal from PDF | POST | https://app.sekoia.io/api/v2/inthreat/reports/pdf | action_post_reports_pdf.json | Create Content Proposal from PDF | create_content_proposal_from_pdf |
| create_content_proposal_from_url | Create Content Proposal from URL | POST | https://app.sekoia.io/api/v2/inthreat/reports/url | action_post_reports_url.json | Create Content Proposal from URL | create_content_proposal_from_url |
| delete_asset | [Deprecated] Delete Asset | DELETE | https://app.sekoia.io/api/v1/asset-management/assets/{asset_uuid} | action_deletes_an_asset.json | [DEPRECATED] Delete an asset | delete_asset |
| deny_countermeasure | Deny a Countermeasure | PATCH | https://app.sekoia.io/api/v1/sic/alerts/countermeasures/{cm_uuid}/deny | action_deny_a_countermeasure.json | Deny Countermeasure | deny_countermeasure |
| edit_alert | Edit Alert | PATCH | https://app.sekoia.io/api/v1/sic/alerts/{uuid} | action_patch_an_alert.json | Edit Alert | edit_alert |
| edit_case | Edit Case | PATCH | https://app.sekoia.io/api/v1/sic/cases/{uuid} | action_update_case.json | Edit case | edit_case |
| get_alert | Get Alert | GET | https://app.sekoia.io/api/v1/sic/alerts/{alert_uuid} | action_get_an_alert.json | Get Alert | get_alert |
| get_asset | Get Asset | GET | https://app.sekoia.io/api/v2/asset-management/assets/{uuid} | action_returns_an_asset.json | Get Asset | get_asset |
| get_case | Get Case | GET | https://app.sekoia.io/api/v1/sic/cases/{uuid} | action_get_case.json | Get case | get_case |
| get_custom_priority | Get custom priority | GET | https://app.sekoia.io/api/v1/sic/custom_priorities/{priority_uuid} | action_get_custom_priority.json | Get custom priority | get_custom_priority |
| get_custom_status | Get custom status | GET | https://app.sekoia.io/api/v1/sic/custom_statuses/{status_uuid} | action_get_custom_status.json | Get custom status | get_custom_status |
| get_custom_verdict | Get custom verdict | GET | https://app.sekoia.io/api/v1/sic/custom_verdicts/{verdict_uuid} | action_get_custom_verdict.json | Get custom verdict | get_custom_verdict |
| get_events | Get Events | GET | Custom flow: https://app.sekoia.io/api/v1/sic/conf/events/search/jobs/{job_uuid}/events | action_get_events.json | Get Events | get_events |
| list_alerts | List Alerts | GET | https://app.sekoia.io/api/v1/sic/alerts | action_list_alerts.json | Search Alerts | search_alerts |
| list_assets | List Assets | GET | https://app.sekoia.io/api/v2/asset-management/assets | action_list_assets.json | [DEPRECATED] List Assets | list_assets |
| list_case_comments | List Case Comments | GET | https://app.sekoia.io/api/v1/sic/cases/{case_uuid}/comments | action_list_case_comments.json | List comments of a case | list_case_comments |
| revoke_assetv2 | Revoke an Asset (V2) | PUT | https://app.sekoia.io/api/v2/asset-management/assets/{uuid}/revoke | action_revoke_an_asset_v2.json | Revoke an asset (V2) | revoke_assetv2 |
| search_cases | Search Cases | GET | https://app.sekoia.io/api/v1/sic/cases | action_lists_cases.json | Search Cases | search_cases |
| update_alert_status | Update Alert Status | PATCH | https://app.sekoia.io/api/v1/sic/alerts/{uuid}/workflow | action_trigger_an_action_on_the_alert_workflow.json | Update Alert Status | update_alert_status |
| update_asset | [Deprecated] Update Asset | PUT | https://app.sekoia.io/api/v1/asset-management/assets/{asset_uuid} | action_update_asset.json | Update asset | update_assets |
| update_assets | Update Assets | PUT | https://app.sekoia.io/api/v2/asset-management/assets/{uuid} | action_update_asset.json | Update asset | update_assets |
| upload_observables | Upload Observables | POST | https://app.sekoia.io/api/v2/inthreat/observables/bulk | action_inthreat_upload_observables.json | Upload Observables | upload_observables |

## Notes

- Some connector operation names intentionally differ from playbook action slugs, for example:
  - add_comment_to_alert -> comment_alert
  - list_alerts -> search_alerts
  - update_asset -> update_assets (legacy connector operation name mapped to the newer action slug)

## Specs Mapping (Client Request)

Source ticket:
- [Improvement] FortiSOAR integration update #1515
- Created on 2026-04-15
- https://github.com/SekoiaLab/integration/issues/1515


Notes:
- The spec capabilities listed below are directly sourced from this client ticket
- Non-implemented capabilities listed below cannot currently be derived from existing playbook actions from the [Sekoia.io automation module](https://github.com/SEKOIA-IO/automation-library/tree/develop/Sekoia.io), but some could be implemented in the future from currently unused [OpenAPI endpoints](https://docs.sekoia.com/developer/api/) that are not yet exposed by playbook actions

| Domain | Spec capability | Implemented operation | Coverage | Notes |
| --- | --- | --- | --- | --- |
| Alerts | Create alert comment | add_comment_to_alert | Implemented | Direct match |
| Alerts | Get alerts | list_alerts | Implemented | Direct match |
| Alerts | Get alert comment | get_alert | Implemented | Comments are returned by get_alert (include_comments) |
| Alerts | Get alert details | get_alert | Implemented | Direct match |
| Alerts | Update alert assignee | edit_alert | Implemented | assignee field supported |
| Alerts | Update alert priority | edit_alert | Implemented | Uses urgency field on alert |
| Alerts | Update alert status | update_alert_status | Implemented | Workflow action endpoint |
| Alerts | Update alert verdict | edit_alert | Implemented | verdict_uuid field supported |
| Assets | Get assets | list_assets | Implemented | Direct match |
| Assets | Get asset details | get_asset | Implemented | Direct match |
| Assets | Update asset status | update_assets | Implemented | Via reviewed/revoked fields |
| Cases | Create case comment | comment_case | Implemented | Direct match |
| Cases | Get cases | search_cases | Implemented | Direct match |
| Cases | Get case comment | list_case_comments | Implemented | List comments endpoint |
| Cases | Get case details | get_case | Implemented | Direct match |
| Cases | Update case assignee | edit_case | Implemented | Via subscribers field (assignee type) |
| Cases | Update case priority | edit_case | Implemented | priority/custom_priority_uuid |
| Cases | Update case status | edit_case | Implemented | status_uuid/status_name |
| Cases | Update case verdict | edit_case | Implemented | verdict_uuid |
| Countermeasures | Get countermeasures | N/A | Not implemented | No dedicated list operation in connector |
| Countermeasures | Get countermeasure details | N/A | Not implemented | No dedicated get operation in connector |
| Countermeasures | Update countermeasures status | activate_countermeasure / deny_countermeasure | Partially implemented | Two explicit status transition operations |
| Custom fields | Get custom field priority | get_custom_priority | Implemented | Direct match |
| Custom fields | Get custom field status | get_custom_status | Implemented | Direct match |
| Custom fields | Get custom field verdict | get_custom_verdict | Implemented | Direct match |
| Custom fields | Update custom field priority | N/A | Not implemented | OpenAPI endpoints exist, no connector operation yet |
| Custom fields | Update custom field status | N/A | Not implemented | OpenAPI endpoints exist, no connector operation yet |
| Custom fields | Update custom field verdict | N/A | Not implemented | OpenAPI endpoints exist, no connector operation yet |
| Events | Get events | get_events | Implemented | Direct match |
| Events | Get event details | N/A | Not implemented | No dedicated get-event-by-id operation |
| Events | Update event status | N/A | Not implemented | No status update operation in connector |
