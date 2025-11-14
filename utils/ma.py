# EMA(today) = Closing price(today) x multiplier + EMA(previous day) x (1-multiplier)
# multiplier = (smoothing / 1 + days)
# smoothing = 2 or 3

SMOOTHING = 2


def calculate_sma(num_days, data):
    n = len(data)
    if n < num_days:
        return []

    sums = []
    i = 0
    j = num_days

    initial_sum = sum(data[:num_days][4])
    sums.append(initial_sum)

    while j < n:
        sums.append(sums[-1] + data[j][4] - data[i][4])
        j += 1
        i += 1

    sma = [round(s / num_days, 2) for s in sums]
    return sma


def calculate_ema(num_days, data):
    ema = []
    n = len(data)
    multiplier = SMOOTHING / (1 + num_days)

    sma = calculate_sma(num_days, data[:num_days][4])
    ema.append(sma[0])

    for i in range(num_days, n):
        ema_temp = (data[i][4] * multiplier) + (ema[-1] * (1 - multiplier))
        ema.append(ema_temp)

    return ema
