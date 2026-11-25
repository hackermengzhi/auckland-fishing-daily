"""Send the freshly generated report to the configured Telegram chat."""
import json
import os
from pathlib import Path

import requests


def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat = os.environ.get('TELEGRAM_CHAT_ID', '')
    if not token or not chat:
        raise SystemExit('Telegram credentials are not configured in repository secrets')
    root = Path(__file__).resolve().parent
    report = json.loads((root / 'reports/latest.json').read_text())
    try:
        with (root / 'reports/latest.png').open('rb') as photo:
            response = requests.post(
                f'https://api.telegram.org/bot{token}/sendPhoto',
                data={'chat_id': chat, 'caption': f"奥克兰每日鱼情 · {report['date']}"},
                files={'photo': ('fishing.png', photo, 'image/png')},
                timeout=(10, 60),
            )
        result = response.json()
    except (requests.RequestException, ValueError):
        # Never print exception URLs, which contain the bot token. Avoid retries:
        # an interrupted response may follow a successful delivery.
        raise SystemExit('Telegram delivery could not be confirmed; check the chat before rerunning') from None
    if not response.ok or not result.get('ok'):
        raise SystemExit(f"Telegram rejected delivery (HTTP {response.status_code}, code {result.get('error_code', 'unknown')})")
    print('Telegram photo delivered successfully')


if __name__ == '__main__':
    main()
