from typing import Any, Dict, Optional, Sequence

TIMEFRAME_M5: int
ORDER_TYPE_BUY: int
ORDER_TYPE_SELL: int
ORDER_TIME_GTC: int
ORDER_FILLING_IOC: int
TRADE_ACTION_DEAL: int
TRADE_RETCODE_DONE: int


class _TerminalInfo:
    trade_allowed: bool


class _AccountInfo:
    equity: float


class _SymbolInfo:
    visible: bool


class _TickInfo:
    ask: float
    bid: float


class _TradeResult:
    retcode: int
    order: int
    comment: str


def initialize(path: Optional[str] = ..., *, login: Optional[int] = ..., password: Optional[str] = ..., server: Optional[str] = ...) -> bool: ...
def login(*, login: int, password: str, server: str) -> bool: ...
def shutdown() -> None: ...
def last_error() -> Any: ...

def account_info() -> Optional[_AccountInfo]: ...
def symbol_info(symbol: str) -> Optional[_SymbolInfo]: ...
def symbol_info_tick(symbol: str) -> Optional[_TickInfo]: ...
def symbol_select(symbol: str, enable: bool) -> bool: ...
def order_send(request: Dict[str, Any]) -> Optional[_TradeResult]: ...
def positions_get(*, symbol: Optional[str] = ...) -> Optional[Sequence[Any]]: ...
def terminal_info() -> Optional[_TerminalInfo]: ...
def copy_rates_from_pos(symbol: str, timeframe: int, start_pos: int, count: int) -> Optional[Sequence[Any]]: ...
