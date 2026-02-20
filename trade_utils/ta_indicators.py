# EMA(today) = Closing price(today) x multiplier + EMA(previous day) x (1-multiplier)
# multiplier = (smoothing / 1 + days)
# smoothing = 2 or 3

from typing import List

from trade_utils.returns import (
    calculate_avg_gain,
    calculate_avg_loss,
    calculate_simple_returns,
    get_rsi_value,
)

SMOOTHING = 2


def calculate_sma(num_days, data):
    n = len(data)
    if n < num_days:
        return []

    sums = []
    i = 0
    j = num_days

    initial_sum = sum(d for d in data[:num_days])
    sums.append(initial_sum)

    while j < n:
        sums.append(sums[-1] + data[j] - data[i])
        j += 1
        i += 1

    sma = [round(s / num_days, 2) for s in sums]
    return sma


def calculate_ema(num_days, data):
    n = len(data)
    if n < num_days:
        return []
    ema = []
    multiplier = SMOOTHING / (1 + num_days)

    sma = calculate_sma(num_days, data[:num_days])
    ema.append(sma[0])

    for i in range(num_days, n):
        ema_temp = (data[i] * multiplier) + (ema[-1] * (1 - multiplier))
        ema.append(round(ema_temp, 2))

    return ema

def calculate_ema_crossover(ema_short, ema_long):
    # ema_short and ema_long are arrays with the respective ema values
    starting_point = len(ema_short) - len(ema_long)
    ema_crossover = [(ema_short[starting_point + i], ema_long[i]) for i in range(len(ema_long))]

    return ema_crossover


def rsi(num_days, data):
    # rs = avg. gain / avg. loss
    n = len(data)
    if n < num_days:
        return []

    i = 0
    j = num_days
    rsi_values = []

    gains = []
    losses = []
    for k in range(i, j):
        returns = calculate_simple_returns(data[k][1], data[k][4])
        if returns > 0:
            gains.append(returns)
            losses.append(0)
        else:
            losses.append(abs(returns))
            gains.append(0)

    avg_gain = calculate_avg_gain(gains)
    avg_loss = calculate_avg_loss(losses)

    rs = avg_gain / avg_loss
    rsi_values.append(get_rsi_value(rs))

    while j < n:
        gain = []
        loss = []
        for k in range(i, j):
            returns = calculate_simple_returns(data[k][1], data[k][4])
            if returns < 0:
                loss.append(abs(returns))
                gain.append(0)
            else:
                gain.append(returns)
                loss.append(0)

        avg_gain = sum(gain) / len(gain)
        avg_loss = sum(loss) / len(loss)

        if avg_loss == 0:
            rsi_values.append(100)
        else:
            rsi_value = 100 - (100 / (1 + (avg_gain / avg_loss)))
            rsi_values.append(rsi_value)
        i += 1
        j += 1

    return rsi_values
