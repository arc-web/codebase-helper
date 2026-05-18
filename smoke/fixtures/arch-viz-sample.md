# Sample Architecture Visualization

This sample demonstrates the `arch-viz` renderer schema. Replace the JSON block with your own architecture.

```arch-viz
{
  "project": {
    "title": "Sample Auth Architecture",
    "subtitle": "Demonstrates arch-viz renderer",
    "logoIcon": "🏗",
    "logoGradient": "linear-gradient(135deg, #238636, #2ea043)"
  },
  "identities": [
    {
      "id": "agent",
      "name": "Automated Agent",
      "icon": "🤖",
      "avatarGradient": "linear-gradient(135deg, #1f6feb, #388bfd)",
      "authType": "AppRole",
      "authColor": "var(--blue)",
      "authBg": "var(--blue-dim)",
      "description": "Machine identity with scoped read access.",
      "badges": [
        { "text": "AppRole", "bg": "var(--blue-dim)", "color": "var(--blue)" },
        { "text": "TTL: 8h", "bg": "var(--surface3)", "color": "var(--text2)" }
      ],
      "networkPath": [
        { "icon": "🖥️", "name": "Agent", "subtext": "local process" },
        { "icon": "☁️", "name": "Cloudflare", "subtext": "tunnel" },
        { "icon": "🔐", "name": "Vault", "subtext": "secret store" },
        { "icon": "🔑", "name": "Secret", "subtext": "returned" }
      ],
      "steps": [
        {
          "node": "1Password",
          "nodeColor": "var(--blue)",
          "numberBg": "var(--blue-dim)",
          "action": "Bootstrap: read role_id + secret_id",
          "detail": "op item get 'My AppRole' --vault ARC --reveal"
        },
        {
          "node": "Vault",
          "nodeColor": "var(--purple)",
          "numberBg": "var(--purple-dim)",
          "action": "POST /v1/auth/approle/login",
          "detail": "{ role_id, secret_id } → 8h token"
        },
        {
          "node": "Vault KV",
          "nodeColor": "var(--green)",
          "numberBg": "var(--green-dim)",
          "action": "GET /v1/secret/data/shared/my-api-key",
          "detail": "response.data.data.value → API key"
        },
        {
          "node": "Downstream API",
          "nodeColor": "var(--orange)",
          "numberBg": "var(--orange-dim)",
          "action": "Use key to call service",
          "detail": "X-API-Key: <key>"
        }
      ],
      "policies": {
        "allow": ["shared/*", "projects/*"],
        "deny": ["human-only/*", "admin/*"]
      },
      "auditLog": "type=request | auth.token.type=service\nauth.metadata.role_name=agent | path=secret/data/shared/my-api-key\noperation=read | remote_address=1.2.3.4",
      "alert": {
        "type": "blue",
        "icon": "ℹ️",
        "text": "Audit log shows role_name=agent — distinct from other AppRoles. Each agent gets its own fingerprint."
      }
    },
    {
      "id": "human",
      "name": "Human Operator",
      "icon": "👤",
      "avatarGradient": "linear-gradient(135deg, #9e6a03, #e3b341)",
      "authType": "userpass",
      "authColor": "var(--yellow)",
      "authBg": "var(--orange-dim)",
      "description": "Human team member with broader read scope.",
      "badges": [
        { "text": "userpass", "bg": "var(--orange-dim)", "color": "var(--yellow)" },
        { "text": "TTL: 8h", "bg": "var(--surface3)", "color": "var(--text2)" }
      ],
      "networkPath": [
        { "icon": "👤", "name": "Human", "subtext": "browser / CLI" },
        { "icon": "☁️", "name": "Cloudflare", "subtext": "tunnel" },
        { "icon": "🔐", "name": "Vault", "subtext": "secret store" },
        { "icon": "🔑", "name": "Secret", "subtext": "returned" }
      ],
      "steps": [
        {
          "node": "1Password",
          "nodeColor": "var(--yellow)",
          "numberBg": "var(--orange-dim)",
          "action": "Look up password in 1P",
          "detail": "op item get 'Vault userpass - alice' --vault MyVault"
        },
        {
          "node": "Vault",
          "nodeColor": "var(--purple)",
          "numberBg": "var(--purple-dim)",
          "action": "POST /v1/auth/userpass/login/alice",
          "detail": "{ password } → 8h token"
        },
        {
          "node": "Vault KV",
          "nodeColor": "var(--green)",
          "numberBg": "var(--green-dim)",
          "action": "GET secret/data/shared/service-key",
          "detail": "response.data.data.value → key"
        }
      ],
      "policies": {
        "allow": ["shared/*", "hosting/*", "tool-infra/*"],
        "deny": ["agent-only/*", "admin/*"]
      },
      "auditLog": "type=request | auth.token.type=service\nauth.display_name=userpass-alice | path=secret/data/shared/service-key\noperation=read",
      "alert": {
        "type": "green",
        "icon": "✅",
        "text": "Human identities use display_name=userpass-alice in audit log — distinct per user, not per machine."
      }
    }
  ],
  "flows": [
    {
      "id": "ci-flow",
      "title": "CI/CD Credential Flow",
      "description": "How a CI pipeline fetches secrets at runtime without storing them in the repo.",
      "badges": ["automated", "ephemeral token", "5-min TTL"],
      "steps": [
        {
          "actor": "CI Runner",
          "actorColor": "var(--blue)",
          "actorBg": "var(--blue-dim)",
          "dotColor": "var(--blue)",
          "event": "Pipeline starts",
          "detail": "Reads VAULT_ROLE_ID and VAULT_SECRET_ID from CI environment secrets.",
          "code": null
        },
        {
          "actor": "Vault",
          "actorColor": "var(--purple)",
          "actorBg": "var(--purple-dim)",
          "dotColor": "var(--purple)",
          "event": "AppRole login",
          "detail": "Returns a 5-minute token. Short TTL ensures it expires before logs are accessible.",
          "code": "POST /v1/auth/approle/login\n{ role_id, secret_id } → { client_token, lease_duration: 300 }"
        },
        {
          "actor": "Vault KV",
          "actorColor": "var(--green)",
          "actorBg": "var(--green-dim)",
          "dotColor": "var(--green)",
          "event": "Read API key",
          "detail": "Token used once to fetch the key, then discarded.",
          "code": "GET /v1/secret/data/shared/service-key\nX-Vault-Token: <5min-token>"
        },
        {
          "actor": "Downstream API",
          "actorColor": "var(--orange)",
          "actorBg": "var(--orange-dim)",
          "dotColor": "var(--orange)",
          "event": "API call succeeds",
          "detail": "Pipeline completes work using the real key. Token has already expired.",
          "code": null
        }
      ],
      "stateMappings": [
        { "trigger": "Pipeline success", "result": "Task → Done", "resultColor": "var(--green)" },
        { "trigger": "Pipeline fails", "result": "Task → Blocked", "resultColor": "var(--red)" }
      ]
    }
  ],
  "infrastructure": [
    { "label": "Vault endpoint", "value": "https://vault.example.com" },
    { "label": "Auth method", "value": "AppRole + userpass" },
    { "label": "KV version", "value": "v2" },
    { "label": "Token TTL", "value": "8h (human) / 5m (CI)" }
  ]
}
```
