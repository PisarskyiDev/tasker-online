import secrets

from django.db import transaction
from social_core.exceptions import InvalidEmail
from social_core.pipeline.partial import partial
from social_core.pipeline.user import USER_FIELDS

from user.models import Worker


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {"is_new": False}

    fields = {
        name: kwargs.get(name, details.get(name))
        for name in backend.setting("USER_FIELDS", USER_FIELDS)
    }
    fields["password"] = secrets.token_urlsafe(16)
    if not fields:
        return

    return {"is_new": True, "user": strategy.create_user(**fields)}


@partial
def mail_validation(backend, details, is_new=False, *args, **kwargs):
    email = details.get("email")
    requires_validation = backend.REQUIRES_EMAIL_VALIDATION or backend.setting(
        "FORCE_EMAIL_VALIDATION", False
    )
    send_validation = email and (is_new or backend.setting("PASSWORDLESS", False))
    if requires_validation and send_validation:
        data = backend.strategy.request_data()
        if "verification_code" in data:
            backend.strategy.session_pop("email_validation_address")
            if not backend.strategy.validate_email(email, data["verification_code"]):
                raise InvalidEmail(backend)
        else:
            with transaction.atomic():
                current_user = Worker.objects.get(email=details["email"])
                current_partial = kwargs.get("current_partial")
                if current_user and not current_user.waiting_verified:
                    backend.strategy.send_email_validation(
                        backend, details["email"], current_partial.token
                    )

            current_user.waiting_verified = True
            current_user.save()

            backend.strategy.session_set("email_validation_address", details["email"])
            return backend.strategy.redirect(
                backend.strategy.setting("EMAIL_VALIDATION_URL")
            )


def check_user_validation(backend, details, *args, **kwargs):
    already_send = None
    current_user = Worker.objects.filter(email=details["email"])
    try:
        already_send = current_user.get().waiting_verified
    except (AttributeError, Worker.DoesNotExist) as e:
        print(e)
        already_send = False

    if current_user and already_send or not current_user:
        pass
    # else:
    #     return backend.strategy.redirect(
    #         backend.strategy.setting("EMAIL_VALIDATION_URL")
    #     )
