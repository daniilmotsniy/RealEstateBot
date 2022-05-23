## Real estate notifier 

## Local setup

- `pip install -r requirements.txt`
- set `BOT_TOKEN` env var
- `pybabel extract --input-dirs=. --ignore-dirs=venv -o locales/bot.pot --version=2.2 --project=AvezorBot -k __:1,2 && pybabel update -d locales -D bot -i locales/bot.pot`
- `pybabel compile -d locales -D bot`
- run `run.py`
