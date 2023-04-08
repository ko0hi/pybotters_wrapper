from typing import Callable, Awaitable, NamedTuple

from aiohttp.client import ClientResponse

from .._typedefs import TEndpoint, TSymbol, TSide, TSize, TRequsetMethod
from ..core import APIClient, OrderAPI, PriceSizeFormatter


class MarketOrderAPIResponse(NamedTuple):
    order_id: str
    resp: ClientResponse | None = None
    resp_data: dict | None = None


class MarketOrderAPI(OrderAPI):
    def __init__(
        self,
        api_client: APIClient,
        method: TRequsetMethod,
        order_id_key: str,
        endpoint: TEndpoint
        | Callable[[TSymbol, TSide, TSize, dict], str]
        | None = None,
        parameter_translater: Callable[[TEndpoint, TSymbol, TSide, TSize, dict], dict]
        | None = None,
        order_id_extractor: Callable[[ClientResponse, dict, str], str | None]
        | None = None,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ]
        | None = None,
        price_size_formatter: PriceSizeFormatter | None = None,
        price_format_keys: list[str] | None = None,
        size_format_keys: list[str] | None = None,
    ):
        super(MarketOrderAPI, self).__init__(
            api_client,
            method,
            order_id_key=order_id_key,
            order_id_extractor=order_id_extractor,
            response_decoder=response_decoder,
            price_size_formatter=price_size_formatter,
            price_format_keys=price_format_keys,
            size_format_keys=size_format_keys,
        )
        self._endpoint = endpoint
        self._parameter_translater = parameter_translater

    def _generate_endpoint(
        self,
        symbol: TSymbol,
        side: TSide,
        size: TSize,
        extra_params: dict,
    ) -> TEndpoint:
        assert self._endpoint is not None
        if isinstance(self._endpoint, str):
            return self._endpoint
        elif callable(self._endpoint):
            return self._endpoint(symbol, side, size, extra_params)

    def _translate_parameters(
        self,
        endpoint: TEndpoint,
        symbol: TSymbol,
        side: TSide,
        size: TSize,
        extra_params: dict,
    ) -> dict:
        assert self._parameter_translater is not None
        return self._parameter_translater(endpoint, symbol, side, size, extra_params)

    def _wrap_response(
        self, order_id: str, resp: ClientResponse, resp_data: dict
    ) -> MarketOrderAPIResponse:
        return MarketOrderAPIResponse(order_id, resp, resp_data)

    async def market_order(
        self,
        symbol: TSymbol,
        side: TSide,
        size: TSize,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> MarketOrderAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(symbol, side, size, extra_params)
        parameters = self._translate_parameters(
            endpoint, symbol, side, size, extra_params
        )
        parameters = {**parameters, **extra_params}
        parameters = self._format_size(parameters, symbol)
        resp = await self.request(endpoint, parameters, **request_params)
        resp_data = await self._decode_response(resp)
        order_id = self._extract_order_id(resp, resp_data)
        return self._wrap_response(order_id, resp, resp_data)
