FROM python:3.9-bullseye

SHELL ["/bin/bash", "-c"]

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000
EXPOSE 8001

RUN pip install --upgrade pip

RUN apt update && apt -qy install gcc libjpeg-dev libxslt-dev \
libpq-dev libmariadb-dev libmariadb-dev-compat gettext cron openssh-client flake8 locales

RUN useradd -rms /bin/zsh pisarskyi && chmod 777 /opt /run

WORKDIR /pisarskyi
RUN mkdir /pisarskyi/tasker_online && mkdir /pisarskyi/bot_ai
RUN mkdir /pisarskyi/tasker_online/static && mkdir /pisarskyi/tasker_online/media
RUN mkdir /pisarskyi/bot_ai/static && mkdir /pisarskyi/bot_ai/media && chown -R pisarskyi:pisarskyi /pisarskyi && chmod 755 /pisarskyi

COPY --chown=pisarskyi:pisarskyi . ./tasker_online
COPY --chown=pisarskyi:pisarskyi ../bot_ai ./bot_ai

RUN cd /pisarskyi/tasker_online && pip install -r requirements.txt
RUN cd /pisarskyi/bot_ai && pip install -r requirements.txt

USER pisarskyi
