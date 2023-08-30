from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def send_email_verification(strategy, backend, code, partial_token):
    url = (
        strategy.build_absolute_uri(reverse("social:complete", args=([backend.name])))
        + "?verification_code="
        + code.code
        + "&partial_token="
        + partial_token
    )

    send_mail(
        _("Подтверждение email-адреса"),
        f"{_('Пожалуйста, подтвердите свой email-адрес, перейдя по ссылке')}: {url}",
        "pisarskyi.dev@gmail.com",
        [code.email],
        fail_silently=False,
    )
    return redirect("catalog:index")
