def calculate_total_revenue(cash_in, card_in, qr_in, cash_return, card_return):
    return cash_in + card_in + qr_in - cash_return - card_return

def calculate_cash_end(cash_start, cash_in, incassation, salary, rko, pko, exchange):
    return cash_start + cash_in - incassation - salary - rko + pko + exchange

def validate_counter_vs_revenue(counter_start, counter_end, total_revenue):
    return abs((counter_end - counter_start) - total_revenue) < 0.01  # допуск копеек