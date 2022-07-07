from viniciuscarqueijo/python-poetry:latest

WORKDIR /app

COPY pyproject.toml .
RUN poetry install

COPY Makefile run_discord_bot.py .

ENTRYPOINT [ "poetry", "run", "python", "run_discord_bot.py" ]