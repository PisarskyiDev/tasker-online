import secrets

from social_core.pipeline.user import USER_FIELDS


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
