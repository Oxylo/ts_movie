""" Downsample 1Min data to 
"""


import pandas as pd

tickers = ["1INCHUSDT",
"AAVEUSDT",
"ADAUSDT",
"ALGOUSDT",
"ALICEUSDT",
"ALPHAUSDT",
"ANKRUSDT",
"ARDRUSDT",
"ARUSDT",
"ATOMUSDT",
"AUDIOUSDT",
"AVAXUSDT",
"AXSUSDT",
"BADGERUSDT",
"BAKEUSDT",
"BANDUSDT",
"BATUSDT",
"BCHUSDT",
"BNBUSDT",
"BNTUSDT",
"BTCSTUSDT",
"BTCUSDT",
"BTGUSDT",
"BTTUSDT",
"BUSDUSDT",
"CAKEUSDT",
"CELOUSDT",
"CELRUSDT",
"CFXUSDT",
"CHZUSDT",
"CKBUSDT",
"COMPUSDT",
"COTIUSDT",
"CRVUSDT",
"CTSIUSDT",
"CVCUSDT",
"DAIUSDT",
"DASHUSDT",
"DCRUSDT",
"DENTUSDT",
"DGBUSDT",
"DOGEUSDT",
"DOTUSDT",
"DYDXUSDT",
"EGLDUSDT",
"ELFUSDT",
"ENJUSDT",
"EOSUSDT",
"ETCUSDT",
"ETHUSDT",
"EURUSDT",
"FETUSDT",
"FILUSDT",
"FLOWUSDT",
"FTMUSDT",
"FTTUSDT",
"FUNUSDT",
"GBPUSDT",
"GNOUSDT",
"GRTUSDT",
"HBARUSDT",
"HIVEUSDT",
"HNTUSDT",
"HOTUSDT",
"ICPUSDT",
"ICXUSDT",
"INJUSDT",
"IOSTUSDT",
"IOTAUSDT",
"IOTXUSDT",
"JUVUSDT",
"KAVAUSDT",
"KLAYUSDT",
"KSMUSDT",
"LINKUSDT",
"LPTUSDT",
"LRCUSDT",
"LSKUSDT",
"LTCUSDT",
"LUNAUSDT",
"MANAUSDT",
"MATICUSDT",
"MDXUSDT",
"MINAUSDT",
"MKRUSDT",
"MLNUSDT",
"MTLUSDT",
"NANOUSDT",
"NEARUSDT",
"NEOUSDT",
"NKNUSDT",
"NMRUSDT",
"NUUSDT",
"OCEANUSDT",
"OGNUSDT",
"OMGUSDT",
"ONEUSDT",
"ONGUSDT",
"ONTUSDT",
"OXTUSDT",
"PAXGUSDT",
"PERPUSDT",
"POLYUSDT",
"QNTUSDT",
"QTUMUSDT",
"RAYUSDT",
"REEFUSDT",
"RENUSDT",
"REPUSDT",
"RLCUSDT",
"ROSEUSDT",
"RSRUSDT",
"RUNEUSDT",
"RVNUSDT",
"SANDUSDT",
"SCUSDT",
"SHIBUSDT",
"SKLUSDT",
"SNXUSDT",
"SOLUSDT",
"SRMUSDT",
"STMXUSDT",
"STORJUSDT",
"STRAXUSDT",
"STXUSDT",
"SUSHIUSDT",
"SXPUSDT",
"TFUELUSDT",
"THETAUSDT",
"TOMOUSDT",
"TRXUSDT",
"TUSDUSDT",
"UMAUSDT",
"UNIUSDT",
"USDCUSDT",
"USDPUSDT",
"VETUSDT",
"VTHOUSDT",
"WAVESUSDT",
"WAXPUSDT",
"WINUSDT",
"WRXUSDT",
"XECUSDT",
"XEMUSDT",
"XLMUSDT",
"XRPUSDT",
"XTZUSDT",
"XVGUSDT",
"XVSUSDT",
"YFIUSDT",
"ZECUSDT",
"ZENUSDT",
"ZILUSDT",
"ZRXUSDT"]

