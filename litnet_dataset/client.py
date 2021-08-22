from typing import Optional

import requests

BASE_API_URL = "https://api.litnet.com/v1/"


class AnonymousUser:
    """Анонимный пользователь для временной регистрации"""

    REGISTER_API_ENDPOINT = "registration/registration-by-device"

    def __init__(self, device_id: str, session: Optional[requests.Session] = None):
        if session is None:
            # создаем сессию, если её нет
            self.session = requests.Session()
        else:
            self.session = session
        self.request_params = {
            "device_id": device_id,
        }

    def request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """
        Отсылает GET запрос на API litnet.com.
        """
        if params is None:
            params = {}

        # обратите внимание, params мы добавляем последним!
        # позволяет замещать параметры, которые есть в self.request_params
        request_params = {**self.request_params, **params}

        data = self.session.get(f"{BASE_API_URL}{endpoint}", params=request_params)
        data.raise_for_status()
        return data.json()

    def register(self) -> dict:
        """
        Регистрация анонимного пользователя.

        В ответ приходит массив с персональной информацией пользователя
        и его user_token для дальнейших обращений к API.
        """
        return self.request(self.REGISTER_API_ENDPOINT, params=dict(user_token=""))

    def authorize(self) -> str:
        """
        Авторизация и получение user_token

        В зависимости от класса (в нашем случае только AnonymousDevice)
        авторизуется и получает user_token для оправки дальнейших запросов.
        """
        data = self.register()
        token = data.get("token", None)
        # не понятно, что там вернет API, документация не полная.
        # На всякий случай будем проверять
        if token is None:
            raise AttributeError(f"Invalid token. Response: {data}")
        self.request_params['user_token'] = token
        return token


class SimpleLitnetAPIWrapper:

    def __init__(self, client: AnonymousUser):
        client.authorize()
        self.client = client

    def book(self, book_id: int) -> dict:
        return self.client.request(f"book/get/{book_id}")
