# Stubs for texttable (Python 3.6)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any, List

class ArraySizeError(Exception):
    msg = ...  # type: Any
    def __init__(self, msg: Any) -> None: ...

class Texttable:
    BORDER = ...  # type: int
    HEADER = ...  # type: Any
    HLINES = ...  # type: Any
    VLINES = ...  # type: Any
    def __init__(self, max_width: int = ...) -> None: ...
    def reset(self) -> None: ...
    def set_chars(self, array: List) -> None: ...
    def set_deco(self, deco: Textable.HEADER): ...
    def set_cols_align(self, array: List) -> None: ...
    def set_cols_valign(self, array: List) -> None: ...
    def set_cols_dtype(self, array: List) -> None: ...
    def set_cols_width(self, array: List) -> None: ...
    def set_precision(self, width): ...
    def header(self, array: List): ...
    def add_row(self, array: List): ...
    def add_rows(
        self,
        rows: List[List[str]],
        header: bool = ...
    ): ...
    def draw(self) -> str: ...
