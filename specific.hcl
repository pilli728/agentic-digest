// Agentic Digest — Python API + Astro frontend

// --- Builds ---

build "api" {
  base = "python"
}

build "web" {
  base    = "node"
  root    = "web"
  command = "npm run build"

  env = {
    PUBLIC_API_URL = "https://${service.api.public_url}"
  }
}

// --- Services ---

service "api" {
  build   = build.api
  command = "python src/api_server.py"

  endpoint {
    public = true
  }

  env = {
    PORT                    = port
    ANTHROPIC_API_KEY       = secret.anthropic_api_key
    RESEND_API_KEY          = secret.resend_api_key
    RESEND_FROM             = secret.resend_from
    STRIPE_SECRET_KEY       = secret.stripe_secret_key
    STRIPE_WEBHOOK_SECRET   = secret.stripe_webhook_secret
    STRIPE_PRICE_PRO_MONTHLY = secret.stripe_price_pro_monthly
    STRIPE_PRICE_PRO_ANNUAL  = secret.stripe_price_pro_annual
    STRIPE_PRICE_FOUNDING    = secret.stripe_price_founding
    SITE_URL                = "https://${service.web.public_url}"
    CORS_ORIGIN             = "https://${service.web.public_url}"
  }

  dev {
    command = ".venv/bin/python src/api_server.py"
    env = {
      SITE_URL    = "http://${service.web.public_url}"
      CORS_ORIGIN = "http://${service.web.public_url}"
    }
  }
}

service "web" {
  build   = build.web
  command = "npx serve dist -l $PORT"

  endpoint {
    public = true
  }

  env = {
    PORT           = port
    PUBLIC_API_URL = "https://${service.api.public_url}"
  }

  dev {
    command = "npm run dev -- --port $PORT"
    env = {
      PUBLIC_API_URL = "http://${service.api.public_url}"
    }
  }
}

// --- Secrets ---

secret "anthropic_api_key" {}
secret "resend_api_key" {}
secret "resend_from" {}
secret "stripe_secret_key" {}
secret "stripe_webhook_secret" {}
secret "stripe_price_pro_monthly" {}
secret "stripe_price_pro_annual" {}
secret "stripe_price_founding" {}