def downsample_binance_generalized(df, freq='5m', remove_incomplete_candles=True, minimum_pct_minutes_per_candle=80):
    """ Return dataframe with given frequency

    Credits: http://sacbnctrading.blogspot.com/2016/10/convert-1m-ohlc-data-into-other.html

    Paraneters
    ----------
      df                             : Dataframe. Contains 1 minute candles according to Binance format
      freq                           : String. Frequency after downsampling given df like 3Min, 5Min, 15Min, 1H, 4H etc.
      remove_incomplete_candles      : Boolean
      minimum_pct_minutes_per_candle : Float

    Returns
    -------
      Dataframe
    """
    
    aggregator = {'open':'first', 'high':'max', 'low':'min', 'close':'last',
                  'volume':'sum', 'close_time': 'last', 'quote_av': 'sum', 
                  'trades':'sum', 'tb_base_av': 'sum', 'tb_quote_av': 'sum',
                  'range': 'sum'}
    
    aggreg = dict()
    
    for col in df.columns:
        if 'close_time' in col:
            aggreg[col] = aggregator['close_time']
        elif '_O' in col:
            aggreg[col] = aggregator['open']
        elif '_H' in col:
            aggreg[col] = aggregator['high']
        elif '_L' in col:
            aggreg[col] = aggregator['low']
        elif '_C' in col:
            aggreg[col] = aggregator['close']
        elif '_V' in col:
            aggreg[col] = aggregator['volume']
        elif 'tb_quote_av' in col:
            aggreg[col] = aggregator['tb_quote_av']
        elif 'quote_av' in col:
            aggreg[col] = aggregator['quote_av']
        elif 'trades' in col:
            aggreg[col] = aggregator['trades']
        elif 'tb_base_av' in col:
            aggreg[col] = aggregator['tb_base_av']
        elif 'range' in col:
            aggreg[col] = aggregator['range']
        else:
            print('*** WARNING: Unable to convert {} to appropriate column name'.format(col))
           
    
    if remove_incomplete_candles:
        # Remove incomplete candles less than minimum_pct_minutes_per_candle complete
        nminutes_per_candle = freq2min(freq)
        nminutes_required =  int((minimum_pct_minutes_per_candle / 100)  * nminutes_per_candle)
        df['ones'] = 1
        aggreg['ones'] = 'sum'
        outp = df.resample(freq).agg(aggreg)
        outp = outp[outp.ones >= nminutes_required].dropna(how='any')
        df.drop('ones', axis=1, inplace=True)
        return outp.drop('ones', axis=1)
    else:
        outp = df.resample(freq).agg(aggreg).dropna(how='any')
        return outp

def freq2min(freq):
    """ Convert frequency to minutes
    """
    mins = range(1, 59)
    lookup1 = {str(m) + 'm': m for m in mins}
    lookup2 = {str(m) + 'Min': m for m in mins}
    lookup3 = {'1H': 60,
              '2H': 120,
              '4H': 240,
              '6H': 360,
              '8H': 480,
              '12H': 720,
              '1D': 1440,
              '3D': 4320,
              '1w': 10080,
              '1M': 43200}
    lookup = {**lookup1, **lookup2, **lookup3}
    return lookup.get(freq, 'Not found!')




for ticker in tickers:

    infile = f"~/projects/cando/data/{ticker}-1m-data.csv"
    df = pd.read_csv(infile, usecols=[0, 1, 2, 3, 4, 5])
    df["timestamp"] = pd.to_datetime(df["timestamp"],format= "%Y-%m-%d %H:%M:%S")
    df = df.rename(columns={'open': 'price_O', 'high': 'price_H', 'low': 'price_L', 'close': 'price_C', 'volume': 'total_V'})
    ddf = df.groupby("timestamp").first()

    for frq in ["H", "D", "W"]:
        print(f"Downsampling: {ticker} to {frq}...", end="")
        data = downsample_binance_generalized(ddf, freq=frq, remove_incomplete_candles=False)
        outfile = f"~/projects/cando/data/{ticker}-{frq}-data.csv"
        data.reset_index().to_csv(outfile, index=False)
        print("OK")

print("Ready!")




