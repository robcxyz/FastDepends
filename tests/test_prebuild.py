from __future__ import annotations

from pydantic import BaseModel, Field

from fast_depends.core import build_call_model
from fast_depends.use import inject, Depends

from .wrapper import noop_wrap


class Model(BaseModel):
    a: str
    b: list = Field(default_factory=list)


def base_func(a: int) -> str:
    return "success"


def model_func(m: Model) -> str:
    return m.a


def test_prebuild() -> None:
    model = build_call_model(base_func)
    inject()(None, model)(1)


def test_prebuild_with_wrapper() -> None:
    func = noop_wrap(model_func)
    assert func(Model(a="Hi!")) == "Hi!"

    # build_call_model should work even if function is wrapped with a
    # wrapper that is imported from different module
    call_model = build_call_model(func)

    assert call_model.model
    # Fails if function unwrapping is not done at type introspection

    if hasattr(call_model.model, "model_rebuild"):
        call_model.model.model_rebuild()
    else:
        # pydantic v1
        call_model.model.update_forward_refs()


def test_prebuild_with_inject_on_model() -> None:
    @inject
    def model_func(m: Model = Depends(Model)) -> Model:
        return m

    assert model_func(a="Hi!").b == []
