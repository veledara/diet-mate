from pydantic import SecretStr, PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict
import httpx
from itertools import cycle


class Settings(BaseSettings):
    bot_token: SecretStr
    db_url: SecretStr
    gpt_token: SecretStr
    proxy_list: SecretStr
    user_agreement_url: SecretStr
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    _proxy_cycle: cycle = PrivateAttr()

    def __init__(self, **values):
        super().__init__(**values)
        self.proxy_list = self.load_proxies_from_env()
        self._proxy_cycle = cycle(self.proxy_list)

    def load_proxies_from_env(self):
        proxy_str = self.proxy_list.get_secret_value()
        return proxy_str.split(",") if proxy_str else []

    def get_next_proxy(self):
        return next(self._proxy_cycle)

    def create_async_client_with_proxy(self):
        """
        Если прокси лист пуст — возвращаем обычный httpx.AsyncClient.
        Иначе — создаём клиент с использованием прокси.
        """
        if not self.proxy_list:
            return httpx.AsyncClient()
        proxy = self.get_next_proxy()
        host, port, user, password = proxy.split(":")
        proxy_url = f"http://{user}:{password}@{host}:{port}"
        client = httpx.AsyncClient(proxies=proxy_url)
        return client


settings = Settings()
