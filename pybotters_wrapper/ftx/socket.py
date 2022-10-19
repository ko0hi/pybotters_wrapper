from pybotters_wrapper.common import SocketChannels


class FTXSocketChannels(SocketChannels):
    ENDPOINT = "wss://ftx.com/ws"

    @classmethod
    def _subscribe(cls, channel, **kwargs):
        params = {"op": "subscribe", "channel": channel}
        params.update(kwargs)
        return params

    @classmethod
    def trades(cls, symbol, **kwargs):
        return cls._subscribe("trades", market=symbol)

    