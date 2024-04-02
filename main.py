from flask import Flask, render_template, request, redirect, url_for, session,send_from_directory
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

app = Flask(__name__, static_url_path='/static')

app.secret_key = 'welcome'

# Initialize web3 and other global variables
blockchain_address = 'http://127.0.0.1:9545'
web3 = Web3(HTTPProvider(blockchain_address))
admin_account = web3.eth.accounts[0]
#####################
#####################################################

def readDetails(contract_type):
    global details
    details = ""
    blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    admin_account = web3.eth.accounts[0]
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
    admin_account = web3.eth.accounts[0]
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
        

@app.route('/transfer_credits', methods=['GET', 'POST'])
def transfer_credits_form():
    if request.method == 'POST':
        recipient = request.form['recipient']
        amount = int(request.form['amount'])
        # Instead of calling the transfer function here, we will simply render the template
        return render_template('transfer_credits.html')
    else:
        return render_template('transfer_credits.html')
    


@app.route('/ViewCertificates', methods=['GET', 'POST'])
def ViewCertificates():
    if request.method == 'GET':
        output = '<table border=1 align=center width=100%>'
        font = '<font size="" color="black">'
        arr = ['Student ID', 'Student Name', 'Course Name', 'Contact No', 'Address Details', 'Date & Time',
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

@app.route('/AddCertificateAction', methods=['GET', 'POST'])
def AddCertificateAction():
    if request.method == 'POST':
        global sid
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
            digital_signature = sha256(contents).hexdigest();
            # url = pyqrcode.create(sid)
            # url.png('static/qrcode/'+sid+'.png', scale = 6)
            data = sid + "#" + sname + "#" + course + "#" + contact + "#" + address + "#" + str(
                current_time) + "#" + digital_signature + "\n"
            saveDataBlockChain(data, "certificate")
            context = "Certificate details added with id : " + sid + "<br/>Generated Digital Signatures : " + digital_signature
            return render_template('Download.html', msg=context)
        else:
            context = "Given " + sid + "already exists"
            return render_template('Download.html', msg=context)

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
        arr = ['Student ID', 'Student Name', 'Course Name', 'Contact No', 'Address Details', 'Date & Time',
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


if __name__ == '__main__':
    app.run()
