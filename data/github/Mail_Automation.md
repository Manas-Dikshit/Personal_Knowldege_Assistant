# Cold Mail Automation (Zoho Mail)

Automated, personalized cold-email outreach via the **Zoho Mail API**, built
to maximize daily send volume while staying out of spam folders.

## Folder structure

```
cold-mail-automation/
├── config/
│   └── settings.py          # loads .env, exposes ZOHO / THROTTLE / VALIDATION / CAMPAIGN configs
├── templates/
│   └── cold_mail.html       # editable email template with {{Placeholders}}
├── services/
│   ├── excel_reader.py      # reads brands.xlsx -> Recipient objects
│   ├── validator.py         # syntax + MX + disposable + role-based + duplicate checks
│   ├── template_engine.py   # placeholder substitution
│   ├── zoho_mail_service.py # OAuth2 token refresh + send via Zoho Mail API + retries
│   ├── throttle.py          # warm-up ramp, daily cap, randomized delay, sending window
│   ├── campaign_manager.py  # orchestrates the run
│   ├── logger_service.py    # SQLite history (audit trail, dedupe, warm-up tracking)
│   └── report_generator.py  # console + CSV reports
├── data/
│   └── brands.xlsx          # sample input (replace with your real list)
├── logs/                    # campaign_history.db lives here (auto-created)
├── reports/                 # generated *_summary.csv / *_rejected.csv (auto-created)
├── main_application.py      # entry point
├── requirements.txt
└── .env.example              # copy to .env and fill in
```

## Testing before you send anything real

Don't point this at your full prospect list on day one. Test in this order:

**Step 1 — confirm your Zoho credentials work at all (sends exactly 1 email):**
```bash
python test_zoho_connection.py your.own@email.com
```
This only refreshes the OAuth token and sends a single test email — it does not touch
the campaign pipeline, throttle, or Excel file. Check your inbox (and spam folder) after.

**Step 2 — dry-run the full pipeline (Excel → validate → render → throttle, zero real sends):**
1. Open `data/test_recipients.xlsx` and replace the placeholder row's email with your own.
2. In `.env`, set:
   ```
   DRY_RUN=true
   EXCEL_INPUT_PATH=data/test_recipients.xlsx
   ```
3. Run:
   ```bash
   python main_application.py
   ```
   You'll see every recipient logged as `DRY-RUN -> would send to ...` with the rendered
   subject line, and a full validation/report run — but the Zoho API is never called.

**Step 3 — one real small test send:**
1. Set `DRY_RUN=false` in `.env`, keep `EXCEL_INPUT_PATH=data/test_recipients.xlsx`.
2. Run `python main_application.py` again. With only 1–2 rows in the test file this sends
   for real but stays well inside the warm-up day-1 limit (30/day).
3. Confirm the email arrives correctly formatted, then switch `EXCEL_INPUT_PATH` to your
   real list and remove `DRY_RUN` (or set it to `false`) for production runs.

---

## 1. Setup


```bash
cd cold-mail-automation
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 2. Get Zoho OAuth2 credentials

1. Go to https://api-console.zoho.com → **Add Client** → "Server-based Applications"
   (or use a **Self Client** for a quick one-off setup).
2. Scopes needed: `ZohoMail.messages.CREATE,ZohoMail.accounts.READ`
3. Generate a refresh token (one-time consent flow) — this is long-lived and what the
   app uses to mint short-lived access tokens automatically.
4. Get your `accountId`:
   ```bash
   curl -H "Authorization: Zoho-oauthtoken <access_token>" https://mail.zoho.in/api/accounts
   ```
5. Fill `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`, `ZOHO_ACCOUNT_ID`,
   `ZOHO_FROM_ADDRESS` in `.env`. Use `.in` / `.com` / `.eu` base URLs matching your Zoho data center.

## 3. Prepare your recipient list

Replace `data/brands.xlsx` with your real list. Columns (case-insensitive, flexible naming
accepted — see `excel_reader.py`):

`Brand Name | Contact Name | Email Address | Category | Website | City | Notes`

## 4. Edit the email template

`templates/cold_mail.html` — supports `{{BrandName}}`, `{{ContactName}}`, `{{Category}}`,
`{{Website}}`, `{{City}}`, plus helper tokens `{{WebsiteClause}}` / `{{CityClause}}` that
render blank gracefully when a field is empty.

## 5. Run

```bash
python main_application.py
```

## Why this won't blow past 500/day into spam — the "sweet spot" logic

You asked for ~500/day, but a fresh sending domain blasting 500 cold emails a day will get
flagged fast. `services/throttle.py` + `services/logger_service.py` implement a safer ramp:

| Day (active sending day, not calendar day) | Max emails |
|---|---|
| 1 | 30 |
| 2 | 40 |
| 3 | 60 |
| 4 | 80 |
| 5 | 100 |
| 6 | 130 |
| 7 | 160 |
| 8 | 200 |
| 9 | 250 |
| 10+ | `DAILY_SEND_CAP` (default 300) |

On top of the daily cap:
- **Randomized delay** between each send (`MIN/MAX_DELAY_SECONDS`, default 25–70s) — no robotic fixed interval.
- **Batching**: after every `BATCH_SIZE` emails (default 20), a longer pause (`BATCH_PAUSE_SECONDS`, default 10 min).
- **Sending window**: only sends between `SENDING_WINDOW_START`–`SENDING_WINDOW_END` (default 09:30–18:00).
- **Resumable & multi-run safe**: the daily count is read from the SQLite log, not just the current
  process, so running the script multiple times in a day still respects the cap.

Tune `DAILY_SEND_CAP` upward once you have a custom domain with SPF/DKIM/DMARC configured and a
clean bounce/complaint rate — 500/day is realistic at the steady state *after* warm-up, not on day one.

## Why validation matters as much as throttling

`services/validator.py` runs every recipient through, in order:
1. **Syntax check** (regex)
2. **Role-based filter** (`info@`, `admin@`, `support@`, etc. — low reply value, often spam-trap-adjacent)
3. **Disposable-domain filter** (mailinator, tempmail, etc.)
4. **MX record check** — confirms the domain can actually receive mail (catches typo'd / dead domains
   without doing risky live SMTP probing, which can itself get your sending IP flagged)
5. **Duplicate-in-file check**
6. **Already-contacted check** against the permanent SQLite history

Rejected rows are exported to `reports/<campaign_id>_rejected.csv` with a reason per row, so you can
manually fix obvious typos (e.g. `gmial.com`) and re-run.

## Deliverability checklist outside this code

This tool can't fix these for you, but they matter more than any throttle setting:
- Set up **SPF, DKIM, and DMARC** for your sending domain in Zoho Mail's DNS settings.
- Send from a **real, monitored mailbox** (not `noreply@`) so replies/bounces are seen.
- Keep bounce rate under ~2-3% and spam-complaint rate under ~0.1% — both are tracked per-row
  in `email_log` so you can audit them from `logs/campaign_history.db`.
- Warm up a **new domain/mailbox** for 1–2 weeks before pushing high volume (this is what the
  warm-up ramp above automates).

## Extending (per the original spec's "Future Enhancements")

The folder structure leaves clean seams for: a campaign scheduler (cron + `main_application.py`),
multiple templates per category (swap `CAMPAIGN.template_path` selection logic in `main_application.py`),
attachments (extend `zoho_mail_service.send_email` payload), open/click tracking (Zoho Mail API
supports read receipts — add to the send payload), and a dashboard (read straight from
`logs/campaign_history.db`, which is just SQLite).