from flask import Flask, render_template, request
import pickle
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table
from reportlab.lib.units import inch
from flask import send_file
import io

app = Flask(__name__)
model = pickle.load(open("model.pkl", "rb"))
accuracy = pickle.load(open("accuracy.pkl", "rb"))

@app.route('/')
def home():
    return render_template("index.html",
                           accuracy_text=f"Model Performance: {accuracy*100:.0f}% Variance Explained (R² = {accuracy:.2f})")

@app.route('/predict', methods=['POST'])
def predict():
    age = int(request.form['age'])
    sex = int(request.form['sex'])
    bmi = float(request.form['bmi'])
    children = int(request.form['children'])
    smoker = int(request.form['smoker'])
    region = request.form['region']
    

    # Create DataFrame for Pipeline
    features = pd.DataFrame({
        "age": [age],
        "sex": ["male" if sex == 0 else "female"],
        "bmi": [bmi],
        "children": [children],
        "smoker": ["yes" if smoker == 1 else "no"],
        "region": [region]
    })

    prediction = model.predict(features)
    amount = prediction[0]

    # Risk Logic
    if amount < 10000:
        risk = "Low Risk"
        risk_color = "Green"
    elif amount < 25000:
        risk = "Medium Risk"
        risk_color = "Orange"
    else:
        risk = "High Risk"
        risk_color = "Red"

    return render_template("result.html",
                       amount=f"₹{amount:,.2f}",
                       risk=risk,
                       risk_color=risk_color,
                       age=age,
                       bmi=bmi,
                       smoker="Smoker" if smoker == 1 else "Non-Smoker",
                       region=region.title(),
                       accuracy_text=f"Model Performance: {accuracy*100:.0f}% Variance Explained (R² = {accuracy:.2f})")
    
    
@app.route('/download_pdf')
def download_pdf():
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from datetime import datetime
    from flask import request, send_file
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []

    # ===== Fetch values FIRST =====
    amount = request.args.get("amount", "").replace("₹", "INR ")
    risk = request.args.get("risk", "")
    age = request.args.get("age", "")
    bmi = request.args.get("bmi", "")
    smoker = request.args.get("smoker", "")
    region = request.args.get("region", "")

    # ===== Title =====
    title_style = ParagraphStyle(
        name='TitleStyle',
        fontSize=18,
        spaceAfter=20,
        alignment=1  # Center alignment
    )

    elements.append(Paragraph("Health Insurance Risk Assessment Report", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    # ===== Date =====
    date_style = ParagraphStyle(name='DateStyle', fontSize=12)
    elements.append(Paragraph(f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M')}", date_style))
    elements.append(Spacer(1, 0.5 * inch))

    # ===== Profile Table =====
    profile_data = [
        ["Age", age],
        ["BMI", bmi],
        ["Smoking Status", smoker],
        ["Region", region]
    ]

    profile_table = Table(profile_data, colWidths=[200, 200])
    profile_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(profile_table)
    elements.append(Spacer(1, 0.5 * inch))

    # ===== Charges & Risk Table =====
    data = [
        ["Estimated Insurance Charges", amount],
        ["Risk Category", risk]
    ]

    table = Table(data, colWidths=[250, 200])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)

    # ===== Build PDF =====
    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer,
                     as_attachment=True,
                     download_name="Insurance_Report.pdf",
                     mimetype='application/pdf')
    
if __name__ == "__main__":
    app.run(debug=True)