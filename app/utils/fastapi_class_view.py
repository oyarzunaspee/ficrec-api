from __future__ import annotations

import re
from collections.abc import Callable, Iterable

from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from fastapi_class.openapi import _exceptions_to_responses
from fastapi_class.routers import Metadata, Method

COMMON_KEYWORD = "common"
RESPONSE_MODEL_ATTRIBUTE_NAME = "response_model"
RESPONSE_CLASS_ATTRIBUTE_NAME = "response_class"
ENDPOINT_METADATA_ATTRIBUTE_NAME = "__endpoint_metadata"
EXCEPTIONS_ATTRIBUTE_NAME = "EXCEPTIONS"


def _view_class_name_default_parser(cls: object, method: str):
    class_name = " ".join(re.findall(r"[A-Z][^A-Z]*", cls.__name__.replace("View", "")))  # type: ignore
    return f"{method.capitalize()} {class_name}"


def View(
    router: FastAPI | APIRouter,
    *,
    path: str = "/",
    default_status_code: int = status.HTTP_200_OK,
    name_parser: Callable[[object, str], str] = _view_class_name_default_parser,
):
    """Class-based view decorator for FastAPI.

    ### Example:
        >>> from fastapi import FastAPI
        >>> from fastapi_class import View

        >>> app = FastAPI()
        >>> @View(app)
        ... class MyView:
        ...     async def get(self):
        ...         return {"message": "Hello, world!"}
    """

    def _decorator(cls) -> object:
        obj = cls()
        cls_based_response_model = getattr(obj, RESPONSE_MODEL_ATTRIBUTE_NAME, {})
        cls_based_response_class = getattr(obj, RESPONSE_CLASS_ATTRIBUTE_NAME, {})
        common_exceptions = getattr(obj, EXCEPTIONS_ATTRIBUTE_NAME, {}).get(COMMON_KEYWORD, ())
        for _callable_name in dir(obj):
            _callable = getattr(obj, _callable_name)
            if _callable_name in set(Method) or hasattr(_callable, ENDPOINT_METADATA_ATTRIBUTE_NAME):
                metadata: Metadata = getattr(
                    _callable,
                    ENDPOINT_METADATA_ATTRIBUTE_NAME,
                    Metadata([_callable_name]),
                )
                exceptions: Iterable[HTTPException] = getattr(obj, ENDPOINT_METADATA_ATTRIBUTE_NAME, {}).get(
                    _callable_name, []
                )
                exceptions += common_exceptions
                _path = path
                if metadata and metadata.path:
                    _path = path + metadata.path
                router.add_api_route(
                    _path,
                    _callable,
                    methods=list(metadata.methods),
                    response_class=metadata.response_class_or_default(
                        cls_based_response_class.get(_callable_name, JSONResponse)
                    ),
                    response_model=metadata.response_model_or_default(cls_based_response_model.get(_callable_name)),
                    responses=_exceptions_to_responses(exceptions),
                    name=metadata.name_or_default(name_parser(cls, _callable_name)),
                    status_code=metadata.status_code_or_default(default_status_code),
                )
        return obj

    return _decorator