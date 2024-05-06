import logging
from flask import Flask, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
import requests
import os
import email
import bleach
import hashlib
import uuid
import rsa
import base64
from subprocess import Popen, PIPE

app = Flask(__name__)
strs3cr3txDLL = './helpers/s3cr3tx.dll'
strPEMfileName = ''
        
# to_email = "recipient@example.com"
# from_email = "your_email@example.com"
# smtp_server = "smtp.example.com"
# smtp_port = 587  # Typically 587 for TLS
# smtp_user = "your_username"
# smtp_password = "your_password"
# subject = "Test Email"
# message_body = "This is a test email sent via Python."

# app.config['SECRET_KEY'] = 'your_secret_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
# with app.app_context():
#     db = app.db
#     class User(db.Model):
#         id = db.Column(app.db.Integer, primary_key=True)
#         username = db.Column(app.db.String(80), unique=True, nullable=False)
#         email = db.Column(app.db.String(120), unique=True, nullable=False)

def protect(request):
    # Input validation and sanitation example
    try:
        if request.method == 'POST':
            strIP = request.remote_addr
        
            if request.form["email"] is not None:
                #origusername = request.form['username']
                origemail = request.form['email']
                #bleach_sanitized_username = sanitize_input(origusername)
                bleach_sanitized_email = sanitize_input(origemail)
            # check for full script elements
                #username = str(str(escape(bleach_sanitized_username)).lower().replace("<script>","")).replace("</script>","")
                email = str(str(escape(bleach_sanitized_email)).lower().replace("<script>","")).replace("</script>","")
                # check for partial script elements
                #username = str(username).replace('</','').replace('<','').replace('/>','').replace('>','').replace('(','').replace(')','')
                email = str(email).replace('</','').replace('<','').replace('/>','').replace('>','').replace('(','').replace(')','')
                
                if str(origemail).lower() != email:
                    logging.warning('Attack detected: Injection Attack from ' + str(strIP))
                    # email.send_secure_email(
                #     to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password, subject, message_body
                # )   
                    flash('Something went wrong. Please try again.', 'error')
                    return False
                else:
                    return True
            else:
                return True
        else:
            return True
    except Exception as err:
        print('An error occured: ' + str(err))  


# Example usage:
# store_pem_certificate("/path/to/your/certificate.pem")
def retrieve_pem_certificate(common_name, output_file_path, keychain_path="login.keychain"):
    """
    Retrieves a PEM certificate by common name from the specified macOS Keychain and saves it to a file.
    
    Args:
    common_name (str): Common Name (CN) of the certificate to retrieve.
    output_file_path (str): Path to save the retrieved PEM certificate.
    keychain_path (str): Path to the keychain file, defaults to the login keychain.
    """
    try:
        # Find the certificate and export it to a PEM file
        output = subprocess.run([
            "security", "find-key", "-l", common_name, "-t", "private"
        ], check=True, text=True, stdout=subprocess.PIPE)
        with open(output_file_path, "w") as f:
            f.write(output.stdout)
        print(f"Certificate exported successfully to {output_file_path}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to retrieve certificate: {str(e)}")

# Example usage:
# retrieve_pem_certificate("Your Certificate CN", "/path/to/save/certificate.pem")

   
def sanitize_input(input_string):

    """

    Sanitize an input string to prevent Cross-Site Scripting (XSS) attacks while allowing safe HTML elements and attributes.

    Args:

        input_string (str): The input string to be sanitized.

    Returns:

        str: The sanitized input string.

    """

    # Define the list of allowed HTML tags and attributes

    allowed_tags = [

        'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li',

        'ol', 'strong', 'ul', 'p', 'br', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'

    ]

    

    # Define a dictionary of allowed attributes for each tag

    allowed_attributes = {

        'a': ['href', 'title'],

        'abbr': ['title'],

        'acronym': ['title'],

    }
    # Sanitize the input string

    sanitized_string = bleach.clean(input_string, tags=allowed_tags, attributes=allowed_attributes)

    return sanitized_string

# def getS3cr3txLocalD(strInput):
#     try:
#         strInput = str(strInput)
#         stdout = Popen('dotnet'+' \"'+ strs3cr3txDLL + '\"'+' d '+' \"'+ strPEMfileName + '\"'+' \"' + strInput+'\"', shell=True, stdout=PIPE).stdout
#         s3cr3tx =str(stdout.readline()).lstrip('b\'').rstrip('\'')
#         return str(s3cr3tx)
#     except Exception as err:
#         print('An error occured: ' + str(err))  

