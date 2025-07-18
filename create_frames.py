""" Create frames for time series animations
"""

import numpy as np
import pandas as pd
import pickle
from utils_animation import calculate_min_max_indicators

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


for ticker in tickers:

    print(f"Processing: {ticker}...", end="")

    # Read time series (daily data)

    infile = f"~/projects/cando/data/{ticker}-D-data.csv"
    df = pd.read_csv(infile)
    df["timestamp"] = pd.to_datetime(df["timestamp"],format= "%Y-%m-%d")
    df.sort_values("timestamp", inplace=True)
    df.set_index("timestamp", inplace=True)

    frames = calculate_min_max_indicators(df)
    outfile = f"/home/pieter/projects/cando/data/{ticker}-frames.pickle"

    with open(outfile, 'wb') as f:
        pickle.dump(frames, f)

    print("OK")


