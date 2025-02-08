import time
import requests
import logging
from .exceptions import (
    NortecApiApplicationException,
    NortecApiServerException,
    NortecApiCorruptedSessionException,
    NortecApiSessionExpiredException,
    NortecApiLogicException,
)
from .models import Message

logger = logging.getLogger(__name__)


class NortecApiWrapper:
    base_url = "https://backend.nortec1.dk"
    session = None

    def __init__(
        self,
        username: str,
        password: str,
        session: str | None = None,
    ):
        self.session = session
        self.username = username
        self.password = password

        self._validate_session()

    def _get_params(self, additional_params: None | dict = None) -> dict:
        if additional_params is None:
            additional_params = {}

        params = {
            "App": "TUK",
            "session": self.session,
            "tick": self._get_tick(),
            "native": "false",
        }
        params.update(additional_params)
        return params

    @staticmethod
    def _get_tick() -> int:
        return int(time.time() * 1000)

    @staticmethod
    def _raise_for_response_code(response: dict) -> None:
        return_value = response.get("Return")
        match return_value:
            case None:
                raise NortecApiLogicException("Return value not found in response")
            case 100:
                return
            case 206:
                raise NortecApiServerException()
            case 207:
                raise NortecApiSessionExpiredException()
            case 208:
                raise NortecApiCorruptedSessionException()
            case 224:
                raise NortecApiApplicationException()
            case _:
                return

    def _check_session_update(self, session: str):
        """
        Session can change during the API call, this method updates used session for the next calls
        """
        if session != self.session:
            self.session = session

    def _make_api_call(self, endpoint: str, params: dict) -> dict:
        # unfortunately, API needs `.json` without `=`, but requests doesn't allow it, so let's use this workaround
        url = f"{self.base_url}{endpoint}?.json"
        response = requests.get(url, params=params)
        self._raise_for_response_code(response.json())

        # session update check
        if "Session" in response.json():
            self._check_session_update(response.json()["Session"])

        return response.json()

    def _validate_session(self):
        endpoint = "/User/Home3/"
        params = self._get_params(additional_params={"tabid": 1})
        try:
            self._make_api_call(endpoint, params)
        except (NortecApiSessionExpiredException, NortecApiCorruptedSessionException):
            self.session = ""
            self._login(self.username, self.password)

    def _login(self, username: str, password: str):
        endpoint = "/User/Login4/"
        params = self._get_params(
            {
                "username": username,
                "password": password,
                "domain": "https://vuoronvaraus.fi",
                "language": "fi",
                "guid": "",
            }
        )
        response = self._make_api_call(endpoint, params)
        if "Session" not in response:
            raise ValueError("Session not found in login response")

    def get_messages(self) -> list[Message]:
        endpoint = "/User/Messages1/"
        params = self._get_params()
        response = self._make_api_call(endpoint, params)
        messages = [Message(**section) for section in response["Sections"]]
        return messages
