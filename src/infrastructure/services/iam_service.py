import logging
import os

import dotenv
import httpx
import httpx_retries
import jwt
import orjson

import settings
from service import exceptions
from service.interfaces.services import iam_service

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


class LocalJWTIAMService(iam_service.IAMService):
    """
    Проверка access-токена так же, как в IAM.
    Те же параметры jwt.decode: secret, algorithm, audience, issuer.
    """

    def __init__(self) -> None:
        self._settings = settings.jwt_settings

    @staticmethod
    def _log_signature_debug(
        token: str,
        jwt_secret: str,
        expected_issuer: str,
        expected_audience: str,
    ) -> None:
        """При APP_DEBUG логирует payload токена и длину секрета для отладки Signature verification failed."""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            logger.warning(
                "JWT signature debug (APP_DEBUG): token iss=%r aud=%r sub=%r | "
                "expect iss=%r aud=%r | secret_len=%d last_char=%r",
                payload.get("iss"),
                payload.get("aud"),
                payload.get("sub"),
                expected_issuer,
                expected_audience,
                len(jwt_secret),
                repr(jwt_secret[-1]) if jwt_secret else "n/a",
            )
        except Exception:
            pass

    async def get_user_id(self, token: str) -> str:
        jwt_secret = self._settings.secret
        jwt_algorithm = self._settings.algorithm
        jwt_audience = self._settings.audience
        jwt_issuer = self._settings.issuer
        try:
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=[jwt_algorithm],
                audience=jwt_audience,
                issuer=jwt_issuer,
            )
        except jwt.ExpiredSignatureError as e:
            logger.error("Invalid access token: %s", e)
            raise exceptions.UnauthorizedError("token expired")
        except jwt.InvalidTokenError as e:
            if "Signature verification failed" in str(e):
                self._log_signature_debug(token, jwt_secret, jwt_issuer, jwt_audience)
            logger.error("Invalid access token: %s", e)
            raise exceptions.UnauthorizedError("invalid token")
        user_id = payload.get("sub")
        if not user_id:
            logger.error("Invalid access token: user_id not found in token")
            raise exceptions.GetUserIdError("user_id not found in token")
        return str(user_id)


class HttpIAMService(iam_service.IAMService):
    VALIDATE_TOKEN_ENDPOINT = os.getenv("VALIDATE_TOKEN_ENDPOINT", default="notset")

    def __init__(self):
        self.transport = httpx_retries.RetryTransport(
            retry=httpx_retries.Retry(
                total=15,
                backoff_factor=1,
                status_forcelist=[502, 503, 504, 429],
                allowed_methods=["POST", "GET"],
            ),
        )

    async def get_user_id(self, token: str) -> str:
        logger.info("Validating token")
        try:
            async with httpx.AsyncClient(
                transport=self.transport,
            ) as client:
                response = await client.get(
                    self.VALIDATE_TOKEN_ENDPOINT,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}",
                    },
                    timeout=30.0,
                )
        except httpx.HTTPError as e:
            logger.error(f"Failed to get user id: {e}")
            raise exceptions.GetUserIdError(f"Failed to get user id: {str(e)}")

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get user id: {e}")
            response_data = orjson.loads(response.content)
            raise exceptions.UnauthorizedError(response_data.get("message", "unknown"))

        response_data = orjson.loads(response.content)

        return response_data["result"]["user_id"]
