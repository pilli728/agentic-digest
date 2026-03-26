---
title: "OpenClaw Week-One Setup: Lock Your Gateway Before You Connect Anything"
description: "The exact setup sequence for OpenClaw that avoids the security mistakes 80% of new users make. Gateway config, plugin vetting, cost controls."
date: "2026-03-26"
tier: "founding"
category: "guide"
---

OpenClaw is an open-source gateway for managing AI agent plugins. It lets you connect agents to tools — web search, code execution, database access, file systems — through a single control plane.

It's powerful. It's also dangerous if you set it up wrong.

Most people install it, connect a bunch of plugins, and start building. That's backwards. You need to lock the gateway down first.

## Why Setup Order Matters

OpenClaw's default configuration is permissive. Out of the box, any connected plugin can access any resource. There's no spending cap. There's no request logging. There's no plugin isolation.

If you connect a third-party plugin before configuring security, that plugin has the same access as your own code. I've seen setups where a random community plugin could read environment variables. That means API keys. Database credentials. Everything.

Lock first. Connect second.

## Step 1: Gateway Security (Day 1)

Before you touch plugins, configure these three things:

**Authentication**: Set up API key auth on the gateway itself. Every request to OpenClaw should require a key. This isn't optional.

```yaml
# openclaw.config.yaml
gateway:
  auth:
    type: api_key
    keys:
      - name: "production"
        key: "${OPENCLAW_API_KEY}"
        permissions: ["read", "write", "execute"]
```

**Network isolation**: Restrict which hosts plugins can reach. By default, a plugin can make outbound requests to anywhere. Lock it to your approved list.

```yaml
network:
  allowed_hosts:
    - "api.openai.com"
    - "api.anthropic.com"
    - "your-database.internal"
  deny_all_others: true
```

**Request logging**: Turn on full request/response logging from day one. You'll need this when something goes wrong. And something will go wrong.

## Step 2: Plugin Vetting (Day 2-3)

Not all plugins are equal. Before installing any plugin, check three things:

1. **Source code availability.** If you can't read the code, don't install it. Period.
2. **Permission scope.** What does the plugin ask for? A web search plugin shouldn't need file system access. If permissions look too broad, skip it.
3. **Maintenance status.** Check the last commit date. Abandoned plugins don't get security patches.

Start with the core plugins from the OpenClaw org. They're audited. Community plugins need manual review.

Install one plugin at a time. Test it. Check the logs. Then move to the next one. Batch-installing five plugins and debugging which one is misbehaving is a miserable experience.

## Step 3: Cost Controls (Day 4-5)

AI agent plugins can run up bills fast. An agent in a loop hitting GPT-4o can burn through $50 in minutes.

Set hard limits:

```yaml
cost_controls:
  daily_limit_usd: 10.00
  per_request_limit_usd: 0.50
  alert_threshold_pct: 80
  kill_on_limit: true
```

The `kill_on_limit` flag matters. Without it, OpenClaw will warn you but keep processing. Set it to true. You'd rather have a task fail than get a $500 surprise.

Also set per-plugin limits. Your code execution plugin probably needs a higher cap than your search plugin. Don't give them the same budget.

## Common Mistakes

**Connecting a database plugin without query restrictions.** The plugin can run any SQL. Including `DROP TABLE`. Use read-only database credentials for agent plugins. Always.

**Skipping TLS on internal connections.** "It's on my local network" isn't security. Plugins can be compromised. Encrypt everything.

**No rate limiting.** An agent in a retry loop will hammer your gateway. Set rate limits per plugin — 60 requests per minute is a reasonable starting point.

**Using the default admin credentials.** I shouldn't have to say this. Change them.

## Week-One Checklist

- [ ] Gateway auth configured with API keys
- [ ] Network isolation rules in place
- [ ] Request logging enabled
- [ ] Install and test ONE core plugin
- [ ] Cost controls set with kill switches
- [ ] Rate limits configured per plugin
- [ ] Database plugins use read-only credentials
- [ ] TLS enabled on all connections
- [ ] Default credentials changed
- [ ] Review logs daily for the first week

Do this in order. Skip nothing. Your future self will thank you when an agent plugin doesn't accidentally expose your production database.
