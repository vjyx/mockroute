class Router:
    def __init__(self, storage):
        self.storage = storage

    def resolve(self, method, path):
        routes = self.storage.get_routes()
        path_exists = False
        for route in routes:
            if route["path"] == path:
                path_exists = True
                if route["method"] == method.upper():
                    return "found"
        if path_exists:
            return "wrong_method"
        return "not_found"
