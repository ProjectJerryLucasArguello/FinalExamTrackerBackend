from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail, Message
#Set up database

# MySQL / MariaDB
#mysql://scott:tiger@localhost/project

app = Flask(__name__)
CORS(app) 

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:examplepassword@db/njit_finals_locations'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:OzonatedWater%402@localhost/njit_finals_locations'
app.config['SECRET_KEY'] ="secretKey for security"
db = SQLAlchemy(app)

#Input the data from the database given what I have inputted in the MySQL database
class ExamsLocations(db.Model):
    __tablename__= 'testinglocations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # New unique primary key
    Exam_Component_ID = db.Column(db.Integer)
    Title = db.Column(db.String(100))
    Date_of_Test = db.Column(db.String(20)) 
    Time_of_Test = db.Column(db.String(20))
    Building = db.Column (db.String(20))
    Room = db.Column(db.String(20))
    Instructor = db.Column(db.String(50))
    class_name= db.Column(db.String(10))  # `class` renamed to `class_name` to avoid conflict with Python keyword
    class_level = db.Column(db.String(10))
    

@app.route('/get_exam_info', methods=['POST'])
def get_exam_info():
    # Parse JSON array from request body
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Request data must be a JSON array"}), 400

    # Collect results for each parameter set
    all_results = []

    for params in data:
        exam_component_id = params.get('Exam_Component_ID')
        class_name = params.get('class')
        class_level = params.get('class_level')

        # Query database for each parameter set
        results = db.session.query(
            ExamsLocations.Exam_Component_ID,
            ExamsLocations.Title,
            ExamsLocations.Date_of_Test,
            ExamsLocations.Time_of_Test,
            ExamsLocations.Building,
            ExamsLocations.Room,
            ExamsLocations.Instructor,
            ExamsLocations.class_name,
            ExamsLocations.class_level
        ).filter_by(
            Exam_Component_ID=exam_component_id,
            class_name=class_name,
            class_level=class_level
        ).all()
  # If no results, add a message indicating no class was found
        if not results:
            all_results.append({
                "Exam_Component_ID": exam_component_id,
                "class": class_name,
                "class_level": class_level,
                "message":  f"""No class was found given the information provided:
                            Exam Component ID: {exam_component_id}, Class: {class_name}, Class Level: {class_level}.
                            Please refer back to "https://www.njit.edu/registrar/exams/finalexams.php" OR speak with your instructor.
                            """
            })
        else:
            # Append each found exam detail to all_results
            exams = [{
                'Exam_Component_ID': result.Exam_Component_ID,
                'Title': result.Title,
                'Date_of_Test': result.Date_of_Test,
                'Time_of_Test': result.Time_of_Test,
                'Building': result.Building,
                'Room': result.Room,
                'Instructor': result.Instructor,
                'class': result.class_name,
                'class_level': result.class_level
            } for result in results]
            all_results.extend(exams)

    return jsonify(all_results)

    # Configure email settings
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='jerryarg1120@gmail.com',
    MAIL_PASSWORD='ijeoiaxoadelfejw',
    MAIL_DEFAULT_SENDER='jerryarg1120@gmail.com'  # Add default sender
)


mail = Mail(app)

@app.route('/send_exam_info', methods=['POST'])
def send_exam_info():
    data = request.get_json()
    email = data.get("email")
    exam_info = data.get("exam_info")

    # Compose email body with exam details
    message_body = "Exam Details:\n\n"
    for exam in exam_info:
        message_body += f"Exam Component ID: {exam['Exam_Component_ID']}\n"
        message_body += f"Title: {exam['Title']}\n"
        message_body += f"Date of Test: {exam['Date_of_Test']}\n"
        message_body += f"Time of Test: {exam['Time_of_Test']}\n"
        message_body += f"Building: {exam['Building']}\n"
        message_body += f"Room: {exam['Room']}\n"
        message_body += f"Instructor: {exam['Instructor']}\n\n"

    # Send email
    msg = Message("Your Exam Information", recipients=[email], body=message_body)
    try:
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()

#  python info_retrevial.py <-- If we want to run it again, make sure you in the right directory


#Create Input for mutiple parameters,
#should retreieve the information
#Now I need to implement a condition where if the parameters find no existing parameters 
#It should say "no class was found given the information" 
#Taking the information provided in a JSON file 
#I need to organized into a table
#Then provide the option to send via email