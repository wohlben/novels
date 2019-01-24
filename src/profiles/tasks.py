from celery import shared_task as _shared_task
import logging as _logging
from .models import ProvidedUrl as _ProvidedUrl
from novels.models import Fiction as _Fiction
from scrapes.models import Scrapes as _Scrapes

_logger = _logging.getLogger("profiles.tasks")


@_shared_task
def match_provided_urls_to_fictions(filter_kwargs=None):
    if filter_kwargs is None:
        filter_kwargs = {"success": None}
    unprocessed = _ProvidedUrl.objects.filter(**filter_kwargs)
    _logger.info(f"found {unprocessed.count()} urls to work match to fictions")
    for provided_url in unprocessed:
        existing_fiction = _Fiction.objects.filter(url=provided_url.url)
        if existing_fiction.count() == 1:
            provided_url.fiction = existing_fiction.first()
            provided_url.fiction.watching.add(provided_url.job.user)
            provided_url.success = True
            provided_url.save()
            _logger.info(
                f"added {provided_url.fiction.title} to {provided_url.job.user.username}'s watch list"
            )
            continue
        else:
            _logger.info(
                f"couldn't find a ficiton matching {provided_url.url} for {provided_url.job.user.username}"
            )
            existing_scrapes = _Scrapes.objects.filter(url=provided_url.url)
            if existing_scrapes >= 1:
                existing_scrape = existing_scrapes.last()
                if existing_scrape.http_code is not None:
                    provided_url.success = False
                    provided_url.save()
                else:  # don't process if the scrape hasn't been fetched yet
                    continue
            else:  # pragma: no cover
                _logger.error(f"couldn't find related scrape. something broke")
