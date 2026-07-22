# ADR-002: Google OAuth2 Must Use Web Application Credential Type
**Status:** Accepted | **Date:** 2026-06-08 | **Sprint:** 0

## Context
The 2D Planes require a Google Sheets sync bridge (PLN-003). n8n handles the OAuth2 flow for Google API credentials. The n8n OAuth2 callback URL is a server-side redirect at `https://[n8n-host]/rest/oauth2-credential/callback`.

## Decision
The Google OAuth2 credential created in Google Cloud Console MUST be of type **Web Application**, NOT **Desktop Application**.

Google enforces the following rule: Desktop Application credentials only permit `localhost` or `http://localhost` as valid redirect URIs. Any non-localhost redirect URI registered against a Desktop credential will result in a `redirect_uri_mismatch` error at authorization time.

Since n8n is deployed on a server with a non-localhost hostname, the credential MUST be a Web Application with the full server redirect URI explicitly registered.

## Consequences
- Positive: OAuth2 authorization flow completes without errors in production.
- Negative: If the Google Cloud Console project is recreated or the credential is accidentally deleted and re-created as Desktop type, the n8n integration will silently break at token refresh time, not at configuration time. The runbook `/docs/runbooks/google-oauth-setup.md` (TESS-050) mitigates this risk.
- Action required in Sprint 4: Document this in the runbook and add a smoke test that verifies the credential type after any Google Cloud Console changes.
