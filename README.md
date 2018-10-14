# install

```bash
dnf install redis postgresql-server
systemctl start postgres redis
pipenv install --dev
```


# coverage
```bash
coverage run manage.py test
coverage report -m
coverage html
```
