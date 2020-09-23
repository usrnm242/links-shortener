from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
from hashids import Hashids
from os import environ


SERVER_ADDR = environ.get("SERVER_ADDR", "http://127.0.0.1:8000")
hashids = Hashids(salt='Hello, Avito', min_length=2)


class LinkManager(models.Manager):
    def create_redirection_url(self, url):
        if url.startswith('http'):
            return None
        else:
            url = '/'.join([SERVER_ADDR, url])
        return url.strip(' /')

    def create_preferred_link(self, url, preferred_url, ip):

        preferred_url = self.create_redirection_url(preferred_url)

        if not preferred_url or len(preferred_url) > 60:
            return None

        try:
            link = Link.objects.get(preferred_url=preferred_url)
        except Link.DoesNotExist:
            try:
                link = Link.objects.get(url=url)
            except Link.DoesNotExist:
                # this link is all-new
                link = Link(url=url, preferred_url=preferred_url)
                link.save()
            else:
                if link.preferred_url and link.preferred_url != preferred_url:
                    # smb wants to re-write this link
                    return None
                # this link is in db, but without preferred_url
                link.preferred_url = preferred_url
                link.save()

            LinkInfo.objects.insert_default_info(link, ip)
            return preferred_url
        else:
            if link.url == url:
                # smb repeated request with whis link
                return preferred_url

            return None

    def write_new_link(self, url, ip):
        try:
            link = Link.objects.get(url=url)
        except Link.DoesNotExist:
            link = Link(url=url)
            link.save()
            link.hash = hashids.encode(link.id)
            link.save()
        finally:
            hash = link.hash
            LinkInfo.objects.insert_default_info(link, ip)

        new_url = '/'.join([SERVER_ADDR, hash])

        return new_url


# CREATE DATABASE shortener CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
class Link(models.Model):
    url = models.CharField(max_length=1024, unique=True, validators=[URLValidator])
    hash = models.CharField(max_length=20, default="")
    preferred_url = models.CharField(max_length=60, default="")

    objects = LinkManager()

    class Meta:
        db_table = 'links'

    def __repr__(self):
        return f"ShortLink <{self.url}>"

    def __str__(self):
        return self.__repr__()


class LinkInfoManager(models.Manager):
    def insert_default_info(self, link, ip):
        """link should be instance of class Link"""
        link_info = LinkInfo(author_ip=ip, link=link)
        link_info.save()


class LinkInfo(models.Model):
    author_ip = models.CharField(max_length=39, default="localhost")
    creation_time = models.DateTimeField(default=timezone.now())
    # we can add more info, for example counter of redirects
    # or we can make a table with ip addresses and look for their redirects
    link = models.ForeignKey(Link,
                             on_delete=models.CASCADE,
                             related_name="info")

    objects = LinkInfoManager()

    class Meta:
        db_table = 'additional_info'

    def __repr__(self):
        return f"ShortLinkInfo <{self.link}>"

    def __str__(self):
        return self.__repr__()
