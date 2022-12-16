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


def get_months_count_progressive(total_sum, rate_percents, monthly_payment, inflation_rate):
    P = 1 + rate_percents / 12 / 100
    S = total_sum
    x = monthly_payment
    M = (1 + inflation_rate / 100) ** (1/12)
    months = 0
    paid = 0
    while S > x:
        S -= x
        paid += x
        S *= P
        x *= M
        months += 1
    months += S / x
    return months, paid


def format_months(months_count, text=True):
    if text:
        line = '{0:.0f} y {1:.0f} m'.format(months_count // 12,
                                            int(months_count % 12))
    else:
        line = '{:.2f}'.format(months_count / 12)
    return line


def format_sum(s):
    s = int(s)
    res = ''
    while s > 0:
        if s // 1000 > 0:
            res = ' {0:03}'.format(s % 1000) + res
        else:
            res = '{0}'.format(s) + res
        s //= 1000
    return res


full_price = 9.2e6
first_payment = 2.4e6 + 1.0e6
monthly = 70e3 
term = 30*12  # months
inflation = 7.5  # percents, yearly
discount = 0.0  # part, next year


total_credit = full_price - first_payment
print( format_sum(full_price/1000), '->', format_sum(full_price*(1-discount)/1000))

rate = 6.5
m, paid = get_months_count_progressive(total_credit, rate, monthly, inflation)
print('2022:', format_months(m, text=False), 'years')
print('Monthly:', format_sum(get_monthly_payment(total_credit, rate, term)))

total_credit -= full_price*discount

rate = 7.5
m, paid = get_months_count_progressive(total_credit, rate, monthly, inflation)
print('2023:', format_months(m, text=False), 'years')
print('Monthly:', format_sum(get_monthly_payment(total_credit, rate, term)))


