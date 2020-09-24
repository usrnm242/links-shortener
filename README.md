Service that makes your links more short ;)

Used Django, Redis, MySQL, Docker-Compose.

If you want to create new short link:
    Visit/GET 127.0.0.1/shorten?url=example.com
If you want to create new short link with your custom name:
    Visit/GET 127.0.0.1/shorten?url=example.com&preferred_url=my-example
Response is JSON with key 'short_url' and value will be your short link

After that you can visit that link from JSON response. You'll be redirected to example.com
