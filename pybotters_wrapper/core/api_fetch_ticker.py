from typing import NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from pybotters_wrapper._typedefs import TEndpoint, TSymbol
from .api_fetch import FetchAPI
from .normalized_store_ticker import TickerItem


class TickerFetchAPIResponse(NamedTuple):
    ticker: TickerItem
    resp: ClientResponse | None = None
    resp_data: dict | None = None


class TickerFetchAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    extra_params: dict


class TickerFetchAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    extra_params: dict


class TickerFetchAPIWrapResponseParameters(TypedDict):
    item: TickerItem
    resp: ClientResponse
    resp_data: dict


class TickerFetchAPI(
    FetchAPI[
        TickerFetchAPIResponse,
        TickerFetchAPIGenerateEndpointParameters,
        TickerFetchAPITranslateParametersParameters,
        TickerFetchAPIWrapResponseParameters,
    ]
):
    async def fetch_ticker(
        self, symbol: TSymbol, *, extra_params: dict = None, request_params: dict = None
    ) -> TickerFetchAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            TickerFetchAPIGenerateEndpointParameters(
                symbol=symbol, extra_params=extra_params
            )
        )
        parameters = self._translate_parameters(
            TickerFetchAPITranslateParametersParameters(
                endpoint=endpoint, symbol=symbol, extra_params=extra_params
            )
        )
        parameters = {**parameters, **extra_params}
        resp = await self.request(endpoint, parameters, **request_params)
        resp_data = await self._decode_response(resp)
        item = self._itemize_response(resp, resp_data)
        return self._wrap_response(
            TickerFetchAPIWrapResponseParameters(
                ticker=item, resp=resp, resp_data=resp_data
            )
        )
