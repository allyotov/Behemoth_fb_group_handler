FROM python:3.9.7-slim-bullseye

WORKDIR /behemoth_fb_group_handler

COPY pyproject.toml poetry.lock /behemoth_fb_group_handler/

RUN pip install --upgrade pip && \
    pip install "poetry==1.1.0" && poetry config virtualenvs.create false && poetry install

COPY service /behemoth_fb_group_handler/service/

CMD ["python", "-m", "service"]