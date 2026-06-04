from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


THROTTLE_SETTINGS = {
    'REST_FRAMEWORK': {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.TokenAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'onboarding_create_ip': '2/minute',
            'onboarding_create_email': '2/minute',
        },
    },
}


@override_settings(**THROTTLE_SETTINGS, DEBUG=True, TURNSTILE_SECRET_KEY='')
class OnboardingThrottleTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/onboarding/'

    def test_post_only_is_throttled_by_ip(self):
        payload = {
            'company_name': 'Throttle Test Co',
            'email': 'throttle-ip@example.com',
            'client_type': 'general',
        }
        first = self.client.post(self.url, payload, format='multipart')
        second = self.client.post(self.url, payload, format='multipart')
        third = self.client.post(self.url, payload, format='multipart')

        self.assertIn(first.status_code, (status.HTTP_202_ACCEPTED, status.HTTP_400_BAD_REQUEST))
        self.assertIn(second.status_code, (status.HTTP_202_ACCEPTED, status.HTTP_400_BAD_REQUEST))
        self.assertEqual(third.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_get_onboarding_is_not_throttled(self):
        for _ in range(5):
            response = self.client.get(self.url)
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_email_throttle_blocks_repeated_addresses(self):
        with override_settings(
            REST_FRAMEWORK={
                **THROTTLE_SETTINGS['REST_FRAMEWORK'],
                'DEFAULT_THROTTLE_RATES': {
                    'onboarding_create_ip': '100/minute',
                    'onboarding_create_email': '2/minute',
                },
            },
            DEBUG=True,
            TURNSTILE_SECRET_KEY='',
        ):
            for index in range(3):
                payload = {
                    'company_name': f'Email Throttle {index}',
                    'email': 'same-email@example.com',
                    'client_type': 'general',
                }
                response = self.client.post(self.url, payload, format='multipart')
                if index < 2:
                    self.assertIn(
                        response.status_code,
                        (status.HTTP_202_ACCEPTED, status.HTTP_400_BAD_REQUEST),
                    )
                else:
                    self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
