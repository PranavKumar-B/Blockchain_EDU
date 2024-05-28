from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import json
from web3 import Web3, HTTPProvider
import hashlib
from hashlib import sha256
import os
import datetime
import pyqrcode
import png
from pyqrcode import QRCode
import json
from pymongo import MongoClient
from flask import send_file

app = Flask(__name__, static_url_path='/static')

app.secret_key = 'welcome'

# Initialize web3 and other global variables
blockchain_address = 'http://127.0.0.1:9545'
web3 = Web3(HTTPProvider(blockchain_address))
# admin_account = web3.eth.accounts[0]
web3.eth.defaultAccount = web3.eth.accounts[0]

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['Project']
collection = db['students']
collection2 = db['halltickets']
collection3 = db['collection']
courses_collection = db['courses']
status_collection = db['status']

#####################
#####################################################

import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

def generate_hall_ticket(name, roll_no, department, student_photo_path, course_details):
    # Get the current directory of the script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(script_dir, "hall_ticket.pdf")
    
    # Create a PDF canvas
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Set up some basic formatting
    c.setFont("Helvetica", 12)
    
    # Add college emblem
    emblem_path = os.path.join(script_dir, "college_emblem.png")
    c.drawImage(emblem_path, 50, 650, width=100, height=100, preserveAspectRatio=True)
    
    # Add student photo
    # c.drawImage(student_photo_path, 400, 650, width=100, height=100, preserveAspectRatio=True)
    
    # Add student information
    c.drawString(150, 630, f"Name: {name}")
    c.drawString(150, 615, f"Roll Number: {roll_no}")
    c.drawString(150, 600, f"Department: {department}")
    
    # Add course details table
    table_data = [["Course Name", "Course ID", "Credits"]] + course_details
    table = Table(table_data)
    table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black)]))
    table.wrapOn(c, 400, 200)
    table.drawOn(c, 100, 450)
    
    # Add signatures
    c.drawString(100, 400, "Signature of Dean")
    c.drawString(400, 400, "Signature of Student")
    
    # Save the PDF
    c.save()



def generate_completion_certificate(student_name, roll_no, course_name, course_credits, course_code, grade):
    # Get the current directory of the script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(script_dir, "completion_certificate.pdf")
    
    # Create a PDF canvas
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Set up some basic formatting
    c.setFont("Helvetica", 12)  # Set font
    line_height = 25  # Define line height
    
    # Add university logo
    logo_path = os.path.join(script_dir, "college_emblem.png")
    c.drawImage(logo_path, 200, 650, width=200, height=100, preserveAspectRatio=True)
    
    # Add margin on top for the logo
    c.drawString(0, 630, "")
    
    # Add student name, roll number, course details
    c.drawString(50, 610, f"Student Name: {student_name}")
    c.drawString(50, 590, f"Roll Number: {roll_no}")
    c.drawString(50, 570, f"Course Name: {course_name}")
    c.drawString(50, 550, f"Course Credits: {course_credits}")
    c.drawString(50, 530, f"Course Code: {course_code}")
    
    # Add grade received
    c.drawString(50, 510, f"Grade Received: {grade}")
    
    # Add fancy border
    c.setStrokeColor(colors.black)
    c.rect(30, 650, 550, -250, stroke=1, fill=0)
    
    # Add signature line
    c.line(350, 430, 550, 430)
    
    # Add signature of dean
    c.drawString(400, 420, "Signature of Dean")
    
    # Save the PDF
    c.save()

    with open(output_path, 'rb') as f:
        certificate_data = f.read()
    
    return certificate_data



def readDetails(contract_type):
    global details
    details = ""
    blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    # admin_account = web3.eth.accounts[0]
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'CertificateVerification.json' #certification verification contract code
    deployed_contract_address = '0xe68FD04167a523932c89a02B80f2815B9AF23818' #hash address to access certification verification contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'company':
        details = contract.functions.getCompanyDetails().call()
    if contract_type == 'certificate':
        details = contract.functions.getCertificateDetails().call()
    if contract_type == 'hallticket':
        details = contract.functions.getHallTicketDetails().call()
    
    if len(details) > 0:
        if 'empty' in details:
            details = details[5:len(details)]    
    print(details)    

