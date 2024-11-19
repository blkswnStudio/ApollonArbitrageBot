

def float_to_int(number: float, decimals: int) -> int:
    return int(round(number * (10 ** decimals), decimals))


def int_to_float(number: int, decimals: int) -> float:
    return round(number / (10 ** decimals), decimals)
