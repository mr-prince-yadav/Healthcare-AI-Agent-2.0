def generate_recommendations(p):
    rec = []

    weight = p.get("weight", 70)
    height = p.get("height", 170)
    sleep_hours = p.get("sleep_hours", 7)
    glucose = p.get("glucose", 90)
    heart_rate = p.get("heart_rate", 70)

    height_m = height / 100
    bmi = round(weight / (height_m ** 2), 1) if height_m > 0 else 0

    if bmi < 18.5:
        rec.append("Underweight: increase calories and protein.")
    elif bmi > 25:
        rec.append("Overweight: reduce carbs and sugar.")

    if sleep_hours < 6:
        rec.append("Sleep deficit detected.")

    if glucose > 140:
        rec.append("High glucose level.")

    if heart_rate < 50 or heart_rate > 100:
        rec.append("Abnormal heart rate.")

    if "diabetes" in p.get("disease", "").lower():
        rec.append("Strict diabetic diet advised.")

    return rec
