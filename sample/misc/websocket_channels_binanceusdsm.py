import asyncio
import pybotters
import pybotters_wrapper as pbw


async def main():
    symbol = "btcusdt"

    async with pybotters.Client() as client:
        channels = pbw.binance.BinanceUSDSMWebsocketChannels()
        subscribes = (
            channels.ticker(symbol)
            .agg_trades(symbol)
            .book_ticker(symbol)
            .depth(symbol)
            .kline(symbol, "1m")
            .continuous_kline(symbol, "perpetual", "1m")
            .liquidation(symbol)
            .mark_price(symbol)
            .composite_index("defiusdt")
            .order()
            .execution()
            .position()
            .get()
        )

        for endpoint, send in subscribes.items():
            await client.ws_connect(
                endpoint, send_json=send, hdlr_json=lambda msg, ws: print(msg)
            )

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
