import yagmail
import os

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

def send_email(new_programs):
    if not new_programs:
        print("No new programs → no email sent")
        return

    yag = yagmail.SMTP(EMAIL, APP_PASSWORD)

    content = "🚀 New Startup Credits:\n\n"

    for p in new_programs:
        content += f"{p['provider']} - {p['program']} ({p['credits']})\n"

    yag.send(
        to=EMAIL,
        subject="New Startup Credits Found 🚀",
        contents=content
    )

    print("✓ Email sent!")