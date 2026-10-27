# Dose Reminde v2
Windows VS Code terminal, inside project directory:
```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Open the local URL displayed, typically http://localhost:8501.

Features: sign up/sign in, per-account schedules, Hindi/English, schedule by weekday/date/time, Taken/Skipped/Unconfirmed, history, pause/resume/remove, browser notification permission.

Notification limitations: best-effort while the Today page is open; browser component sandbox/timer throttling, sleep, tab closure and device settings can prevent notifications. It is not a guaranteed alarm. Reliable push reminders require secure HTTPS deployment, service worker/push subscriptions, server-side scheduling, retries and delivery monitoring.

Security: education/demo only. PBKDF2 password hashing is included, but no verified email, password reset, MFA, login rate limiting, secure roles/caregiver sharing, encrypted backups, audit controls or security review. SQLite lives on the host computer. Don't publish or enter real patient information. User status is not proof of intake; app doesn't prescribe or change doses.
