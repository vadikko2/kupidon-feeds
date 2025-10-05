import logging
import typing

import di
import fastapi
from di import dependent, executors
from fastapi import security, status

from infrastructure import dependencies as infrastructure_dependencies
from service import exceptions
from service.interfaces.services import iam_service as iam_service_interface

logger = logging.getLogger(__name__)

bearer_scheme = security.HTTPBearer(auto_error=True)

_D = typing.TypeVar("_D")


async def _resolve_dependencies(container: di.Container, type_: typing.Type[_D]) -> _D:
    executor = executors.AsyncExecutor()
    solved = container.solve(
        dependent.Dependent(type_, scope="request"),
        scopes=["request"],
    )
    with container.enter_scope("request") as state:
        return await solved.execute_async(executor=executor, state=state)


async def extract_account_id(
    credentials: security.HTTPAuthorizationCredentials = fastapi.Security(
        bearer_scheme,
    ),
) -> str:
    iam_service = await _resolve_dependencies(
        infrastructure_dependencies.container,
        iam_service_interface.IAMService,
    )
    try:
        return await iam_service.get_user_id(credentials.credentials)
    except exceptions.UnauthorizedError as e:
        raise fastapi.HTTPException(status.HTTP_403_FORBIDDEN, str(e))
