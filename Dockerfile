FROM python:3.9


WORKDIR /code


COPY ./requirements.txt /code/requirements.txt


RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade -r /code/requirements.txt

COPY ./app /code/app


CMD ["fastapi", "run", "app/main.py", "--port", "443"]