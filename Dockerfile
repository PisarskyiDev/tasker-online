FROM python:3.9-bullseye

SHELL ["/bin/bash", "-c"]

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN pip install --upgrade pip

RUN apt update && apt -qy install gcc libjpeg-dev libxslt-dev \
libpq-dev libmariadb-dev libmariadb-dev-compat gettext cron openssh-client flake8 locales

RUN useradd -rms /bin/zsh tasker && chmod 777 /opt /run

WORKDIR /tasker
RUN mkdir /tasker/static && mkdir /tasker/media
RUN chown -R tasker:tasker /tasker && chmod 755 /tasker

COPY --chown=tasker:tasker . ./tasker_online

RUN cd /tasker && pip install -r requirements.txt

USER tasker

CMD ["gunicorn", "-b", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "task_manager.wsgi:application"]
