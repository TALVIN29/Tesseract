# Engineering — Skill

## Code Deployment
1. Run `pytest` — all tests must pass
2. Tag release: `git tag v<major>.<minor>.<patch>`
3. Deploy to staging: `docker compose up -d`
4. Smoke test: hit `/health` endpoint
5. Merge PR to main — triggers prod deploy

## Incident Escalation
1. Investigate for < 2 hours
2. If unresolved: page tech lead via Slack `#oncall`
3. If customer-facing: open war-room in `#incident` channel
4. Post-mortem required within 48h of resolution

## Code Review Checklist
- [ ] Tests written and passing
- [ ] No secrets or API keys committed
- [ ] Function names describe what, not how
- [ ] PR description explains why, not what

See also: [[engineering/soul]] for quality principles and [[hr/skill]] for onboarding.
