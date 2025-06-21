import math as m
import pandas as pd
import numpy as np
from datetime import timedelta



def downsample_binance(df, freq='5m'):
    """ Return dataframe with given frequency

    Credits: http://sacbnctrading.blogspot.com/2016/10/convert-1m-ohlc-data-into-other.html

    Paraneters
    ----------
      df   : Dataframe. Contains 1 minute candles according to Binance format
      freq : String. Frequency after downsampling given df like 3Min, 5Min, 15Min, 1H, 4H etc.

    Returns
    -------
      Dataframe
    """
    aggregator = {'open':'first', 'high':'max', 'low':'min', 'close':'last',
                  'volume':'sum', 'close_time': 'last', 'quote_av': 'sum', 
                  'trades':'sum', 'tb_base_av': 'sum', 'tb_quote_av': 'sum',
                  'range': 'sum'}
    outp = df.resample(freq).agg(aggregator).dropna(how='any')
    cols=['open', 'high', 'low', 'close', 'volume', 'close_time',
         'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'range']
    return outp[cols]


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


def price_plot(df_source: pd.DataFrame, framenr:int) -> None:
    """ Return price plot on dashboard
    """
    fig, ax = plt.subplots()
    ax.set_xlim((0, df_source.shape[0]))
    past = df_source[df_source.index<=framenr]
    future = df_source[df_source.index>framenr]
    past.plot(y="price_C", color="blue", ax=ax)
    future.plot(y="price_C", color="lightgrey", ax=ax)


def calculate_min_max_indicators(ohlc: pd.DataFrame) -> dict:
    """ Return dict with indicator history for location_factor, PATH_ratio and ATLH_ratio
    """
    result = dict()
                                 
    # Calculate running MAX
    time_series = ohlc["price_H"].values
    nitems = np.shape(time_series)[0]
    stacked = time_series * np.ones((nitems,nitems))
    upper_triangle = np.triu(stacked)
    mask = np.arange(stacked.shape[0])[:,None] > np.arange(stacked.shape[1])
    upper_triangle[mask] = np.nan
    running_max = np.fmax.accumulate(upper_triangle, axis=1)
    
    # Calculate running MIN
    time_series = ohlc["price_L"].values
    nitems = np.shape(time_series)[0]
    stacked = time_series * np.ones((nitems,nitems))
    upper_triangle = np.triu(stacked)
    mask = np.arange(stacked.shape[0])[:,None] > np.arange(stacked.shape[1])
    upper_triangle[mask] = np.nan
    running_min = np.fmin.accumulate(upper_triangle, axis=1)
    
    # Calculate location factor, Price All Time High ratio (PATH_ratio) and All Time Low All Time High ratio (ATLH_ratio)
    result["location_factor"] = 100 * (running_min - ohlc["price_C"].values) / (running_min - running_max) 
    result["PATH_ratio"] = 100 *  ohlc["price_C"].values / running_max 
    result["ATLH_ratio"] = 100 * running_min / running_max
    return result


def get_frame(indicators: dict, i: int) -> pd.DataFrame:
    return pd.DataFrame({k: indicators[k][:, i] for k in ["location_factor", "PATH_ratio", "ATLH_ratio"]})


def create_random_ohlc(size:int=10, start_price:float=6000, std_daily_change: float= 500,
                       mean_bivariate_normal:list=[5.4, 5.4], cov_bivariate_normal: list = [[1.4, 0.3],[0.3, 1.4]]) -> pd.DataFrame:
    """ Return OHLC dataframe with random walk prices
    """
    outp = pd.DataFrame(index=range(size), columns=["price_O", "price_H", "price_L", "price_C"])
    outp["price_L"] = np.repeat(-9999, repeats=size)
    number_of_iterations = 0
    
    while sum(outp["price_L"] < 0):       
        daily_change = np.random.normal(loc=0, scale=std_daily_change, size=size)
        outp["price_C"] = start_price + np.cumsum(daily_change) - daily_change[0]
        delta = np.random.multivariate_normal(mean=mean_bivariate_normal, cov=cov_bivariate_normal, size=size)
        delta = np.exp(delta)
        outp["price_L"] = outp["price_C"] - delta[:, 0]
        outp["price_H"] = outp["price_C"] + delta[:, 1]
        outp["price_O"] = outp["price_C"].shift().fillna(start_price)
        number_of_iterations = number_of_iterations + 1
    print(f"Non-negative time series found in {number_of_iterations} iterations")
    return outp


def read_ohlc(full_path: str) -> pd.DataFrame:
    """ Reads CSV-file containing OHLCV data and returns it as a dataframe
    """
    df = pd.read_csv(full_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"],format= "%Y-%m-%d")
    df.sort_values("timestamp", inplace=True)
    return df.set_index("timestamp")


