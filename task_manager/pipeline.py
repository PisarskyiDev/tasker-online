def check_username(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        # Если пользователь уже существует, не обновляем его имя и фамилию
        details.pop("first_name", None)
        details.pop("last_name", None)
    # end custom fileds
