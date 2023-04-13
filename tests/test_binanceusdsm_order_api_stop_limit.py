import pytest
import pytest_mock
from aioresponses import aioresponses

from conftest import MockAsyncResponse
from pybotters_wrapper import create_client
from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_stop_limit_order_api,
)
from pybotters_wrapper.core.api_order_stop_limit import StopLimitOrderAPI


class TestOrderApiStopLimitBinanceUSDSM:
    URL = "https://fapi.binance.com/fapi/v1/order"
    SYMBOL = "BTCUSDT"
    SIDE = "BUY"
    PRICE = 40000
    SIZE = 0.01
    TRIGGER = 40000
    DUMMY_RESPONSE = {
        "orderId": 139842790733,
        "symbol": "BTCUSDT",
        "status": "NEW",
        "clientOrderId": "UgNaDaoz9q6hONkn140tAl",
        "price": "40000",
        "avgPrice": "0.00000",
        "origQty": "0.010",
        "executedQty": "0",
        "cumQty": "0",
        "cumQuote": "0",
        "timeInForce": "GTC",
        "type": "STOP",
        "reduceOnly": False,
        "closePosition": False,
        "side": "BUY",
        "positionSide": "BOTH",
        "stopPrice": "40000",
        "workingType": "CONTRACT_PRICE",
        "priceProtect": False,
        "origType": "STOP",
        "updateTime": 1681376176580,
    }

    @pytest.fixture(scope="function")
    def patch_price_size_precision_fetcher(self, mocker: pytest_mock.MockerFixture):
        mocker.patch(
            "pybotters_wrapper.binance.common.price_size_precisions_fetcher_binance.BinancePriceSizePrecisionsFetcher.fetch_precisions",
            return_value={"price": {"BTCUSDT": 1}, "size": {"BTCUSDT": 3}},
        )

    @pytest.mark.asyncio
    async def test_generate_endpoint(self, patch_price_size_precision_fetcher):
        expected = "/fapi/v1/order"

        async with create_client() as client:
            api = create_binanceusdsm_stop_limit_order_api(client, verbose=True)

            actual = api._generate_endpoint(
                {
                    "symbol": self.SYMBOL,
                    "side": self.SIDE,
                    "price": self.PRICE,
                    "size": self.SIZE,
                    "trigger": self.TRIGGER,
                    "extra_params": {},
                }
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_translate_parameters(self, patch_price_size_precision_fetcher):
        expected = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "STOP",
            "price": 40000,
            "quantity": 0.01,
            "stopPrice": 40000,
            "timeInForce": "GTC",
        }

        async with create_client() as client:
            api = create_binanceusdsm_stop_limit_order_api(client, verbose=True)
            actual = api._translate_parameters(
                {
                    "endpoint": "/fapi/v1/order",
                    "symbol": self.SYMBOL,
                    "side": self.SIDE,
                    "price": self.PRICE,
                    "size": self.SIZE,
                    "trigger": self.TRIGGER,
                    "extra_params": {},
                }
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_extract_order_id(
        self, patch_price_size_precision_fetcher, async_response_mocker
    ):
        expected = "139842790733"

        async with create_client() as client:
            api = create_binanceusdsm_stop_limit_order_api(client, verbose=True)
            actual = api._extract_order_id(
                async_response_mocker(self.DUMMY_RESPONSE, 200),
                self.DUMMY_RESPONSE,  # noqa
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_combined(
        self, patch_price_size_precision_fetcher, mocker: pytest_mock.MockerFixture
    ):
        url = "https://fapi.binance.com/fapi/v1/order"
        spy_generate_endpoint = mocker.spy(StopLimitOrderAPI, "_generate_endpoint")
        spy_translate_parameters = mocker.spy(
            StopLimitOrderAPI, "_translate_parameters"
        )
        spy_wrap_response = mocker.spy(StopLimitOrderAPI, "_wrap_response")

        async with create_client() as client:
            api = create_binanceusdsm_stop_limit_order_api(client, verbose=True)
            with aioresponses() as m:
                m.post(url, payload=self.DUMMY_RESPONSE)
                await api.stop_limit_order(
                    self.SYMBOL, self.SIDE, self.PRICE, self.SIZE, self.TRIGGER
                )

                assert spy_generate_endpoint.spy_return == "/fapi/v1/order"
                assert spy_translate_parameters.spy_return == {
                    "symbol": "BTCUSDT",
                    "side": "BUY",
                    "type": "STOP",
                    "price": 40000,
                    "quantity": 0.01,
                    "stopPrice": 40000,
                    "timeInForce": "GTC",
                }
                assert spy_wrap_response.spy_return.order_id == "139842790733"
