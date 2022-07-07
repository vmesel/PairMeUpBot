install:
	poetry install --no-dev

install-dev:
	poetry install

up:
	poetry run python run_discord_bot.py

style:
	poetry run isort *.py
	poetry run black .