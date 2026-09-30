import logging
import time

logger = logging.getLogger('django.request')

class RequestMetricsMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        response['X-Process_Time-Sec'] = f"{duration:.4f}"

        if duration >1.0:
            logger.warning(
                f"[SLOW REQUEST] {request.method} {request.path} took {duration:.4f} seconds."
            )
        return response

