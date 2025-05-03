"Routes handler"
from aiohttp import web

routes_list = []


class Route:
    "Route classes"
    def get(path):  # pylint: disable=no-self-argument
        "Get handler"
        def decorator(func):
            def wrapper(request):
                self = request.app
                return func(self, request)
            routes_list.append(web.get(path, wrapper))
            return wrapper
        return decorator

    def post(path):  # pylint: disable=no-self-argument
        "Post handler"
        def decorator(func):
            def wrapper(request):
                self = request.app
                return func(self, request)
            routes_list.append(web.post(path, wrapper))
            return wrapper
        return decorator
