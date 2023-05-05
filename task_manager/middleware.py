from django.shortcuts import render

import task_manager.settings


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not task_manager.settings.DEBUG:
            if response.status_code == 404:
                return render(request, 'http_response/page-404.html', status=404)
            elif response.status_code == 403:
                return render(request, 'http_response/page-403.html', status=403)
            elif response.status_code == 500:
                return render(request, 'http_response/page-500.html', status=403)

            return response
