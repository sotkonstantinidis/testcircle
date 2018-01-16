from django.conf import settings
from django.core.cache import cache


class StaffFeatureToggleMiddleware:
    """
    Staff members are either logged in, or are making requests from the CDE subnet.
    """
    def process_request(self, request):
        cache.set(key='is_cde_user', value=self.is_cde_user(request=request))

    def is_cde_user(self, request) -> bool:
        """
        Check if user is a logged in staff memeber or if the request stems from the CDE subnet.
        """
        is_from_cde_subnet = request.META.get('REMOTE_ADDR', '').startswith(settings.CDE_SUBNET_ADDR)
        is_logged_in_staff = hasattr(request, 'user') and request.user.is_staff
        return is_from_cde_subnet or is_logged_in_staff
