# -*- coding: utf-8 -*-
import numpy as np
import dash
import pickle
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from utils_animation import read_ohlc
from plotly.subplots import make_subplots
from utils_animation import get_frame

ts_tickers = ['1INCHUSDT', 'AAVEUSDT', 'ADAUSDT', 'ALGOUSDT', 'ALICEUSDT', 'ALPHAUSDT', 'ANKRUSDT', 'ARDRUSDT',
              'ARUSDT', 'ATOMUSDT', 'AUDIOUSDT', 'AVAXUSDT', 'AXSUSDT', 'BADGERUSDT', 'BAKEUSDT', 'BANDUSDT',
              'BATUSDT', 'BCHUSDT', 'BNBUSDT', 'BNTUSDT', 'BTCSTUSDT', 'BTCUSDT', 'BTGUSDT', 'BTTUSDT',
              'BUSDUSDT', 'CAKEUSDT', 'CELOUSDT', 'CELRUSDT', 'CFXUSDT', 'CHZUSDT', 'CKBUSDT', 'COMPUSDT',
              'COTIUSDT', 'CRVUSDT', 'CTSIUSDT', 'CVCUSDT', 'DAIUSDT', 'DASHUSDT', 'DCRUSDT', 'DENTUSDT',
              'DGBUSDT', 'DOGEUSDT', 'DOTUSDT', 'DYDXUSDT', 'EGLDUSDT', 'ELFUSDT', 'ENJUSDT', 'EOSUSDT',
              'ETCUSDT', 'ETHUSDT', 'EURUSDT', 'FETUSDT', 'FILUSDT', 'FLOWUSDT', 'FTMUSDT', 'FTTUSDT',
              'FUNUSDT', 'GBPUSDT', 'GNOUSDT', 'GRTUSDT', 'HBARUSDT', 'HIVEUSDT', 'HNTUSDT', 'HOTUSDT',
              'ICPUSDT', 'ICXUSDT', 'INJUSDT', 'IOSTUSDT', 'IOTAUSDT', 'IOTXUSDT', 'JUVUSDT', 'KAVAUSDT',
              'KLAYUSDT', 'KSMUSDT', 'LINKUSDT', 'LPTUSDT', 'LRCUSDT', 'LSKUSDT', 'LTCUSDT', 'LUNAUSDT',
              'MANAUSDT', 'MATICUSDT', 'MDXUSDT', 'MINAUSDT', 'MKRUSDT', 'MLNUSDT', 'MTLUSDT', 'NANOUSDT',
              'NEARUSDT', 'NEOUSDT', 'NKNUSDT', 'NMRUSDT', 'NUUSDT', 'OCEANUSDT', 'OGNUSDT', 'OMGUSDT',
              'ONEUSDT', 'ONGUSDT', 'ONTUSDT', 'OXTUSDT', 'PAXGUSDT', 'PERPUSDT', 'POLYUSDT', 'QNTUSDT',
              'QTUMUSDT', 'RANDOM_1', 'RANDOM_2', 'RANDOM_3', 'RAYUSDT', 'REEFUSDT', 'RENUSDT', 'REPUSDT',
              'RLCUSDT', 'ROSEUSDT', 'RSRUSDT',
              'RUNEUSDT', 'RVNUSDT', 'SANDUSDT', 'SCUSDT', 'SHIBUSDT', 'SKLUSDT', 'SNXUSDT', 'SOLUSDT',
              'SRMUSDT', 'STMXUSDT', 'STORJUSDT', 'STRAXUSDT', 'STXUSDT', 'SUSHIUSDT', 'SXPUSDT', 'TFUELUSDT',
              'THETAUSDT', 'TOMOUSDT', 'TRXUSDT', 'TUSDUSDT', 'UMAUSDT', 'UNIUSDT', 'USDCUSDT', 'USDPUSDT',
              'VETUSDT', 'VTHOUSDT', 'WAVESUSDT', 'WAXPUSDT', 'WINUSDT', 'WRXUSDT', 'XECUSDT', 'XEMUSDT',
              'XLMUSDT', 'XRPUSDT', 'XTZUSDT', 'XVGUSDT', 'XVSUSDT', 'YFIUSDT', 'ZECUSDT', 'ZENUSDT',
              'ZILUSDT', 'ZRXUSDT']

