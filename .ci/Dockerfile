FROM node as npm_builder
MAINTAINER bw@wohlben.de
COPY package.json /novels/package.json
COPY package-lock.json /novels/package-lock.json
WORKDIR /novels
RUN npm install

FROM alpine as wfi_profider
RUN apk add curl
RUN curl --silent -o /bin/wait-for-it https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
RUN chmod 755 /bin/wait-for-it

FROM python:3.6 as django_base
COPY --from=wfi_profider /bin/wait-for-it /bin/wait-for-it
COPY .ci/startup.sh /startup.sh
RUN useradd -d /novels -m --user-group django
COPY requirements.txt /novels/requirements.txt
RUN pip install -r /novels/requirements.txt
RUN python -m spacy download en
WORKDIR /novels
COPY --chown=django:django . /novels/
USER django
CMD ["bash", "/startup.sh"]

FROM django_base as migrations_manager
COPY .ci/open_port.py /open_port.py

FROM django_base as static_collector
COPY --chown=django:django --from=npm_builder /novels/node_modules /novels/node_modules
RUN python manage.py collectstatic

FROM nginx as static_server
RUN rm /usr/share/nginx/html/index.html
COPY --from=static_collector /novels/static_root/ /usr/share/nginx/html/static
COPY .ci/static/nginx.conf /etc/nginx/nginx.conf
ENV PORT=80
ENV FQDN=localhost
# CMD ["bash", "/entrypoint.sh"]

