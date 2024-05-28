from tkinter import Tk, Text, Button, Scrollbar
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk
import tkinter
import numpy as np
import cv2
import json
from web3 import Web3, HTTPProvider
import traceback

main = Tk()
main.title("Hall Ticket Verification") 
main.geometry("1300x1200")

global details

def readDetails(contract_type):
    global details
    details = ""
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'CertificateVerification.json' 
    deployed_contract_address = '0xe68FD04167a523932c89a02B80f2815B9AF23818' 
    with open(compiled_contract_path) as file:
        contract_json = json.load(file) 
        contract_abi = contract_json['abi']  
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) 
    if contract_type == 'company':
        details = contract.functions.getCompanyDetails().call()
    if contract_type == 'certificate':
        details = contract.functions.getCertificateDetails().call()
    if contract_type == 'hallticket':
        details = contract.functions.getHallTicketDetails().call()
    if len(details) > 0:
        if 'empty' in details:
            details = details[5:len(details)]        

def validateDetails(data):
    readDetails('hallticket')
    arr = details.split("\n")
    flag = 0
    for entry in arr:
        array = entry.split("#")
        if array[0].strip() == data.strip():
            text.delete('1.0', 'end')
            text.insert('end', 'Student Roll No  : ' + array[0] + "\n")
            text.insert('end', 'Digital Signature: ' + array[1]+"\n")
            text.insert('end', "Hall Ticket Verified Successfully")
            text.update_idletasks()
            flag = 1
            break

    if flag == 0:
        text.delete('1.0', 'end')
        text.insert('end', "Hall Ticket Verification Failed. Roll No not found in blockchain data")
        text.update_idletasks()

def runWebCam():
    global emp_id, present_date
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    try:
        while True:
            _, img = cap.read()
            data, bbox, _ = detector.detectAndDecode(img)
            if bbox is not None:
                for i in range(len(bbox)):
                    cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255, 0, 0), thickness=2)
            if data:
                validateDetails(str(data))
            cv2.imshow("QR Code Scanner", img)
            if cv2.waitKey(1) == ord("q"):
                break
    except Exception:
        traceback.print_exc()
        pass
    cap.release()
    cv2.destroyAllWindows()        
            
def exit():
    main.destroy()

font = ('Arial', 13, 'bold')
title = tkinter.Label(main, text='Hall Ticket Verification')
title.config(bg='mediumorchid', fg='white')  
title.config(font=font)           
title.config(height=3, width=120)       
title.pack()

frame = ttk.Frame(main, padding="20")
frame.pack(expand=True)

font1 = ('Arial', 12, 'bold')
text = Text(frame, height=20, width=100)
scroll = Scrollbar(frame, command=text.yview)
text.configure(yscrollcommand=scroll.set)
text.pack(side="left", fill="both", expand=True)
scroll.pack(side="right", fill="y")

uploadButton = Button(main, text="Start Webcam", command=runWebCam)
uploadButton.config(font=font1)  
uploadButton.pack(pady=10)

exitButton = Button(main, text="Exit", command=exit)
exitButton.config(font=font1) 
exitButton.pack(pady=10)

main.config(bg='lightgray')
main.mainloop()
