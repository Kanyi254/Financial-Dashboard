import math
import datetime as dt
import numpy as np
import yfinance as yf
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.models import TextInput, Button, DatePicker, MultiChoice

def load_data(ticker1, ticker2, start, end):
    df1 = yf.download(ticker1, start=start, end=end)
    df2 = yf.download(ticker2, start=start, end=end)
    return df1, df2

def plot_data(df, ticker, indicators, sync_axis=None):
    gain = df['Close'] > df['Open']
    loss = df['Open'] > df['Close']
    
    # Increase the width of the bars
    width = 24 * 60 * 1000  # Increase width from 12 to 24 hours

    # Create the figure with the stock name as the title
    if sync_axis is not None:
        p = figure(x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,save", width=1000,
                   x_range=sync_axis, title=f"Stock Data for {ticker}")
    else:
        p = figure(x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,save", width=1000,
                   title=f"Stock Data for {ticker}")
    p.xaxis.major_label_orientation = math.pi / 4
    p.grid.grid_line_alpha = 0.25

    # Plot the candlesticks
    p.segment(df.index, df['High'], df.index, df['Low'], color="black")
    p.vbar(df.index[gain], width, df['Open'][gain], df['Close'][gain], fill_color="#00ff00", line_color="#00ff00")
    p.vbar(df.index[loss], width, df['Open'][loss], df['Close'][loss], fill_color="#ff0000", line_color="#ff0000")

    # Add indicators
    for indicator in indicators:
        if indicator == "30 Day SMA":
            df['SMA30'] = df['Close'].rolling(30).mean()
            p.line(df.index, df['SMA30'], color="purple", legend_label="30 Day SMA")
        elif indicator == "100 Day SMA":
            df['SMA100'] = df['Close'].rolling(100).mean()
            p.line(df.index, df['SMA100'], color="purple", legend_label="100 Day SMA")
        elif indicator == "Linear Regression Line":
            par = np.polyfit(range(len(df.index.values)), df['Close'].values, 1, full=True)
            slope = par[0][0]
            intercept = par[0][1]
            y_pred = [slope * i + intercept for i in range(len(df.index.values))]
            p.line(df.index, y_pred, legend_label="Linear Regression", color="red")

    # Set legend location and click policy
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    return p

def on_button_click(ticker1, ticker2, start, end, indicators):
    df1, df2 = load_data(ticker1, ticker2, start, end)
    p1 = plot_data(df1, ticker1, indicators)
    p2 = plot_data(df2, ticker2, indicators, sync_axis=p1.x_range)
    curdoc().clear()
    curdoc().add_root(row(p1, p2))

# Input widgets
stock1_text = TextInput(title="Stock 1")
stock2_text = TextInput(title="Stock 2")
date_picker_from = DatePicker(title="Start Date", value="2024-09-06", min_date="2000-01-01",
                              max_date=dt.datetime.now().strftime("%Y-%m-%d"))
date_picker_to = DatePicker(title="End Date", value="2024-10-06", min_date="2000-01-01",
                            max_date=dt.datetime.now().strftime("%Y-%m-%d"))
indicator_choice = MultiChoice(options=["100 Day SMA", "30 Day SMA", "Linear Regression Line"])

# Button to load data
load_button = Button(label="Load Data", button_type="success")
load_button.on_click(lambda: on_button_click(stock1_text.value, stock2_text.value,
                                             date_picker_from.value, date_picker_to.value,
                                             indicator_choice.value))

# Layout for the UI
layout = column(stock1_text, stock2_text, date_picker_from, date_picker_to, indicator_choice, load_button)

# Set up the document layout
curdoc().clear()
curdoc().add_root(layout)