options = [{"label": item if item in ("RANDOM_1", "RANDOM_2", "RANDOM_3") else item[:-4], "value": item} for item in ts_tickers]


app = Dash(__name__)

server = app.server

app.layout = html.Div([
    dcc.Dropdown(
        id='upper-plot-select',
        options=options,
        value='BTCUSDT',  # default value for drop down menu
        clearable=False,
        style={'width': '200px', 'marginBottom': '20px'}
    ),

    dcc.Graph(id='upper-graph', animate=False),
    dcc.Graph(id='sine-graph', animate=False),

    dcc.Interval(
        id='interval-component',
        interval=25,  # 40 FPS
        n_intervals=0,
        disabled=True  # start paused
    ),

    dcc.Slider(
        id='frame-slider',
        min=0,
        # max=100,  # Fallback initial max
        value=0,
        step=1,
        updatemode='drag'
    ),

    html.Div([
        html.Button('Play', id='play-button', n_clicks=0),
        html.Button('Pause', id='pause-button', n_clicks=0),
    ], style={'marginTop': '20px'})
])

#
# This callback turns animation on/off by enabling or disabling the timer based on user clicks on Play/Pause buttons.
# The callback listens for clicks on the Play and Pause buttons.
# When Play is clicked → returns False to enable the Interval (start the timer, so animation runs).
# When Pause is clicked → returns True to disable the Interval (stop the timer, so animation pauses).
# Otherwise, keeps the current disabled state.
#


@app.callback(
    Output('interval-component', 'disabled'),
    Input('play-button', 'n_clicks'),
    Input('pause-button', 'n_clicks'),
    State('interval-component', 'disabled'),
)
def play_pause(play_clicks, pause_clicks, disabled):
    ctx = dash.callback_context
    if not ctx.triggered:
        return True
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'play-button':
        return False
    elif button_id == 'pause-button':
        return True
    return disabled

@app.callback(
    Output('frame-slider', 'max'),
    Output('frame-slider', 'marks'),
    Input('upper-plot-select', 'value')
)
def update_slider_max(upper_plot_value):
    data = read_ohlc(full_path=f"data/{upper_plot_value}-D-data.csv")
    max_frame = data.shape[0] - 1
    marks = {i: str(i) for i in range(0, max_frame + 1, 200)}
    return max_frame, marks


@app.callback(
    Output('frame-slider', 'value'),
    Input('interval-component', 'n_intervals'),
    State('frame-slider', 'value'),
    State('frame-slider', 'max'),
)
def update_slider(n_intervals, slider_value, max_value):
    # Guard against uninitialized max_value:
    # max_value is None when the update_slider callback is triggered before update_slider_max has set the
    # frame-slider's max value.
    if max_value is None or slider_value is None:
        return 0

    if slider_value >= max_value:
        return 0
    return slider_value + 1

@app.callback(
    Output('upper-graph', 'figure'),
    Output('sine-graph', 'figure'),
    Input('frame-slider', 'value'),
    Input('upper-plot-select', 'value')
)
def update_graphs(frame, upper_plot_value):

    # Upper plot
    data = read_ohlc(full_path=f"data/{upper_plot_value}-D-data.csv")
    x = np.arange(0, data.shape[0])
    y_upper = data["price_C"].values 
    title = f'{upper_plot_value}'
    color = 'green'

    y_sin = y_upper

    upper_fig = make_subplots() 

    upper_fig.add_trace(go.Scatter(x=x[:(frame+1)], y=y_upper[:(frame+1)], mode='lines', line=dict(color="blue"), showlegend=False))

    upper_fig.add_trace(go.Scatter(x=x[(frame+1):], y=y_upper[(frame+1):], mode='lines', line=dict(color="lightgrey"), showlegend=False))


    # Lower plot

    with open(f"data/{upper_plot_value}-frames.pickle", "rb") as f:
        all_frames = pickle.load(f)

    current_frame = get_frame(all_frames, frame)

    stacked = current_frame.stack().to_frame().reset_index().rename(columns={"level_0": "nr", "level_1": "indicator", 0: "value"})

    sine_fig = px.line(stacked, x="nr", y="value", color="indicator")

    sine_fig.update_layout(
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='black',
            borderwidth=1
        )
    )

    return upper_fig, sine_fig

if __name__ == '__main__':
    app.run(debug=True)

