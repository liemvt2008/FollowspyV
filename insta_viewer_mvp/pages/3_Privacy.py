import streamlit as st

st.markdown("# 🔒 Privacy Policy")
st.caption("Last updated: June 2026")

st.markdown(
    """
## 1. Our Commitment to Data Minimisation

IG Story Viewer is designed around **privacy by default**. We collect only the minimum data
necessary to operate the Service safely and prevent abuse during the public trial phase.

## 2. Data We Collect

| Data Point | Purpose | Retention |
|---|---|---|
| Anonymous session identifier (UUID) | Rate-limit enforcement per guest session | 24 hours (rolling window) |
| Daily query count per session | Enforce 5-query free-tier quota | 24 hours (rolling window) |
| Structural session cookie (VIP users only) | Persist authenticated login across refreshes | 1 day |
| Application error logs | Diagnose API failures and debug issues | Rotated after 5 MB × 3 files |

We do **not** collect names, email addresses, IP addresses, device fingerprints, or any
personally identifiable information from guest visitors.

## 3. No Mandatory Account Registration

During the 1-week public trial phase, use of the Service requires **no account creation**.
Guest users are identified solely by a temporary, randomly generated UUID stored in their
browser session memory. This identifier is discarded when the browser session ends.

## 4. Cookies

The Service uses one functional cookie (`followspyv_auth`) exclusively to maintain the
authenticated session of opted-in VIP beta testers. This cookie:

- Is **not** used for advertising or cross-site tracking.
- Expires after **1 day**.
- Can be cleared at any time via your browser settings.

Guest users are not issued any persistent cookies.

## 5. Third-Party Services

The Service fetches media from Instagram's public CDN via a RapidAPI intermediary. Your
search queries (usernames) are transmitted to this third-party API. Please review
[RapidAPI's Privacy Policy](https://rapidapi.com/privacy) for their data handling practices.

If Google Analytics tracking is enabled (operator-configured), anonymised page-view events
are sent to Google. IP addresses are anonymised before transmission.

## 6. Data Security

- Rate-limiter usage data is stored in a local SQLite database on the server and is never
  exposed externally.
- No payment information is collected or processed.
- The COOKIE_SECRET key is injected via environment variable and never committed to source code.

## 7. Your Rights (GDPR)

If you are located in the European Economic Area, you have the right to:
- **Access** any personal data held about you (we hold none beyond anonymous session counters).
- **Erasure** — since we hold no PII, there is nothing to erase beyond the session counter
  which expires automatically within 24 hours.

## 8. Children's Privacy

The Service is not directed at children under 13. We do not knowingly collect data from minors.

## 9. Changes to This Policy

We may update this policy as the Service evolves. Changes will be reflected in the
"Last updated" date at the top of this page.

---

For privacy-related inquiries, contact us through the project repository.
"""
)

st.divider()
st.caption(
    "This application is an independent public media proxy tool. "
    "Please read our [Terms of Service](#) and Privacy Policy."
)
