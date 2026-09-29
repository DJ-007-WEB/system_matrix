import math

def runway_days(on_hand,in_transit,reserved,daily_consumption):
    if daily_consumption<=0: return math.inf
    return max(0,on_hand+in_transit-reserved)/daily_consumption

def supplier_score(on_time_rate,order_accuracy,quality_issues):
    quality=max(0,1-min(quality_issues,10)/10)
    return round(100*(.5*on_time_rate+.3*order_accuracy+.2*quality),1)

def classify_risk(runway,days_until_promised,predicted_delay):
    if runway < days_until_promised+predicted_delay: return "production-critical"
    if predicted_delay>0: return "warning"
    return "normal"
