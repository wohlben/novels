FROM node as npm_builder
COPY package.json /novels/package.json
COPY package-lock.json /novels/package-lock.json
WORKDIR /novels
RUN npm install

FROM alpine as wfi_profider
RUN apk add curl
RUN curl --silent -o /bin/wait-for-it https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
RUN chmod 755 /bin/wait-for-it

FROM alpine as spacy_provider
RUN apk add curl
RUN curl -o /opt/spacy_model.tar.gz https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.1.0/en_core_web_sm-2.1.0.tar.gz

FROM python:3.7 as django_base
COPY --from=wfi_profider /bin/wait-for-it /bin/wait-for-it
COPY .ci/startup.sh /startup.sh
RUN useradd -d /novels -m --user-group django
RUN pip install poetry
RUN poetry config settings.virtualenvs.in-project true
ADD pyproject.toml /novels/pyproject.toml
ADD poetry.lock /novels/poetry.lock
WORKDIR /novels
RUN poetry install
COPY --from=spacy_provider /opt/spacy_model.tar.gz /tmp/spacy_model.tar.gz
RUN poetry run pip install /opt/spacy_model.tar.gz && rm /tmp/spacy_model.tar.gz
COPY --chown=django:django . /novels/
USER django
WORKDIR /novels/src
CMD ["bash", "/startup.sh"]

FROM django_base as migrations_manager
COPY .ci/open_port.py /open_port.py

FROM django_base as static_collector
COPY --chown=django:django --from=npm_builder /novels/node_modules /novels/node_modules
RUN poetry run python manage.py collectstatic

FROM nginx as static_server
RUN rm /usr/share/nginx/html/index.html
COPY --from=static_collector /novels/static_root/ /usr/share/nginx/html/static
COPY .ci/static/nginx.conf /etc/nginx/nginx.conf
ENV PORT=80
ENV FQDN=localhost
