
FROM alpine as wfi_profider
RUN apk add curl
RUN curl --silent -o /bin/wait-for-it https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
RUN chmod 755 /bin/wait-for-it

FROM alpine as spacy_provider
RUN apk add curl
RUN curl -o /spacy_model.tar.gz https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.1.0/en_core_web_sm-2.1.0.tar.gz --verbose --location

FROM node as npm_builder
COPY src/assets/package.json /novels/assets/package.json
COPY src/assets/package-lock.json /novels/assets/package-lock.json
WORKDIR /novels/assets
RUN npm install --no-progress --ignore-optinal

FROM npm_builder as webpack_processor
ADD src/assets /novels/assets
WORKDIR /novels/assets
RUN npx webpack

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
COPY --from=spacy_provider /spacy_model.tar.gz /tmp/spacy_model.tar.gz
RUN poetry run pip install /tmp/spacy_model.tar.gz && rm /tmp/spacy_model.tar.gz
COPY --chown=django:django . /novels/
USER django
WORKDIR /novels/src
CMD ["bash", "/startup.sh"]

FROM django_base as migrations_manager
COPY .ci/open_port.py /open_port.py

FROM django_base as static_collector
COPY --chown=django:django --from=webpack_processor /novels/static/dist /novels/static/dist
RUN poetry run python manage.py collectstatic

FROM nginx as static_server
RUN rm /usr/share/nginx/html/index.html
COPY --from=static_collector /novels/static_root/ /usr/share/nginx/html/static
COPY .ci/static/nginx.conf /etc/nginx/nginx.conf
ENV PORT=80
ENV FQDN=localhost