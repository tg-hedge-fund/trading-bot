def calculate_simple_returns(start_price, end_price) -> float:
    return 100 * ((end_price - start_price) / start_price)


def calculate_avg_gain(gains):
    return gains / len(gains)


def calculate_avg_loss(losses):
    return losses / len(losses)


def get_rsi_value(rs):
    return 100 - (100 / (1 + (rs)))
