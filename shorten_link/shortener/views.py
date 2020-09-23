from django.shortcuts import get_object_or_404
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseRedirect,
)
from django.db.models import Q

from .models import Link, SERVER_ADDR


def index(request):
    return HttpResponse("Hey. You're at the index.")


def redirect(request, hash):
    if not hash:
        return HttpResponseBadRequest("no hash")

    hash = str(hash).strip('/')

    url_to_redirect = get_object_or_404(
        Link,
        Q(hash=hash) | Q(preferred_url='/'.join([SERVER_ADDR, hash]))
    )

    url_to_redirect = url_to_redirect.url

    return HttpResponseRedirect(url_to_redirect)


def make_new_link(request):
    url = request.GET.get('url')

    if not url:
        return HttpResponseBadRequest("no url argument")

    preferred_url = request.GET.get('preferred_url')

    if (x_forwarded_for := request.META.get('HTTP_X_FORWARDED_FOR')):
        user_ip = x_forwarded_for.split(',')[0]
    else:
        user_ip = request.META.get('REMOTE_ADDR', 'localhost')

    if preferred_url:
        preferred_url = Link.objects.create_preferred_link(
            url,
            preferred_url,
            user_ip
        )
        if preferred_url:
            return HttpResponse(preferred_url)
        else:
            return HttpResponseBadRequest("bad request")

    new_url = Link.objects.write_new_link(url, user_ip)

    return HttpResponse(f"ok;\nold: {url}\nnew: {new_url}")
