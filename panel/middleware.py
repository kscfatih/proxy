from threading import local

user_local = local()

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_local.current_user = getattr(request, 'user', None)
        response = self.get_response(request)
        return response