def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    # admin_account = web3.eth.accounts[0]
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'CertificateVerification.json' #certification verification contract file
    deployed_contract_address = '0xe68FD04167a523932c89a02B80f2815B9AF23818' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'company':
        details+=currentData
        msg = contract.functions.setCompanyDetails(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'certificate':
        details+=currentData
        msg = contract.functions.setCertificateDetails(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'hallticket':
        details+=currentData
        msg = contract.functions.setHallTicketDetails(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)

# Function to check if Metamask is installed and retrieve the user's Ethereum address
def check_metamask():
    if not web3.isConnected():
        return None
    if not web3.eth.accounts:
        return None
    return web3.eth.accounts[0]


# def transfer_credits(recipient, amount):
#     compiled_contract_path = 'CertificateVerification.json' #certification verification contract code
#     deployed_contract_address = '0xe68FD04167a523932c89a02B80f2815B9AF23818' #hash address to access certification verification contract
#     with open(compiled_contract_path) as file:
#         contract_json = json.load(file)  # load contract info as JSON
#         contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
#     file.close()
#     contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
#     tx_hash = contract.functions.transfer(recipient, amount).transact()
#     web3.eth.waitForTransactionReceipt(tx_hash)

# # Route for the transfer credits form
# @app.route('/transfer_credits', methods=['GET', 'POST'])
# def transfer_credits_form():
#     if request.method == 'POST':
#         recipient = request.form['recipient']
#         amount = int(request.form['amount'])
#         transfer_credits(recipient, amount)
#         return "Credits transferred successfully"
#     else:
#         return render_template('transfer_credits.html')


#req
@app.route('/req')
def req():
    # Get the Ethereum account address from the query parameters
    ethereum_account = request.args.get('account')

    # Perform authentication using the Ethereum account address
    if ethereum_account == web3.eth.accounts[0]:  # Replace with your admin account address
        # If authentication is successful, redirect to the admin panel
        return redirect(url_for('admin_panel'))
    else:
        # If authentication fails or the account is not authorized, render the Metamask login page with an error message
        return render_template('Student.html')

# Admin panel route
@app.route('/admin_panel')
def admin_panel():
    # Render the admin panel template
    return render_template('AdminScreen.html')


# Metamask login route
@app.route('/metamask_login')
def metamask_login():
    ethereum_address = check_metamask()
    print("Detected Ethereum Address:", ethereum_address)
    if ethereum_address:
        # If Metamask is installed and user is logged in, redirect to admin panel
        return render_template('AdminScreen.html', msg="Welcome ")
    else:
        # If Metamask is not installed or user is not logged in, render Metamask login page
        return render_template('metamask_login.html')

# Admin login action route
@app.route('/AdminLoginAction', methods=['POST'])
def AdminLoginAction():
    ethereum_address = check_metamask()
    if ethereum_address:
        print("Detected Ethereum Address:", ethereum_address)
        # If Metamask is installed and user is logged in, redirect to admin panel
        return render_template('AdminScreen.html', msg="Welcome ")
    else:
        # If Metamask is not installed or user is not logged in, render Metamask login page with error message
        return render_template('metamask_login.html', msg='Metamask account not detected. Please login with Metamask.')

# Index route
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', msg='')

@app.route('/Login', methods=['GET', 'POST'])
def Login():
    return render_template('Login.html', msg='')

@app.route('/AdminLogin', methods=['GET', 'POST'])
def AdminLogin():
    return render_template('login_with_metamask.html', msg='')

# @app.route('/AdminLoginAction', methods=['GET', 'POST'])
# def AdminLoginAction():
#     global uname
#     if request.method == 'POST' and 't1' in request.form and 't2' in request.form:
#         user = request.form['t1']
#         password = request.form['t2']
#         if user == "admin" and password == "admin":
#             return render_template('AdminScreen.html', msg="Welcome "+user)
#         else:
#             return render_template('Login.html', msg="Invalid login details")



# @app.route('/student_login', methods=['GET', 'POST'])
# def student_login():
#     if request.method == 'POST':
#         rollno = request.form['rollno']
#         password = request.form['password']
        
#         # Query the MongoDB collection to check if the roll number and password match
#         student = collection.find_one({"Rollno": int(rollno), "password": password})
#         if student:
#             # If credentials are valid, redirect to a page displaying name and credits
#             return redirect(url_for('student_dashboard', rollno=rollno))
#         else:
#             # If credentials are invalid, render the login page with an error message
#             return render_template('student_login.html', msg='Invalid credentials')
#     else:
#         # If request method is GET, render the login page
#         return render_template('student_login.html', msg='')


@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        rollno = request.form['rollno']
        password = request.form['password']
        
        # Query the MongoDB collection to check if the roll number and password match
        student = collection.find_one({"Rollno": int(rollno), "password": password})
        if student:
            # If credentials are valid, redirect to student_dashboard route
            return redirect(url_for('student_dashboard', rollno=rollno))
        else:
            # If credentials are invalid, render the login page with an error message
            return render_template('student_login.html', msg='Invalid credentials')
    else:
        # If request method is GET, render the login page
        return render_template('student_login.html', msg='')


# @app.route('/student_dashboard/<int:rollno>')
# def student_dashboard(rollno):
#     # Query the MongoDB collection to get the student details
#     student = collection.find_one({"Rollno": rollno})
#     if student:
#         # If student is found, render a dashboard page displaying their name and credits
#         return render_template('student_dashboard.html', name=student['Name'],rollno=student['Rollno'], credits=student['Credits'])
#     else:
#         # If student is not found, render an error page
#         return render_template('error.html', msg='Student not found')
    
#17.04

# @app.route('/student_dashboard/<int:rollno>')
# def student_dashboard(rollno):
#     # Query the MongoDB collection to get the student details
#     student = collection.find_one({"Rollno": rollno})
#     if student:
#         # If student is found, render a dashboard page displaying their name and credits
#         # Retrieve the certificate data from the MongoDB collection
#         certificate_data = collection2.find_one({"student_id":student['Rollno']})
#         if certificate_data:
#             # Assuming the certificate is stored in a PDF format, you can convert the binary data to a file
#             with open('certificate.pdf', 'wb') as file:
#                 file.write(certificate_data['hall_ticket'])
            
#             # Render the student_dashboard.html file with the certificate
#             return render_template('student_dashboard.html', name=student['Name'],rollno=student['Rollno'], credits=student['Credits'], certificate='certificate.pdf')
#         else:
#             # If certificate data is not found, render the dashboard without the certificate
#             return render_template('student_dashboard.html', name=student['Name'],rollno=student['Rollno'], credits=student['Credits'], certificate=None)
#     else:
#         # If student is not found, render an error page
#         return render_template('error.html', msg='Student not found')

from flask import send_file
from io import BytesIO


@app.route('/student_dashboard/<int:rollno>')
def student_dashboard(rollno):
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    # admin_account = web3.eth.accounts[0]
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'CertificateVerification.json' #certification verification contract file
    deployed_contract_address = '0xe68FD04167a523932c89a02B80f2815B9AF23818' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    # Query the MongoDB collection to get the student details
    student = collection.find_one({"Rollno": rollno})
    total_credits = contract.functions.getTotalCreditsByRollNo(rollno).call()
    if student:
        certificate_data = collection2.find_one({"student_id": student['Rollno']})
        if certificate_data:
            # Write the hall ticket PDF data to a file
            with open('certificate.pdf', 'wb') as file:
                file.write(certificate_data['hall_ticket'])
            
            # Write the QR code PNG data to a file
            with open('qr_code.png', 'wb') as file:
                file.write(certificate_data['qr_code'])
        
        # If student is found, retrieve completed and in-progress courses
        completed_courses = status_collection.find({"Rollno": rollno, "Status": 1})
        in_progress_courses = status_collection.find({"Rollno": rollno, "Status": 0})
        
        # Prepare data for the completed courses table
        completed_courses_data = []
        for course in completed_courses:
            course_data = {
                "Course ID": course["Course_Code"],
                "Course Name": course["Course_Name"],
                "Credits": course["Credits"]
            }
            completed_courses_data.append(course_data)
        
        # Prepare data for the in-progress courses table
        in_progress_courses_data = []
        for course in in_progress_courses:
            course_data = {
                "Course ID": course["Course_Code"],
                "Course Name": course["Course_Name"],
                "Credits": course["Credits"]
            }
            in_progress_courses_data.append(course_data)
        
        # Render the student_dashboard.html file with the data for both tables
        return render_template('student_dashboard.html', 
                               name=student['Name'],
                               rollno=student['Rollno'], 
                               credits=total_credits, 
                               completed_courses=completed_courses_data,
                               in_progress_courses=in_progress_courses_data,
                               certificate='certificate.pdf',
                               qr_code='qr_code.png')
    else:
        # If student is not found, render an error page
        return render_template('error.html', msg='Student not found')

@app.route('/download_qr/<int:rollno>')
def download_qr(rollno):
    certificate_data = collection2.find_one({"student_id": rollno})
    if certificate_data and 'qr_code' in certificate_data:
        with open('qr_code.png', 'wb') as file:
            file.write(certificate_data['qr_code'])
        x="qr_code.png"
        # Send the QR code file for download
        return send_file(x,as_attachment=True)
    else:
        return "QR code not found."

 
import tempfile
from flask import send_file, make_response

@app.route('/download_certificate/<int:rollno>/<course_id>')
def download_certificate(rollno, course_id):
    # Query the MongoDB collection to get the certificate data
    certificate_data = status_collection.find_one({"Rollno": int(rollno), "Course_Code": str(course_id)})
    if certificate_data:
        with open('certificate.pdf', 'wb') as file:
                file.write(certificate_data['Completion_Certificate'])
        abc="certificate.pdf"
        return send_file(abc,as_attachment=True)
    else:
        return jsonify({'success': False, 'message': 'Certificate not found'})







@app.route('/certificate/<filename>')
def certificate_file(filename):
    return send_file(filename, as_attachment=True)



######################

@app.route('/Signup', methods=['GET', 'POST'])
def Signup():
    return render_template('Signup.html', msg='')

@app.route('/LoginAction', methods=['GET', 'POST'])
def LoginAction():
    global uname
    if request.method == 'POST' and 't1' in request.form and 't2' in request.form:
        user = request.form['t1']
        password = request.form['t2']
        status = "none"
        readDetails('company')
        arr = details.split("\n")
        for i in range(len(arr) - 1):
            array = arr[i].split("#")
            if array[0] == user and array[1] == password:
                uname = user
                status = "success"
                break
        if status == "success":
            return render_template('UserScreen.html', msg="Welcome " + uname)
        else:
            return render_template('Login.html', msg="Invalid login details")
        

##17.04
        
# @app.route('/transfer_credits', methods=['GET', 'POST'])
# def transfer_credits_form():
#     if request.method == 'POST':
#         student_id = request.form['student_id']
#         course_code = request.form['course_code']
        
#         # Fetch credits for the selected course
#         course = courses_collection.find_one({"Course_Code": course_code})
#         if course:
#             credits = course["Credits"]
#             # Update student's credits in the status collection
#             collection.update_one({"Rollno": student_id}, {"$inc": {"Credits": credits}})
#             return "Credits transferred successfully!"
#         else:
#             return "Course not found!"
#     else:
#         # Fetch students' names and IDs from status collection
#         students = collection.find({}, {"_id": 0, "Rollno": 1})
#         student_list = [(student["Rollno"]) for student in students]

#         # Fetch courses' names from courses collection
#         courses = courses_collection.find({}, {"_id": 0, "Course_Name": 1, "Course_Code": 1})
#         course_list = [(course["Course_Code"], course["Course_Name"]) for course in courses]
        
#         return render_template('transfer_credits.html', students=student_list, courses=course_list)

import base64
from flask import request

@app.route('/transfer_credits', methods=['GET', 'POST'])
def transfer_credits_form():
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    # admin_account = web3.eth.accounts[0]
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'CertificateVerification.json' #certification verification contract file
    deployed_contract_address = '0xe68FD04167a523932c89a02B80f2815B9AF23818' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        course_code = request.form['course_code']

        # Fetch credits for the selected course
        course = courses_collection.find_one({"Course_Code": course_code})
        current_time = datetime.datetime.now()
        if course:
            credits = course["Credits"]
            # Update student's credits in the student collection
            student = collection.find_one({"Rollno": student_id})
            if student:
                old_credits = student.get("Credits", 0)
                new_credits = old_credits + credits
                collection.update_one({"Rollno": student_id}, {"$set": {"Credits": new_credits}})
                status_collection.update_one({"Rollno": student_id, "Course_Code": course_code},
                                              {"$set": {"Status": 1}})
                
                # Call Solidity contract to update credits
                gas_limit = 5721975
                contract.functions.creditTransfer(student["Name"], student_id, course["Course_Name"], credits).transact()
                # Generate completion certificate and update blockchain
                certificate_data = generate_completion_certificate(student_name=student["Name"],
                                                                   roll_no=student_id,
                                                                   course_name=course["Course_Name"],
                                                                   course_credits=credits,
                                                                   course_code=course_code,
                                                                   grade="A")  # Assuming grade is "A"

                digital_signature = sha256(certificate_data).hexdigest()
                blockchain_data = f"{student_id}#{student['Name']}#{course['Course_Name']}#{credits}#{course_code}#{current_time}#{digital_signature}\n"
                saveDataBlockChain(blockchain_data, "certificate")

                # Update student document with the certificate
                status_collection.update_one({"Rollno": student_id, "Course_Code": course_code},
                                       {"$set": {"Completion_Certificate": certificate_data}})
                
                return "Credits transferred successfully!"
            else:
                return "Student not found!"
        else:
            return "Course not found!"
    else:
        # Fetch students' names and IDs from status collection
        students = collection.find({}, {"_id": 0, "Rollno": 1})
        student_list = [student["Rollno"] for student in students]

        # By default, select the first student
        selected_student_id = int(request.args.get('student_id', student_list[0] if student_list else None))

        # Fetch courses associated with the selected student from status collection
        if selected_student_id:
            student_courses = status_collection.find({"Rollno": selected_student_id, "Status": 0})
            course_list = [(course["Course_Code"], course["Course_Name"]) for course in student_courses]
        else:
            course_list = []

        return render_template('transfer_credits.html', students=student_list, courses=course_list,
                               selected_student_id=selected_student_id)

    

from flask import jsonify

@app.route('/get_courses')
def get_courses():
    student_id = request.args.get('student_id')
    if student_id:
        # student_courses = status_collection.find_one({"Rollno": int(student_id)}, {"_id": 0, "Course_Code": 1, "Course_Name": 1})
        student_courses = status_collection.find({"Rollno": int(student_id),"Status": 0})
        course_list = [(course["Course_Code"], course["Course_Name"]) for course in student_courses]
        print(course_list)
        if course_list:
            return jsonify(list(course_list))
        else:
            return jsonify([])
    else:
        return jsonify([])  # Return empty list if no student ID is provided



@app.route('/transaction_history')
def transaction_history():
    # Call the smart contract function to get all students
    # You need to replace the contract address and ABI with your actual contract address and ABI
    blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    # admin_account = web3.eth.accounts[0]
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'CertificateVerification.json' #certification verification contract code
    deployed_contract_address = '0xe68FD04167a523932c89a02B80f2815B9AF23818' #hash address to access certification verification contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data

    # Call the getAllStudents function
    names, roll_nos, courses, credits = contract.functions.getAllStudents().call()
    unique_courses= contract.functions.getAllCourses().call()
    # unique_courses = contract.functions.getAllUniqueCourses().call()
    unique_courses = set(unique_courses)
    # Get occurrences for each unique course
    course_occurrences = []
    for course in unique_courses:
        occurrences = contract.functions.countCourseOccurrences(course).call()
        course_occurrences.append(occurrences)
    print(unique_courses)

    # Combine data into a list of transactions
    transactions = []
    for i in range(len(names)):
        transaction = f"{credits[i]} credits has been awarded to {names[i]} with roll no {roll_nos[i]} for completing course '{courses[i]}'"
        transactions.append(transaction)

    return render_template('transactionhistory.html', transactions=transactions, unique_courses=unique_courses, course_occurrences=course_occurrences)

@app.route('/ViewCertificates', methods=['GET', 'POST'])
def ViewCertificates():
    if request.method == 'GET':
        output = '<table border=1 align=center width=100%>'
        font = '<font size="" color="black">'
        arr = ['Student ID', 'Student Name', 'Course Name', 'Credits', 'Course Code', 'Date & Time',
               'Certificate Signature (Hashcode)']
        output += "<tr>" 
        for i in range(len(arr)):
            output += "<th>" + font + arr[i] + "</th>"
        readDetails('certificate')
        arr = details.split("\n")
        for i in range(len(arr) - 1):
            array = arr[i].split("#")
            output += "<tr><td>" + font + array[0] + "</td>"
            output += "<td>" + font + array[1] + "</td>"
            output += "<td>" + font + array[2] + "</td>"
            output += "<td>" + font + array[3] + "</td>"
            output += "<td>" + font + array[4] + "</td>"
            output += "<td>" + font + array[5] + "</td>"
            output += "<td>" + font + array[6] + "</td>"
            # output+='<td><img src="/static/qrcode/'+array[0]+'.png" width="200" height="200"></img></td>'
        output += "<br/><br/><br/><br/><br/><br/>"
        return render_template('ViewCertificates.html', msg=output)

@app.route('/ViewCompanies', methods=['GET', 'POST'])
def ViewCompanies():
    if request.method == 'GET':
        output = '<table border=1 align=center width=100%>'
        font = '<font size="" color="black">'
        arr = ['Company Username', 'Phone No', 'Email ID', 'Company Address']
        output += "<tr>"
        for i in range(len(arr)):
            output += "<th>" + font + arr[i] + "</th>"
        readDetails('company')
        arr = details.split("\n")
        for i in range(len(arr) - 1):
            array = arr[i].split("#")
            output += "<tr><td>" + font + array[0] + "</td>"
            output += "<td>" + font + array[2] + "</td>"
            output += "<td>" + font + array[3] + "</td>"
            output += "<td>" + font + array[4] + "</td>"
        output += "<br/><br/><br/><br/><br/><br/>"
        return render_template('ViewCompany.html', msg=output)

@app.route('/SignupAction', methods=['GET', 'POST'])
def SignupAction():
    if request.method == 'POST':
        global details
        uname = request.form['t1']
        password = request.form['t2']
        phone = request.form['t3']
        email = request.form['t4']
        address = request.form['t5']
        status = "none"
        readDetails('company')
        arr = details.split("\n")
        status = "none"
        for i in range(len(arr) - 1):
            array = arr[i].split("#")
            if array[0] == uname:
                status = uname + " Username already exists"
                break
        if status == "none":
            data = uname + "#" + password + "#" + phone + "#" + email + "#" + address + "\n"
            saveDataBlockChain(data, "company")
            context = "Company signup task completed"
            return render_template('Signup.html', msg=context)
        else:
            return render_template('Signup.html', msg=status)

@app.route('/Logout')
def Logout():
    return render_template('index.html', msg='')

@app.route('/AddCertificate', methods=['GET', 'POST'])
def AddCertificate():
    return render_template('AddCertificate.html', msg='')

def checkID(student_id):
    readDetails('certificate')
    arr = details.split("\n")
    flag = False
    for i in range(len(arr) - 1):
        array = arr[i].split("#")
        if array[0] == student_id:
            flag = true
            break
    return flag


@app.route('/DownloadAction', methods=['GET', 'POST'])
def DownloadAction():
    if request.method == 'POST':
        global sid
        print("===="+sid)
        return send_from_directory('static/qrcode/', sid+'.png', as_attachment=True)


######################
# @app.route('/hallticket_generation', methods=['GET', 'POST'])
# def hallticket_generation():
#     if request.method == 'GET':
#         # Fetch students' names and roll numbers from MongoDB
#         students = collection.find({}, {"_id": 0, "Name": 1, "Rollno": 1})
#         student_list = [{"name": student["Name"], "rollno": student["Rollno"]} for student in students]
#         return render_template('hallticket_generation.html', students=student_list)
#     elif request.method == 'POST':
#         # Retrieve selected student's roll number from the form
#         roll_no = request.form['student']
#         print("Received roll number:", roll_no)
        
#         # Query the MongoDB collection to get the student's details
#         # student = collection.find_one({"Rollno": roll_no})
#         student = collection.find_one({"Rollno": int(roll_no)})
#         if student:
#             # Retrieve the student's courses
#             course_details = [
#                 [course["course_name"], course["course_id"], course["credits"]]
#                 for course in collection3.find({"studid": str(student['Rollno'])})
#             ]
            
#             # Call generate_hall_ticket function directly
#             generate_hall_ticket(student['Name'], student['Rollno'],"cse", "default_photo.jpg", course_details)
            
#             # Return a response indicating success
            
#             return send_file("hall_ticket.pdf", as_attachment=True)
#         else:
#             # Return a response indicating failure
#             return "Student not found."

#########################



@app.route('/hallticket_generation', methods=['GET', 'POST'])
def hallticket_generation():
    if request.method == 'GET':
        # Fetch students' names and roll numbers from MongoDB
        students = collection.find({}, {"_id": 0, "Name": 1, "Rollno": 1})
        student_list = [{"name": student["Name"], "rollno": student["Rollno"]} for student in students]
        return render_template('hallticket_generation.html', students=student_list)
    
    elif request.method == 'POST':
    # Retrieve selected student's roll number from the form
        roll_no = request.form['student']
        print("Received roll number:", roll_no)
        
        # Query the MongoDB collection to get the student's details
        student = collection.find_one({"Rollno": int(roll_no)})
        if student:
            # Retrieve the student's courses
            course_details = [
                [course["Course_Name"], course["Course_Code"], course["Credits"]]
                for course in status_collection.find({"Rollno": int(student['Rollno'])})
            ]
            print(course_details)
            # Generate the hall ticket PDF
            generate_hall_ticket(student['Name'], student['Rollno'],"cse", "default_photo.jpg", course_details)
            
            # Convert the generated PDF file into bytes
            with open("hall_ticket.pdf", "rb") as file:
                pdf_bytes = file.read()
            
            digital_signature = sha256(pdf_bytes).hexdigest()

            # Generate QR code
            qr_code = pyqrcode.create(str(student['Rollno']))
            qr_code.png('static/qrcode/'+str(student['Rollno'])+'.png', scale=6)
            
            # Convert QR code image to bytes
            with open('static/qrcode/'+str(student['Rollno'])+'.png', 'rb') as qr_file:
                qr_bytes = qr_file.read()

            # Store the hall ticket PDF bytes and QR code bytes in MongoDB
            hall_ticket_data = {
                "student_id": student['Rollno'],
                "hall_ticket": pdf_bytes,
                "qr_code": qr_bytes,
                "generation_time": datetime.datetime.now()
            }

            blockchain_data1 = str(student['Rollno']) + "#" + digital_signature + "\n"
            saveDataBlockChain(blockchain_data1, "hallticket")
            # Insert data into MongoDB collection
            collection2.insert_one(hall_ticket_data)

            # Return a response indicating success
            return "Hall ticket generated successfully"
        else:
            # Return a response indicating failure
            return "Student not found."




@app.route('/AddCertificateAction', methods=['GET', 'POST'])
def AddCertificateAction():
    if request.method == 'POST':
        sid = request.form['t1']
        sname = request.form['t2']
        course = request.form['t3']
        contact = request.form['t4']
        address = request.form['t5']
        certificate = request.files['t6']
        contents = certificate.read()
        current_time = datetime.datetime.now()
        flag = checkID(sid)
        if flag == False:
            digital_signature = sha256(contents).hexdigest()
            url = pyqrcode.create(sid)
            url.png('static/qrcode/'+sid+'.png', scale = 6)
            data = {
                "student_id": sid,
                "student_name": sname,
                "course_name": course,
                "contact_no": contact,
                "address": address,
                "upload_time": current_time,
                "digital_signature": digital_signature
            }

            data2 = {
            "student_id": sid,
            "certificate": contents,
            "upload_time": datetime.datetime.now()
        }
            # Save data to MongoDB
            collection2.insert_one(data2)
            # Blockchain related functionality
            blockchain_data = sid + "#" + sname + "#" + course + "#" + contact + "#" + address + "#" + str(
                current_time) + "#" + digital_signature + "\n"
            saveDataBlockChain(blockchain_data, "certificate")
            # context = "Certificate details added with id : " + sid + "<br/>Generated Digital Signatures : " + digital_signature
            context = "Certificate details added with id : "+sid+"<br/>Generated Digital Signatures : "+digital_signature+"<br/>Download QR CODE"
            return render_template('Download.html', msg=context)
        else:
            context = "Given " + sid + "already exists"
            return render_template('Download.html', msg=context)


# @app.route('/AddCertificateAction', methods=['GET', 'POST'])
# def AddCertificateAction():
#     if request.method == 'POST':
#         global sid
#         sid = request.form['t1']
#         sname = request.form['t2']
#         course = request.form['t3']
#         contact = request.form['t4']
#         address = request.form['t5']
#         certificate = request.files['t6']
#         contents = certificate.read()
#         current_time = datetime.datetime.now()
#         flag = checkID(sid)
#         if flag == False:
#             digital_signature = sha256(contents).hexdigest();
#             # url = pyqrcode.create(sid)
#             # url.png('static/qrcode/'+sid+'.png', scale = 6)
#             data = sid + "#" + sname + "#" + course + "#" + contact + "#" + address + "#" + str(
#                 current_time) + "#" + digital_signature + "\n"
#             saveDataBlockChain(data, "certificate")
#             context = "Certificate details added with id : " + sid + "<br/>Generated Digital Signatures : " + digital_signature
#             return render_template('Download.html', msg=context)
#         else:
#             context = "Given " + sid + "already exists"
#             return render_template('Download.html', msg=context)

@app.route('/AuthenticateScan', methods=['GET', 'POST'])
def AuthenticateScan():
    return render_template('AuthenticateScan.html', msg='')

@app.route('/AuthenticateScanAction', methods=['GET', 'POST'])
def AuthenticateScanAction():
    if request.method == 'POST':
        barcode = request.files['t1']
        contents = barcode.read()
        digital_signature = sha256(contents).hexdigest();
        output = '<table border=1 align=center width=100%>'
        font = '<font size="" color="black">'
        arr = ['Student RollNo', 'Student Name', 'Course Name', 'Credits', 'Course Code', 'Date & Time',
               'Certificate Signature (Hash Code)', 'Status']
        output += "<tr>"
        for i in range(len(arr)):
            output += "<th>" + font + arr[i] + "</th>"
        readDetails('certificate')
        arr = details.split("\n")
        flag = 0
        for i in range(len(arr) - 1):
            array = arr[i].split("#")
            if array[6] == digital_signature:
                flag = 1
                output += "<tr><td>" + font + array[0] + "</td>"
                output += "<td>" + font + array[1] + "</td>"
                output += "<td>" + font + array[2] + "</td>"
                output += "<td>" + font + array[3] + "</td>"
                output += "<td>" + font + array[4] + "</td>"
                output += "<td>" + font + array[5] + "</td>"
                output += "<td>" + font + array[6] + "</td>"
                output += "<td>" + font + "Authentication Successfull" + "</td>"
        if flag == 0:
            output += "<tr><td><td><td><td><td><td><td><td>Uploaded Certificate Authentication Failed</td></tr>"
        output += "<br/><br/><br/><br/><br/><br/>"
        return render_template('ViewDetails.html', msg=output)
    
import pandas as pd
import numpy as np
@app.route('/uploadcsv')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file:
        # Read the Excel file into a pandas DataFrame
        df = pd.read_csv(file, delimiter=',')
        print(df)
        # Convert 'Rollno' column to integer
        df['Rollno'] = df['Rollno'].astype(int)
        df['Completion_Certificate'].replace(np.nan, None, inplace=True)

        # Convert DataFrame to dictionary records
        data = df.to_dict(orient='records')

        # Insert each record into MongoDB collection
        for record in data:
            record['Status'] = 0  # Set status field to 0
            status_collection.insert_one(record)

        return 'File uploaded successfully'
    else:
        return 'File upload failed'
    


###

@app.route('/addstudent')
def upload_form_stud():
    return render_template('addstud.html')

@app.route('/uploadstud', methods=['POST'])
def upload_file_stud():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(file)
        
        # Convert relevant columns to integer
        df['Rollno'] = df['Rollno'].astype(int)
        df['Credits'] = df['Credits'].astype(int)
        
        # Fill NaN values in 'PrivAddr' column with None
        df['PrivAddr'].fillna(value=np.nan, inplace=True)

        # Convert DataFrame to dictionary records
        data = df.to_dict(orient='records')

        # Insert each record into MongoDB collection
        for record in data:
            collection.insert_one(record)

        return 'File uploaded successfully'
    else:
        return 'File upload failed'


if __name__ == '__main__':
    app.run()
