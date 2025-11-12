# EMA(today) = Closing price(today) x multiplier + EMA(previous day) x (1-multiplier)
# multiplier = (smoothing / 1 + days)
# smoothing = 2 or 3

SMOOTHING = 3

def calculate_sma(num_days, data):
    n = len(data)
    sma = []
    i = 0
    j = num_days - 1
    while j < n:
        sum = 0
        for k in range(i, j + 1):
            sum += data[k][4]
        sma.append(sum / num_days)
        i += 1
        j += 1
    return sma


def calculate_ema(num_days, data):
    ema = []
    n = len(data)
    i = 0
    j = num_days - 1
    multiplier = SMOOTHING / (1 + num_days)
    while j < n:
        for k in range(i, j + 1):
            if k == 0:
                ema_temp = data[k][4] * multiplier + calculate_sma(num_days, data)[-1] * (1 - multiplier)
            else:
                ema_temp = data[k][4] * multiplier + ema[k - 1] * (1 - multiplier)
            ema.append(ema_temp)
