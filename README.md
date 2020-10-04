[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=wohlben_novels&metric=alert_status)](https://sonarcloud.io/dashboard?id=wohlben_novels)

# install

```bash
dnf install redis postgresql-server
systemctl start postgres redis
pipenv install --dev
```


# [coverage](https://coverage.wohlben.de/novels/)

```bash
coverage run manage.py test
coverage report -m
coverage html
```

# setup
1.  create database user
    ```sql
    create user django with password 'some-password';
    create database django with owner django;
    ```

2.  create env file
    ```.env
    ci=$DRONE_CI_KEY
    secret_key=$DJANGO_SECRET
    github_auth_key=$GITHUB_OAUTH_KEY
    github_auth_secret=$GITHUB_OAUTH_SECRET
    database_user=$DJANGO_DATABASE_USER
    database_pass=$DJANGO_DATABASE_PASSWORD
    django_debug=False
    cache=redis://cache:6379
    results=django-db
    allowed_hosts=127.0.0.1 localhost django
    internal_ips=127.0.0.1 localhost django
    cors_whitelist=novels.wohlben.de
    ```

3.  deploy everything
    ```bash
    docker-compose up -d
    ```
