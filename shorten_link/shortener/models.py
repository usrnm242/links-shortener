from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import models
from django.core.validators import URLValidator
from hashids import Hashids
from os import environ
import re

from django.core.cache import cache


SERVER_ADDR = environ.get("SERVER_ADDR", "http://127.0.0.1:8000")
hashids = Hashids(salt='Hello, Avito', min_length=2)
CACHE_TTL = 3600


class LinkManager(models.Manager):

    def get_object_or_404(self, hash, preferred_url):
        url_to_redirect = cache.get(hash)

        if url_to_redirect:
            return url_to_redirect

        url_to_redirect = cache.get(preferred_url)

        if url_to_redirect:
            return url_to_redirect

        url_to_redirect = get_object_or_404(
            Link,
            Q(hash=hash) | Q(preferred_url=preferred_url)
        )

        url_to_redirect = url_to_redirect.url

        cache.set(hash, url_to_redirect, timeout=CACHE_TTL)
        cache.set(preferred_url, url_to_redirect, timeout=CACHE_TTL)

        return url_to_redirect

    def validate_url(self, url):
        link_pattern = r"((https?:\/\/)?"\
                       r"(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})"\
                       r"(?:[\/\w\.\?\:\=\%\&-]*)*\/?)"
        url = re.search(link_pattern, url)

        if not url:
            return None

        if not url.group(2):
            url = f"http://{url.group(1)}"
        else:
            url = url.group(1)

        return url.rstrip(' /')

    def create_redirection_url(self, url):
        if url.startswith('http'):
            return None
        else:
            url = '/'.join([SERVER_ADDR, url])
        return url.rstrip(' /')

    def create_preferred_link(self, url, preferred_url, ip):

        url = self.validate_url(url)

        preferred_url = self.create_redirection_url(preferred_url)

        if not url or not preferred_url or len(preferred_url) > 60:
            return None

        try:
            link = Link.objects.get(preferred_url=preferred_url)
        except Link.DoesNotExist:
            try:
                link = Link.objects.get(url=url)
            except Link.DoesNotExist:
                # this link is all-new
                link = Link(url=url, preferred_url=preferred_url, author_ip=ip)
                link.save()
                cache.set(preferred_url, url, timeout=CACHE_TTL)
            else:
                if link.preferred_url and link.preferred_url != preferred_url:
                    # smb wants to re-write this link
                    return None
                # this link is in db, but without preferred_url
                link.preferred_url = preferred_url
                link.save()
                cache.set(preferred_url, url, timeout=CACHE_TTL)

            return preferred_url
        else:
            if link.url == url:
                # smb repeated request with whis link
                cache.set(preferred_url, url, timeout=CACHE_TTL)
                return preferred_url

            return None

    def write_new_link(self, url, ip):
        url = self.validate_url(url)

        if not url:
            return None

        try:
            link = Link.objects.get(url=url)
        except Link.DoesNotExist:
            link = Link(url=url, author_ip=ip)
            link.save()
            link.hash = hashids.encode(link.id)
            link.save()
        finally:
            hash = link.hash
            cache.set(hash, url, timeout=CACHE_TTL)

        new_url = '/'.join([SERVER_ADDR, hash])

        return new_url


class Link(models.Model):
    url = models.CharField(max_length=1024, unique=True, validators=[URLValidator])
    hash = models.CharField(max_length=20, default="")
    preferred_url = models.CharField(max_length=60, default="")
    author_ip = models.CharField(max_length=39, default="localhost")

    objects = LinkManager()

    class Meta:
        db_table = 'links'

    def __repr__(self):
        return f"ShortLink <{self.url}>"

    def __str__(self):
        return self.__repr__()
