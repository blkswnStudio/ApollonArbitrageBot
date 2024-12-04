

def float_to_int(number: float, decimals: int) -> int:
    return int(round(number * (10 ** decimals), decimals))


def int_to_float(number: int, decimals: int) -> float:
    return round(number / (10 ** decimals), decimals)


def calc_out_given_in(amount_in: float, liquidity_in: float, liquidity_out: float, weight_in: float, weight_out: float,
                      swap_fee: float) -> float:
    amount_in_after_fee = amount_in * float(1 - swap_fee)

    liquidity_in_after = liquidity_in + amount_in_after_fee

    exponent = weight_in / weight_out
    ratio = liquidity_in / liquidity_in_after
    power = ratio ** exponent
    amount_out = liquidity_out * (1 - power)

    return amount_out


def calc_in_given_out(amount_out: float, liquidity_in: float, liquidity_out: float, weight_in: float, weight_out: float,
                      swap_fee: float) -> float:
    ratio = liquidity_out / (liquidity_out - amount_out)
    exponent = weight_out / weight_in
    amount_in = liquidity_in * (ratio ** exponent - 1) / (1 - swap_fee)
    return amount_in
