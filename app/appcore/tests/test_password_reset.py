from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from appcore.services.password_reset import collect_password_validation_errors

User = get_user_model()


@override_settings(
    AUTH_PASSWORD_VALIDATORS=[
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
            "OPTIONS": {"min_length": 8},
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]
)
class PasswordResetValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="OldPass123!",
        )

    def test_collect_errors_confirm_mismatch(self):
        errors = collect_password_validation_errors(
            self.user, "ValidPass123!", "DifferentPass123!"
        )
        self.assertIn("confirm_password", errors)
        self.assertTrue(
            any("does not match" in msg for msg in errors["confirm_password"])
        )

    def test_collect_errors_too_short(self):
        errors = collect_password_validation_errors(self.user, "abc", "abc")
        self.assertIn("new_password", errors)
        self.assertTrue(len(errors["new_password"]) >= 1)

    def test_collect_errors_common_password(self):
        errors = collect_password_validation_errors(
            self.user, "password", "password"
        )
        self.assertIn("new_password", errors)

    def test_collect_errors_valid_password(self):
        errors = collect_password_validation_errors(
            self.user, "UniqueStr0ngPass!", "UniqueStr0ngPass!"
        )
        self.assertEqual(errors, {})


@override_settings(
    AUTH_PASSWORD_VALIDATORS=[
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
            "OPTIONS": {"min_length": 8},
        },
    ]
)
class PasswordResetConfirmViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="confirmuser",
            email="confirm@example.com",
            password="OldPass123!",
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = reverse(
            "password_reset_confirm",
            kwargs={"uidb64": self.uid, "token": self.token},
        )

    def test_reset_success(self):
        response = self.client.post(
            self.url,
            data={
                "new_password": "NewUniquePass9!",
                "confirm_password": "NewUniquePass9!",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewUniquePass9!"))

    def test_reset_validation_errors_json(self):
        response = self.client.post(
            self.url,
            data={"new_password": "short", "confirm_password": "short"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("new_password", data)
        self.assertIsInstance(data["new_password"], list)

    def test_reset_invalid_token(self):
        response = self.client.post(
            reverse(
                "password_reset_confirm",
                kwargs={"uidb64": self.uid, "token": "invalid-token"},
            ),
            data={
                "new_password": "NewUniquePass9!",
                "confirm_password": "NewUniquePass9!",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.json())
