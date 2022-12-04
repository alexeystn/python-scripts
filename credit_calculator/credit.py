import numpy as np


def get_monthly_payment(total_sum, rate_percents, months_count):
    P = rate_percents / 100 / 12
    N = months_count
    S = total_sum
    x = S * (P + P/((1+P)**N - 1))
    return x


def get_months_count(total_sum, rate_percents, monthly_payment):
    P = rate_percents / 100 / 12
    S = total_sum
    x = monthly_payment
    N = np.log(P / (x/S - P) + 1) / np.log(1+P)
    return N


monthly_P = 100e3

# BEFORE:
amount = 7.0e6
rate = 7
n = get_months_count(amount, rate, monthly_P)
print(n)

# AFTER:
amount = 6.0e6
rate = 11
n = get_months_count(amount, rate, monthly_P)
print(n)
