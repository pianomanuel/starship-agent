# End-to-end security — pianomanuel.com BETA
Restored onto main 2026-09-13 from Drive SECURITY_E2E_BETA_1.01.md.
No Keychain values. No .p8.

E2E here does **not** mean a new crypto product. It means every hop has an owner, a lock, and an undo — and no hop pretends to be another.

## Trust boundaries (do not flatten)

```
[You / Apple ID / Keychain]
        |  Sign in with Apple (hub only, not built yet)
        v
[Mac localhost hub] ---- site/ HTML has ZERO secrets
        |
        +--> [GitHub private pianomanuel/ManuelOps]  staff code
        +--> [Google Drive ManuelOps]                 staff workbooks
        +--> [Grok / xAI chat + automations]          CoS brain
        +--> [Jira PCS]                               login wall, no API
        +--> [Outlook/Gmail/Calendar]                 ops pings only
```

OneDrive is out. Public DNS is out. Google is **ops**, not hub IdP. KAN is off the compiled deck.

## Honest limit
There is **no** extra envelope that hides Drive workbooks from Google or chats from xAI. Calling that E2E encryption would be a lie. Calling it E2E *control* is accurate.

## Never commit
Passwords, AuthKey_*.p8, clinical packets, SS amounts, Fun-vault body, Jim letter body, street address.

## Required records (Keychain only — empty here)
- APPLE_TEAM_ID
- APPLE_BUNDLE_ID=com.pianomanuel.hub
- SIWA_SERVICE_ID=com.pianomanuel.hub.web
- APPLE_ICLOUD_CONTAINER=iCloud.com.pianomanuel.hub
- PUBLIC_DNS=off

## Connector grants
Keep: GitHub, Google Drive, Gmail, Calendar, Outlook, Automations.
Do not add: Jira API, OneDrive, public Pages.
