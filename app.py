from flask import Flask, render_template, request, redirect, session
from db import Base, engine, SessionLocal
import model
import PyPDF2
import docx 
import json
from ai import analyze_resume

app = Flask(__name__)
app.secret_key = "secret123" 

Base.metadata.create_all(bind=engine)

#Home
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

#singup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    db = SessionLocal()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = db.query(model.User).filter_by(email=email).first()
        if existing_user:
            return "User already exist"
        
        user =model.User(email=email, password=password)
        db.add(user)
        db.commit()

        return redirect("/login")
    return render_template("signup.html")

#login
@app.route("/login", methods=["GET", "POST"])
def login():
    db = SessionLocal()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.query(model.User).filter_by(email=email, password=password).first()

        if user:
            session["user"] = user.email
            return redirect("/dashboard")
        else:
            return "Invalid Credential"
        
    return render_template("login.html")

#Dashboard
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":
        user_goal = request.form.get("role")
        resume_text = request.form.get("resume")

        file = request.files.get("file")

        # Handle uploaded file
        if file and file.filename != "":

            # PDF
            if file.filename.lower().endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""

                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""

                    resume_text = text

                except Exception as e:
                    result = {"error": f"PDF Error: {str(e)}"}

            # DOCX
            elif file.filename.lower().endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text = ""

                    for para in doc.paragraphs:
                        text += para.text + "\n"

                    resume_text = text

                except Exception as e:
                    result = {"error": f"DOCX Error: {str(e)}"}

        if resume_text and user_goal and result is None:
            try:
                result = analyze_resume(resume_text, user_goal)

                db = SessionLocal()

                user = db.query(model.User).filter_by(
                    email=session["user"]
                ).first()

                report = model.Report(
                    user_id=user.id,
                    resume_text=resume_text,
                    result=json.dumps(result)
                )

                db.add(report)
                db.commit()

            except Exception as e:
                result = {"error": f"AI Error: {str(e)}"}

    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )

@app.route("/history", methods=["GET", "POST"])
def history():
    if "user" not in session:
        return redirect("/login")
    
    db = SessionLocal()
    user = db.query(model.User).filter_by(email=session["user"]).first()

    report = db.query(model.Report).filter_by(user_id = user.id).all()

    pasred_reports = []
    for r in report:
                try:
                    pasred_result = json.loads(r.result)
                except:
                    pasred_reports =[]

                pasred_reports.append({
                    "resume": r.resume_text,
                    "result": pasred_result
                })
    return render_template("history.html", reports = pasred_reports)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user", None)
    return redirect("/login")
 

if __name__== "__main__":
    app.run(debug=True)