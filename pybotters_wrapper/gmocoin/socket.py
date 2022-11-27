from __future__ import annotations

from pybotters_wrapper.common import WebsocketChannels


class GMOWebsocketChannels(WebsocketChannels):
    PUBLIC_ENDPOINT = "wss://api.coin.z.com/ws/public/v1"
    PRIVATE_ENDPOINT = "wss://api.coin.z.com/ws/private/v1"
    ENDPOINT = PUBLIC_ENDPOINT

    def _make_endpoint_and_request_pair(self, channel, **kwargs):
        params = {"command": "subscribe", "channel": channel}
        params.update(kwargs)

        endpoint = (
            self.PRIVATE_ENDPOINT
            if channel.endswith("Events")
            else self.PUBLIC_ENDPOINT
        )

        return endpoint, params

    # common channel methods
    def ticker(self, symbol, **kwargs):
        return self._subscribe("ticker", symbol=symbol)

    def trades(self, symbol, option="TAKER_ONLY", **kwargs):
        return self._subscribe("trades", symbol=symbol, option=option)

    def orderbook(self, symbol, **kwargs):
        return self.orderbooks(symbol)

    # GMO channel methods
    def orderbooks(self, symbol):
        return self._subscribe("orderbooks", symbol=symbol)

    def execution_events(self):
        return self._subscribe("executionEvents")

    def order_events(self):
        return self._subscribe("orderEvents")

    def position_events(self):
        return self._subscribe("positionEvents")

    def position_summary_events(self):
        return self._subscribe("positionSummaryEvents")

