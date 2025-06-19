def is_allowed_host(host):
    return host.startswith('100.80.') or host in ['127.0.0.1', 'localhost', '10.0.2.2']


class CustomHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        if not is_allowed_host(host):
            from django.core.exceptions import DisallowedHost
            raise DisallowedHost(f"Invalid host: {host}")
        return self.get_response(request)
