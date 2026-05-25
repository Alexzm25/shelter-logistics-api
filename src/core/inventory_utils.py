LOW_STOCK_MULTIPLIER = 1.5


def resolve_alert_level(quantity, minimum_stock_level):
    if quantity <= minimum_stock_level:
        return "critical"
    if quantity <= minimum_stock_level * LOW_STOCK_MULTIPLIER:
        return "warning"
    return "normal"
