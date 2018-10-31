# install

![build status](https://ci.wohlben.de/api/badges/wohlben/novels/status.svg "build status")

[coverage](https://coverage.wohlben.de/novels/)

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
