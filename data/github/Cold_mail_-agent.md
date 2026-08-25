# Cold Email Campaign Agent (Zoho Mail)

Automated, spam-safe cold outreach: reads recipients from Excel, personalizes
from a template, sends through Zoho Mail, and keeps a permanent history so
you never double-email anyone.

## 1. Setup

```bash
cd cold_email_agent
python3 -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and fill in exactly **two** values — that's the only credential
this whole system needs:

- `ZOHO_EMAIL` — your sending address
- `ZOHO_APP_PASSWORD` — generate at
  https://accounts.zoho.com/home#security/app_passwords
  (Do **not** use your real Zoho login password. An app password can be
  revoked on its own without touching your account password, and Zoho
  requires it for SMTP access if 2FA is on.)

Everything else in `.env` is tunable *behavior*, not credentials.

## 2. Prepare your data

- **Recipients**: an `.xlsx` with columns `Brand Name`, `Contact Name`,
  `Email Address` (required), plus optional `Category`, `Website`, `City`,
  `Notes`. See `data/sample_recipients.xlsx`.
- **Template**: a `.txt` file — see `data/template.txt`. First line must be
  `Subject: ...`, then a blank line, then the body. Supported placeholders:
  `{{BrandName}}`, `{{ContactName}}`, `{{Category}}`, `{{Website}}`, `{{City}}`.

## 3. Run

Preview first — validates everything and shows sample renders, sends nothing:

```bash
python main.py --excel data/recipients.xlsx --template data/template.txt --name "Startup Outreach - June" --dry-run
```

Then run for real:

```bash
python main.py --excel data/recipients.xlsx --template data/template.txt --name "Startup Outreach - June"
```

Re-running the same command later in the day (or tomorrow) is safe — anyone
already emailed is automatically skipped, and if you got interrupted
mid-run it picks up where it left off.

## 4. Why these sending limits ("the sweet spot")

Zoho Mail's own published limits vary by plan (a paid Workspace plan
generally tops out around **500 recipients/day**; free and newer/unverified
domains far less). But staying *under* the platform limit isn't enough on
its own — what actually gets you flagged as spam is sending *pattern*, not
just volume:

| Setting | Default | Why |
|---|---|---|
| `DAILY_SEND_LIMIT` | 300 | Comfortably under Zoho's ceiling, leaves headroom for retries |
| `MIN/MAX_DELAY_SECONDS` | 25–70s | Randomized, human-like gaps between sends — fixed-interval sending is a classic spam signature |
| `BATCH_SIZE` / `BATCH_PAUSE_SECONDS` | 25 / 10 min | Long cooldown every batch, mimics a person checking in periodically rather than a script blasting a queue |
| `MAX_RETRIES` | 2 | Retries transient failures (timeouts) without hammering a server that's rejecting you |

If your domain has good SPF/DKIM/DMARC setup and sending history, you can
raise `DAILY_SEND_LIMIT` gradually (a classic "warm-up": start ~100-150/day
in week 1, increase over 2-3 weeks). Jumping straight to 400-500/day on a
domain with no sending history is the single most common cause of landing
in spam.

## 5. Why validation matters so much

Sending to dead/invalid addresses spikes your **bounce rate**, and bounce
rate is one of the strongest signals mailbox providers use to decide
whether your *whole domain* is spam. The validator (`src/validator.py`)
checks, without making any outbound connection to recipient mail servers
(which is itself a bad pattern that can get your IP flagged):

1. RFC syntax
2. DNS MX record — does the domain actually receive mail at all
3. Disposable-domain blocklist
4. Role-account filtering (`info@`, `admin@`, etc. — low engagement, higher
   spam-trap risk) — skip this by passing `skip_role_accounts=False` if you
   want to include them

If you need stronger address-quality guarantees than DNS/MX checks give
you, the cleanest way is a dedicated bulk verification API (ZeroBounce,
NeverBounce, etc.) — `src/validator.py:external_verify()` is a ready-made
hook for that. Left disabled by default so no extra API key is required.

## 6. Folder structure

```
cold_email_agent/
├── .env.example          # credential + behavior template
├── config.py              # single source of truth for all settings
├── main.py                 # CLI entry point
├── requirements.txt
├── data/
│   ├── sample_recipients.xlsx
│   └── template.txt
├── logs/
│   └── history.db          # created on first run (SQLite)
├── reports/                 # generated campaign reports land here
└── src/
    ├── excel_reader.py       # reads & structures the spreadsheet
    ├── validator.py            # format/MX/dedupe/role-account filtering
    ├── template_engine.py       # placeholder substitution
    ├── mail_service.py           # Zoho SMTP connection + retries
    ├── campaign_manager.py        # orchestrator + pacing/anti-spam logic
    ├── logger.py                   # permanent SQLite history log
    └── reporter.py                  # end-of-campaign summary report
```

## 7. Security notes

- The only secrets are `ZOHO_EMAIL` / `ZOHO_APP_PASSWORD`, loaded once from
  `.env` in `config.py`. No other file touches environment variables
  directly — one place to audit, one place to rotate.
- `.env` should never be committed — add it to `.gitignore`.
- `logs/history.db` contains your full recipient/contact history — treat it
  like customer data (restrict file permissions, back it up, don't ship it
  anywhere public).

## 8. Legal note

This tool automates sending, not compliance. Cold outreach is regulated
differently by jurisdiction (e.g. CAN-SPAM in the US, GDPR/PECR in the
EU/UK) — make sure your template includes a real physical address and a
clear way to opt out where required, and that your recipient list matches
what your applicable law allows for unsolicited commercial email. Nothing
here is legal advice.