# def getS3cr3txLocalE(strInput):
#     try:
#         strInput = str(strInput)
#         stdout= Popen('dotnet'+' \"'+ strs3cr3txDLL + '\"'+' e '+'\"'+ strPEMfileName + '\"'+' \"' + strInput+'\"', shell=True, stdout=PIPE).stdout
#         s3cr3tx=str(stdout.readline()).lstrip('b\'').rstrip('\\n\'')
#         return s3cr3tx
#     except Exception as err:
#         print('An error occured: ' + str(err)) 

def getS3cr3tx(strInput):
    try:
        strInput = str(strInput)
        #please set the following environment variables with the appropriate values s3cr3tx_Email, s3cr3tx_APIToken, s3cr3tx_AuthCode, s3cr3tx_URL for your s3cr3tx API account
        DOC_FORMAT="text/plain"
        Email_Header=os.getenv("s3cr3tx_Email")
        API_Token_Header=os.getenv("s3cr3tx_APIToken")
        Auth_Code_Header=os.getenv("s3cr3tx_AuthCode")
        #set the value to "d" to decrypt the secret using the s3cr3tx API
        EorD_Header="d"
        Input_Header=strInput
        URL_ROOT = os.getenv("s3cr3tx_URL")
        result3 = requests.get(URL_ROOT,headers={"Accept": DOC_FORMAT ,"Email": Email_Header,"APIToken":API_Token_Header,"AuthCode":Auth_Code_Header,"EorD":EorD_Header,"Input":Input_Header })
        s3cr3tx=result3.text
        return s3cr3tx
    except Exception as err:
        print('An error occured: ' + str(err)) 
def getHash(strInput):
    try:
        strInput = str(strInput)
        #please set the following environment variables with the appropriate values s3cr3tx_Email, s3cr3tx_APIToken, s3cr3tx_AuthCode, s3cr3tx_URL for your s3cr3tx API account
        strOutput = ""
        hashedInput = hashlib.sha3_512(strInput.encode('utf-8'))
        strOutput = hashedInput.hexdigest()
        return strOutput
    except Exception as err:
        print('An error occured: ' + str(err))         

def compareHash(strInput,strInput2):
    try:
        strInput = str(strInput)
        #please set the following environment variables with the appropriate values s3cr3tx_Email, s3cr3tx_APIToken, s3cr3tx_AuthCode, s3cr3tx_URL for your s3cr3tx API account
        strOutput = ""
        hashedInput = hashlib.sha3_512(strInput)
        strOutput = hashedInput.hexdigest()
        strInput2 = str(strInput2)
        #please set the following environment variables with the appropriate values s3cr3tx_Email, s3cr3tx_APIToken, s3cr3tx_AuthCode, s3cr3tx_URL for your s3cr3tx API account
        strOutput2 = ""
        hashedInput2 = hashlib.sha3_512(strInput)
        strOutput2 = hashedInput2.hexdigest()
        if strOutput ==  strOutput2:
            return True
        else:
            return False
    except Exception as err:
        print('An error occured: ' + str(err))   
        
def enc(strInput):
    with open(strPEMfileName, mode='rb') as privatefile:
        keydata = privatefile.read()
    privkey = rsa.PrivateKey.load_pkcs1(keydata)
    encbytes = rsa.encrypt(str(strInput).encode("utf-8",'ignore'),privkey) 
    strOutput = base64.urlsafe_b64encode(encbytes).decode("utf-8")
    return strOutput 

def dec(strInput):
    with open(strPEMfileName, mode='rb') as privatefile:
        keydata = privatefile.read()
    privkey = rsa.PrivateKey.load_pkcs1(keydata)
    inputdecoded = base64.urlsafe_b64decode(strInput)
    decbytes = rsa.decrypt(inputdecoded,privkey)
    strOutput = decbytes.decode("utf-8",'ignore')
    return strOutput

def encStandard(strInput):
    with open(strPEMfileName, mode='rb') as privatefile:
        keydata = privatefile.read()
    privkey = rsa.PrivateKey.load_pkcs1(keydata)
    encbytes = rsa.encrypt(str(strInput).encode("utf-8",'ignore'),privkey) 
    strOutput = base64.standard_b64encode(encbytes).decode("utf-8")
    return strOutput 

def decStandard(strInput):
    with open(strPEMfileName, mode='rb') as privatefile:
        keydata = privatefile.read()
    privkey = rsa.PrivateKey.load_pkcs1(keydata)
    inputdecoded = base64.standard_b64decode(strInput)
    decbytes = rsa.decrypt(inputdecoded,privkey)
    strOutput = decbytes.decode("utf-8",'ignore')
    return strOutput
