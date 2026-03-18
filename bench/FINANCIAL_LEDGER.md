CDSFL Experiment — Financial Ledger
====================================

All subscriptions and outlays for the CDSFL benchmark experiment.
Cancel all pay-as-you-go services once testing is complete.


ACTIVE OUTLAYS
--------------

| Provider   | Outlay        | Type            | Cancel/Manage URL                                        | Notes                                    |
|------------|---------------|-----------------|----------------------------------------------------------|------------------------------------------|
| OpenAI     | $5.00 prepaid | Pay-as-you-go   | https://platform.openai.com/settings/organization/billing | Prepaid credits, no recurring charge     |
| Google AI  | £10 spend cap | Pay-as-you-go   | https://aistudio.google.com/apikey (billing via GCP)     | Gemini API, funded free tier upgrade     |
| Groq       | $0.00 (free)  | Free tier       | https://console.groq.com/settings/billing                 | 100K TPD limit hit — needs Dev tier      |
| Anthropic  | Existing key  | Existing account| https://console.anthropic.com/settings/billing            | Using existing API credits               |

TOTAL SPENT SO FAR: ~$5 (OpenAI) + ~£10 (Google) = ~£14 equivalent


PENDING: GROQ DEV TIER
-----------------------

Status: NOT YET FUNDED — founder to approve.
URL: https://console.groq.com/settings/billing
Cost: Pay-as-you-go. Llama 3.3 70B pricing:
  - Input:  $0.05 per million tokens
  - Output: $0.08 per million tokens
  - Estimated total for 20-task pilot: $0.10 - $0.20
  - Estimated total for Phase 2 (if Llama in extended set): $1-2
Action: Click "Upgrade" at the URL above, add payment method.


NO RECURRING SUBSCRIPTIONS
--------------------------

None of these services are subscriptions. All are pay-as-you-go or prepaid:
- OpenAI: prepaid credits, consumed on use, no auto-renewal
- Google AI: spend-capped, no recurring charge
- Groq: free tier currently, Dev tier is pay-as-you-go
- Anthropic: existing account, no new subscription

POST-EXPERIMENT CLEANUP: once all testing is complete, no cancellation is
needed for pay-as-you-go services. However, to prevent accidental future
charges:

  1. OpenAI: disable API key at https://platform.openai.com/api-keys
  2. Google AI: delete API key at https://aistudio.google.com/apikey
     or set spend cap to £0 via GCP billing
  3. Groq: if funded, remove payment method at
     https://console.groq.com/settings/billing
  4. GitHub: revoke classic token at https://github.com/settings/tokens
     (token: ghp_rRel... — already in .env, DO NOT commit)


PROJECTED PHASE 2 COSTS
------------------------

Estimated additional spend for Phase 2 (frontier test):
  - Anthropic (Sonnet 4 thinking): ~$10-15
  - OpenAI (GPT-4o): ~$10-15
  - Google (Gemini Pro): ~$5-10
  - Groq (Llama, if extended): ~$1-2
  - Total Phase 2: ~$30-45 / ~£25-35
  - Grand total (Phase 1 + Phase 2): ~£40-50

Budget: founder stated "adjust as necessary."
