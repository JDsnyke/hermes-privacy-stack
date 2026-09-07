## Summary

Describe what changes and why.

## Privacy / security impact

- Data leaving the device:
- New listening ports or network exposure:
- New credentials / OAuth scopes:
- New third-party code, images, MCPs or skills:
- Least-privilege / fail-closed behavior:

## Validation

- [ ] `python bootstrap.py --self-test`
- [ ] `python scripts/check_secrets.py`
- [ ] `python scripts/doctor.py --static`
- [ ] Relevant Windows/macOS/Linux path considered
- [ ] No credentials, tokens, personal memory, live databases or runtime `.env` files committed
- [ ] ROADMAP.md updated when scope/status changed

## Rollback

Explain how to revert the change without losing Hermes state or Hindsight memory.
