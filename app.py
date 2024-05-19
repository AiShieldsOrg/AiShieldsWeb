from flask import Flask, request, abort,render_template, redirect, url_for, flash
from flask_wtf import CSRFProtect
import bleach
from dotenv import load_dotenv
import os
from markupsafe import escape
from dateutil.relativedelta import relativedelta
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime,Column, ForeignKey, BigInteger,NVARCHAR,Integer, Table, desc, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from self_protection import protect,sanitize_input,getHash,encStandard,decStandard  
import openai
import anthropic
import uuid
from prompt_injection.prompt_injection_sanitizer import prompt_injection_score
from sensitive_information.sensitive_data_sanitizer import SensitiveDataSanitizer
from mdos.mdos_sanitizer import PromptAnalyzer
from aishieldsemail import send_secure_email
import secrets
from insecure_out_handling import InsecureOutputSanitizer
from overreliance.overreliance_data_sanitizer import OverrelianceDataSanitizer as ODS
import json
import netifaces as nif
import os
import nltk
from nltk.corpus import stopwords
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

nltk.download("stopwords")

app.config['SECRET_KEY'] = str(decStandard(os.getenv('SECRET_KEY')))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
email_from = os.getenv('EMAIL_FROM')
smtpserver = os.getenv('SMTP_SERVER')
smtpport = os.getenv('SMTP_PORT')
smtpp = os.getenv('SMTP_PASSWORD')
smtpu = os.getenv('SMTP_USER')

smtp_server = str(decStandard(smtpserver))
smtp_port = str(decStandard(smtpport))
smtp_p = str(decStandard(smtpp))
smtp_u = str(decStandard(smtpu))
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
handler = RotatingFileHandler('/users/youraccount/documents/aishields.log', maxBytes=10000000, backupCount=5)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

apis = [{"APIowner":"OpenAI","TextGen": {"Name":"ChatGPT","Models":[
                {"Name":"GPT 4","details":{ "uri": "https://api.openai.com/v1/chat/completions","jsonv":"gpt-4"}},
                {"Name":"GPT 4 Turbo Preview","details":{ "uri": "https://api.openai.com/v1/chat/completions","jsonv":"gpt-4-turbo-preview" }},
                {"Name":"GPT 3.5 Turbo","details":{"uri":"https://api.openai.com/v1/chat/completions","jsonv": "gpt-3.5-turbo"}}
                ]}},
                {"APIowner":"Anthropic","TextGen": {"Name":"Claude","Models":[
                {"Name":"Claude - most recent","details":{"uri": "https://api.anthropic.com/v1/messages","jsonv":"anthropic-version: 2023-06-01"}}
                 ]}}]

def app_context():
    app = Flask(__name__)
    strAppKey = os.getenv('STR_APP_KEY')
    app.secret_key = strAppKey.encode(str="utf-8")
    csrf = CSRFProtect(app)
    with app.app_context():
        yield

Base = declarative_base()

user_prompt_api_model = Table(
    "user_prompt_api_model",
    db.metadata,
    db.Column("user_id", BigInteger,ForeignKey("users.id")),
    db.Column("prompt_id", BigInteger, ForeignKey("inputPrompt.id")),
    db.Column("preproc_prompt_id",BigInteger,ForeignKey("preprocInputPrompt.id")),
    db.Column("apiresponse_id",BigInteger,ForeignKey("apiResponse.id")),
    db.Column("aishields_report_id",BigInteger,ForeignKey("aiShieldsReport.id")),
    db.Column("postproc_response_id",BigInteger,ForeignKey("postprocResponse.id")),
    db.Column("GenApi_id",BigInteger,ForeignKey("GenApi.id"))
)

user_codes_users = Table(
    "user_codes_users",
    db.metadata,
    db.Column("user_id", BigInteger,ForeignKey("users.id")),
    db.Column("user_codes_id", BigInteger,ForeignKey("user_codes.id")),
)
user_api = Table(
    "user_api",
    db.metadata,
    db.Column("user_id", BigInteger,ForeignKey("users.id")),
    db.Column("genapi_id", BigInteger, ForeignKey("GenApi.id")),
)

user_api_cred = Table(
    "user_api_cred",
    db.metadata,
    db.Column("user_id", BigInteger,ForeignKey("users.id")),
    db.Column("api_id",BigInteger,ForeignKey("GenApi.id")),
    db.Column("cred_id",BigInteger,ForeignKey("cred.id")),
    db.Column("created_date",DateTime)
)

requests_client = Table(
 "requests_client",
    db.metadata,
    db.Column("request_id", BigInteger,ForeignKey("requests.id")),
    db.Column("client_id", BigInteger, ForeignKey("clients.id")),
   
)

class Clients(db.Model):
    __tablename__ = "clients"
    id = db.Column(BigInteger, primary_key=True)
    IPaddress = db.Column(NVARCHAR)
    MacAddress = db.Column(NVARCHAR)
    create_date = db.Column(DateTime,unique=False, default=datetime.datetime.now(datetime.timezone.utc))
    requests = relationship("RequestLog", secondary=requests_client)

class RequestLog(db.Model):
    __tablename__ = "requests"
    id = db.Column(Integer, primary_key=True)
    client_id = db.Column(Integer, nullable=False)  # Assuming client ID is a string
    client_ip = db.Column(NVARCHAR, nullable=False)  # Assuming client ID is a string
    url = db.Column(NVARCHAR)
    request_type = db.Column(NVARCHAR)
    Headers = db.Column(NVARCHAR)  # Using Text instead of NVARCHAR for compatibility
    Body = db.Column(NVARCHAR)
    create_date = db.Column(DateTime, nullable=False, default=datetime.datetime.now)

    # def __init__(self, client_id,client_ip request_type, headers, body, url):
    #     self.client_ip = client_ip
    #     self.client_id = client_id
    #     self.request_type = request_type
    #     self.Headers = headers
    #     self.Body = body
    #     self.url = url

    @staticmethod
    def get_request_count(client_id):
        # Calculate the datetime 10 minutes ago
        ten_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
        
        # Filter requests based on client_id and creation date
        return RequestLog.query.filter_by(client_id=client_id).filter(RequestLog.create_date >= ten_minutes_ago).count()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(BigInteger, primary_key=True)
    username = db.Column(NVARCHAR)
    first_name = db.Column(NVARCHAR)
    last_name = db.Column(NVARCHAR)
    passphrase = db.Column(NVARCHAR)
    email = db.Column(NVARCHAR)
    user_verified = db.Column(Integer,default=0)
    created_date = db.Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = db.Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    inputPrompts = relationship("InputPrompt",secondary=user_prompt_api_model)
    preprocPrompts = relationship("PreProcInputPrompt", secondary=user_prompt_api_model)
    apiResponses = relationship("ApiResponse",secondary=user_prompt_api_model)
    postProcResponses = relationship("PostProcResponse",secondary=user_prompt_api_model)
    aiShieldsReports = relationship("AiShieldsReport",secondary=user_prompt_api_model)
    genApis = relationship(
        "GenApi", secondary=user_api, back_populates="users"
    )
    user_codes = relationship(
        "UserCode", secondary=user_codes_users, back_populates="users",
    )
    
class UserCode(db.Model):
    __tablename__ = "user_codes"
    id = db.Column(BigInteger, primary_key=True)
    user_id = db.Column(BigInteger,ForeignKey("users.id"))
    email = db.Column(NVARCHAR)
    code = db.Column(NVARCHAR)
    created_date = db.Column(DateTime,unique=False, default=datetime.datetime.now(datetime.timezone.utc))
    users = relationship("User", back_populates="user_codes")

class Credential(db.Model):
    __tablename__ = "cred"
    id = db.Column(BigInteger, primary_key=True)
    user_id = db.Column(BigInteger,ForeignKey("users.id"))
    api_id = db.Column(BigInteger,ForeignKey("GenApi.id"))
    username = db.Column(NVARCHAR)
    email = db.Column(NVARCHAR)
    token = db.Column(NVARCHAR, unique=False, nullable=True)
    jwt = db.Column(NVARCHAR, unique=False, nullable=True)
    header = db.Column(NVARCHAR, unique=False, nullable=True)
    formfield = db.Column(NVARCHAR, unique=False, nullable=True)
    created_date = db.Column(DateTime,unique=False, default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = db.Column(DateTime, unique=False, nullable=True)

class GenApi(db.Model):
    __tablename__ = "GenApi"
    id = db.Column(BigInteger, primary_key=True)
    api_owner = db.Column(NVARCHAR, unique=False, nullable=False)
    api_name =  db.Column(NVARCHAR, unique=False, nullable=False)
    uri = db.Column(NVARCHAR, unique=False, nullable=False)
    headers = db.Column(NVARCHAR, unique=False, nullable=True)
    formfields = db.Column(NVARCHAR, unique=False, nullable=True)
    model = db.Column(NVARCHAR, unique=True, nullable=False)
    created_date = db.Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = db.Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    inputPrompts = relationship("InputPrompt", secondary=user_prompt_api_model)
    preprocPrompts = relationship("PreProcInputPrompt", secondary=user_prompt_api_model)
    apiResponses = relationship("ApiResponse",secondary=user_prompt_api_model)
    postProcResponses = relationship("PostProcResponse",secondary=user_prompt_api_model)
    aiShieldsReports = relationship("AiShieldsReport",secondary=user_prompt_api_model)
    users = relationship(
        "User", secondary=user_api, back_populates="genApis"
    )
    
# class User(db.Model):
#     id = db.db.Column(BigInteger, primary_key=True)
#     username = db.db.Column(NVARCHAR, unique=True, nullable=False)
#     email = db.db.Column(NVARCHAR, unique=True, nullable=False)
    
class InputPrompt(db.Model):
    __tablename__ = "inputPrompt"
    id = db.Column(BigInteger, primary_key=True)
    user_id = db.Column(BigInteger,ForeignKey("users.id"))
    cred_id = db.Column(BigInteger, ForeignKey("cred.id"))
    username = db.Column(NVARCHAR)
    email = db.Column(NVARCHAR)
    api_id = db.Column(BigInteger,ForeignKey("GenApi.id"))
    api = db.Column(NVARCHAR)
    internalPromptID = db.Column(NVARCHAR,unique=True)
    inputPrompt = db.Column(NVARCHAR)
    created_date = db.Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = db.Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
  
    
class PreProcInputPrompt(db.Model):
    __tablename__ = "preprocInputPrompt"
    id = db.Column(BigInteger, primary_key=True)
    user_id = db.Column(BigInteger,ForeignKey("users.id"))
    username = db.Column(NVARCHAR)
    email = db.Column(NVARCHAR)
    api_id = db.Column(BigInteger,ForeignKey("GenApi.id"))
    api = db.Column(NVARCHAR,unique=False,nullable=False)
    internalPromptID = db.Column(NVARCHAR,nullable=False)
    rawInputPrompt_id = db.Column(BigInteger,ForeignKey("inputPrompt.id"),nullable=False)
    inputPrompt = db.Column(NVARCHAR,unique=False,nullable=False)
    preProcInputPrompt = db.Column(NVARCHAR,unique=False,nullable=False)
    SensitiveDataSanitizerReport = db.Column(NVARCHAR,unique=False,nullable=True)
    PromptInjectionReport = db.Column(NVARCHAR,unique=False,nullable=True)    
    OverrelianceReport = db.Column(NVARCHAR,unique=False,nullable=True)
    OverrelianceKeyphraseData = db.Column(NVARCHAR,unique=False,nullable=True)
    created_date = db.Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = db.Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))

 
class ApiResponse(db.Model):
    __tablename__ = "apiResponse"
    id = db.Column(BigInteger, primary_key=True)
    user_id = db.Column(BigInteger,ForeignKey("users.id"))
    username = db.Column(NVARCHAR)
    email = db.Column(NVARCHAR)
    internalPromptID = db.Column(NVARCHAR,unique=False,nullable=False)
    preProcPrompt_id = db.Column(BigInteger,ForeignKey("preprocInputPrompt.id"))
    rawInputPrompt_id = db.Column(BigInteger,ForeignKey("inputPrompt.id"))
    externalPromptID = db.Column(NVARCHAR,unique=False,nullable=False)
    api_id = db.Column(BigInteger,ForeignKey("GenApi.id"))
    api = db.Column(NVARCHAR) 
    rawoutput = db.Column(NVARCHAR)
    created_date = db.Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
      
class PostProcResponse(db.Model):
    __tablename__ = "postprocResponse"
    id = db.Column(BigInteger, primary_key=True)
    rawInputPrompt_id = db.Column(BigInteger, ForeignKey("inputPrompt.id"))
    inputPromptID = db.Column(NVARCHAR,unique=False,nullable=False)
    preProcPrompt_id = db.Column(BigInteger, ForeignKey("preprocInputPrompt.id"))
    externalPromptID = db.Column(NVARCHAR,unique=False,nullable=False)
    user_id = db.Column(BigInteger,ForeignKey("users.id"))
    username = db.Column(NVARCHAR)
    email = db.Column(NVARCHAR)
    api_id = db.Column(BigInteger,ForeignKey("GenApi.id"))
    api = db.Column(NVARCHAR,unique=False,nullable=False)
    rawResponseID = db.Column(BigInteger,ForeignKey("apiResponse.id"))
    rawOutputResponse = db.Column(NVARCHAR,unique=False,nullable=False)
    InsecureOutputHandlingReport = db.Column(NVARCHAR,unique=False,nullable=False)
    postProcOutputResponse = db.Column(NVARCHAR,unique=False,nullable=False)    
    created_date = db.Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    
class AiShieldsReport(db.Model):
    __tablename__ = "aiShieldsReport"
    id = db.Column(BigInteger, primary_key=True)
    rawInputPrompt_id = db.Column(BigInteger, ForeignKey("inputPrompt.id"))
    preProcPrompt_id = db.Column(BigInteger, ForeignKey("preprocInputPrompt.id"))
    rawResponse_id = db.Column(BigInteger, ForeignKey("apiResponse.id"))
    postProcResponse_id = db.Column(BigInteger, ForeignKey("postprocResponse.id"))
    internalPromptID = db.Column(NVARCHAR,unique=False,nullable=False)
    externalPromptID = db.Column(NVARCHAR,unique=False,nullable=True)
    user_id = db.Column(BigInteger,ForeignKey("users.id"))
    username = db.Column(NVARCHAR, unique=False, nullable=False)
    email = db.Column(NVARCHAR, unique=False, nullable=False)
    api_id = db.Column(BigInteger,ForeignKey("GenApi.id"))
    api = db.Column(NVARCHAR,unique=False,nullable=False)
    SensitiveDataSanitizerReport = db.Column(NVARCHAR,unique=False,nullable=True)
    PromptInjectionReport = db.Column(NVARCHAR,unique=False,nullable=True)    
    OverrelianceReport = db.Column(NVARCHAR,unique=False,nullable=True)
    InsecureOutputReportHandling = db.Column(NVARCHAR,unique=False,nullable=True)     
    MDOSreport = db.Column(NVARCHAR,unique=False,nullable=True)   
    created_date = db.Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = db.Column(DateTime)
    

def mac_for_ip(ip):
    'Returns a list of MACs for interfaces that have given IP, returns None if not found'
    for i in nif.interfaces():
        addrs = nif.ifaddresses(i)
        try:
            if_mac = addrs[nif.AF_LINK][0]['addr']
            if_ip = addrs[nif.AF_INET][0]['addr']
        except IndexError: #ignore ifaces that dont have MAC or IP
            if_mac = if_ip = None
        except KeyError:
            if_mac = if_ip = None
        if if_ip == ip:
            return if_mac
    return None

@app.before_request
def before_request():
  try:
    public_routes = ['login', 'newaccount', 'forgot', 'verifyemail', 'static','reset']
    if 'logged_in' not in session and request.endpoint not in public_routes:
            return redirect(url_for('login'))
        
    # Save the request data for MDOS protection
    macAddress = mac_for_ip(request.remote_addr)
    if macAddress is None:
        macAddress = "?"
    client_info = Clients(
        IPaddress=request.remote_addr,
        MacAddress=macAddress
    )
    db.session.add(client_info)
    db.session.commit()
    db.session.flush(objects[client_info])
    request_data = RequestLog(
        client_id=client_info.id, 
        client_ip=client_info.IPaddress, 
        request_type=request.method,
        Headers=repr(dict(request.headers)),
        Body=request.data.decode('utf-8'),
        url=request.url
    )
    db.session.add(request_data)
    db.session.commit()
    db.session.flush(objects[request_data])

    # MDOS (Model Denial of Service entrypoint)
    # James Yu can add code here to handle MDOS protection
    client_id = request.remote_addr
    request_count = RequestLog.get_request_count(client_id)
    
    if request_count >= 500:  # Adjust the limit as needed
        flash('Too many requests, please try again later', 'danger')
        print(request_count)
        abort(429)  # Too Many Requests status code
  except Exception as err:
    logging.error('An error occurred during login: %s', err)
    flash("An error occurred. Please try again.")
    return render_template('login.html', form=LoginForm())

    
@app.route("/",methods=['GET','POST'])
def home():
    try:
        return render_template('index.html')
    except Exception as err:
        logging.error('An error occurred during home request: %s', err)
        flash("An error occurred. Please try again.")
        return render_template('index.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
        
                email = request.form.get('email')
                if email is not None:
                    email = str(email).lower().strip(" ")
                    user = (
                            db.session.query(User)
                            .filter(User.email == str(request.form.get("email")).lower(),User.user_verified == 1)
                            .first()
                        ) 
                    if (user is not None and user.user_verified > 0):
                        form = LoginForm(email=str(user.email),passphrase='')
                        return render_template('login.html',form=form)
                    else:
                        return render_template('newaccount.html', email=email)
                else:
                    flash("Please enter a valid email address.")
        
        else:
            return render_template('index.html')
    except Exception as err:
        logging.error('An error occurred in index request: %s', err)
        flash("An error occurred. Please try again. " +str(err))
        return render_template('index.html')

@app.route('/verifyemail',methods=['GET', 'POST'])
def verifyemail():
    try:
        if request.method == 'GET':
            return render_template('verifyemail.html', email=request.form.get(key='email'))
        if request.method == 'POST':
            user_entered_code = str(request.form.get(key='passphrase'))
            usercodes = (db.session.query(UserCode).all)
            user_stored_code = (db.session.query(UserCode).filter(UserCode.email == str(request.form.get(key="email")).lower()).order_by(desc(UserCode.id)).first()) 
            user_code = str(user_stored_code.code)
            if user_code is not None:
                if user_code == user_entered_code:
                    user = (
                        db.session.query(User)
                        .filter(User.email == str(request.form["email"]).lower())
                        .order_by(desc(User.id)).first()
                    )
                    user.user_verified = 1
                    db.session.add(user)
                    db.session.commit()
                    db.session.flush(objects=[user])
                    userName = str(user.first_name + " " + user.last_name)
                    return render_template('chat.html', email=request.form.get("email"),username=userName,apis=apis)
                else:
                    flash("Code did not match, please try entering the code again")
                    return render_template('verifyemail.html', email=request.form.get("email"))
            flash("Please enter the code from your email")
            return render_template('verifyemail.html', email=request.form.get("email"))
        return render_template('verifyemail.html', email=request.form.get("email"))
    except Exception as err:
        logging.error('An error occurred during verify login request: %s',str(err))
        flash("An error occurred. Please try again: " + str(err))
        return render_template('login.html', form=LoginForm())  
 
@app.route('/reset',methods=['GET','POST'])
def reset():
    try:
        if request.method == 'GET':
            strCode = request.query_string.decode('utf-8').split(str('='))[1]
            return render_template('reset.html',code=strCode)
        if request.method == 'POST':
            code = str(request.form.get("code"))
            usercode = (
                db.session.query(UserCode)
                .filter(UserCode.code == code)
                .one_or_none()
            )
            if usercode is not None:
                user = (db.session.query(User).filter(User.id == usercode.user_id)
                        .one_or_none())
                user.passphrase = str(getHash(request.form.get(key="passphrase")))
                db.session.add(user)
                db.session.commit()
                db.session.flush(objects=[user])
                to_email = user.email
                from_email = smtp_u
                s_server = smtp_server
                s_port = smtp_port
                s_p = smtp_p
                m_subj = "Your password was just reset for AiShields.org"
                m_message = "Dear " + user.first_name + ", \n\n Your password was just changed for AiShields. \n\nPlease contact us via email at support@aishields.org if you did not just change your password. \n\n Thank you, \n\n Support@AiShields.org"
                send_secure_email(to_email,from_email,s_server,s_port,from_email,s_p,m_subj,m_message)
                flash("Your password has been changed")
                #now delete the code
                db.session.delete(usercode)
                db.session.commit()
                db.session.flush(objects=[usercode])
                #strCode = request.query_string.decode('utf-8').split('=')[1]
                return render_template('reset.html',code=code)
            else:
                flash("Something went wrong please try again.")
                #strCode = request.query_string.decode('utf-8').split('=')[1]
                return render_template('reset.html',code=code)
    except Exception as err:
        logging.error('An error occurred during during reset request: %s', err)
        flash("An error occurred." + str(err) +" Please try again.")
        strCode = request.query_string.decode('utf-8').split(str('='))[1]
        return render_template('reset.html',code=strCode)

@app.route('/forgot',methods=['GET','POST'])
def forgot():
    try:
        if request.method == 'GET':
            return render_template('forgot.html')
        if request.method == 'POST':
            email = str(request.form.get("email")).lower()
            
            user = (
                db.session.query(User)
                .filter(User.email == email,User.user_verified == 1)
                .first()
            )
            if user is not None:
                if user.user_verified == 1:
                    strCode = str(uuid.uuid4())
                    code = UserCode(user_id=user.id,email=user.email,code=strCode)
                    db.session.add(code)
                    db.session.commit()
                    db.session.flush(objects=[code])
                    to_email = user.email
                    from_email = smtp_u
                    s_server = smtp_server
                    s_port = smtp_port
                    s_p = smtp_p
                    m_subj = "Reset instructions for AiShields.org"
                    m_message = "Dear " + user.first_name + ", \n\n Please click this link: <a href='https://dev.aishields.org/reset?code=" + strCode +"' or paste it into your browser address bar to change your password. \n\nThis link will expire in 20 minutes. \n\n Thank you, \n\n Support@AiShields.org"
                    send_secure_email(to_email,from_email,s_server,s_port,from_email,s_p,m_subj,m_message)
                    flash("An email was sent with a link to reset your password.")
                    return render_template('forgot.html')
    
            else:
                flash("We could not find an account in our system with the email you entered")
                return render_template('forgot.html')
    
    except Exception as err:
        logging.error('An error occured during forgot request: ' + str(err))
        flash("An error occurred." + str(err) +" Please try again.")
        return render_template('forgot.html')
    
             
@app.route('/newaccount',methods=['GET','POST'])
def newaccount():
    try:
        if request.method == 'GET':
            return render_template('newaccount.html')
        if request.method == 'POST':
            email = (
                db.session.query(User)
                .filter(User.email == str(request.form.get("email")).lower(),User.user_verified == 1)
                .one_or_none()
            )
            if email is not None:
                if email.user_verified == 1:
                    flash("Email is already registered, please login")
                    return render_template('login.html',email=email.email)
            bmonth = str(int(request.form["bmonth"]))
            bday = str(int(request.form["bday"]))
            byear = str(int(request.form["byear"]))
            birthdate = datetime.date(int(byear),int(bmonth),int(bday))
            yearstoadd = 18
            currentdate = datetime.datetime.today()
            difference_in_years = relativedelta(currentdate, birthdate).years
            if difference_in_years >= yearstoadd: 
                firstname = sanitize_input(str(request.form["firstname"]).rstrip(' ').lstrip(' '))
                lastname = sanitize_input(str(request.form["lastname"]).rstrip(' ').lstrip(' '))
                username = str(firstname).capitalize() + " " + str(lastname).capitalize()
                user = User(username=str(username),first_name=str(firstname),last_name=str(lastname),email=str(request.form["email"]).lower(),passphrase=getHash(request.form['passphrase']),user_verified=0,created_date=datetime.datetime.now(datetime.timezone.utc))
                db.session.add(user)
                db.session.commit()
                db.session.flush(objects=[user])
                strCode = ""
                for i in range(6):
                    strCode += str(secrets.randbelow(10))
                code = UserCode(user_id=user.id,email=user.email,code=strCode)
                db.session.add(code)
                db.session.commit()
                db.session.flush(objects=[code])
                to_email = user.email
                from_email = smtp_u
                s_server = smtp_server
                s_port = smtp_port
                s_p = smtp_p
                m_subj = "Please verify your email for AiShields.org"
                m_message = "Dear " + firstname + ", \n\n Please enter the following code: " + strCode + " in the email verification form. \n\n Thank you, \n\n Support@AiShields.org"
                send_secure_email(to_email,from_email,s_server,s_port,from_email,s_p,m_subj,m_message)
                return render_template('verifyemail.html',apis=apis, email=user.email)
            else:
                flash("You must be 18 years or older to create an account.")
                return render_template("newaccount.html",apis=apis, email=request.form.get(email))
        else:
            return render_template("login.html",form=LoginForm())
    except Exception as err:
        logging.error('An error occurred during newaccount request: %s', err)
        flash("An error occurred. Please try again.")
        return render_template('login.html', form=LoginForm())

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    try:
        if request.method == 'GET':
            email = session['email']
            if email:
                user = db.session.query(User).filter(User.email == email, User.user_verified==1).one_or_none()
                if user:
                    return render_template('profile.html', email=user.email, firstname=user.first_name, lastname=user.last_name)
            return render_template('login.html')
        if request.method == 'POST':
            email = request.form.get("email").lower()
            user = db.session.query(User).filter(User.email == email, User.user_verified == 1).one_or_none()
            if user:
                firstname = sanitize_input(request.form["firstname"].strip())
                lastname = sanitize_input(request.form["lastname"].strip())
                user.first_name = firstname
                user.last_name = lastname
                user.passphrase = getHash(request.form['passphrase'])
                db.session.commit()
                flash("Profile updated successfully")
                return render_template('profile.html', email=user.email, firstname=user.first_name, lastname=user.last_name)
            flash("Something went wrong. Please try again later.")
            return render_template('profile.html', email=email)
    except Exception as err:
        logging.error('An error occurred during profile request: %s', err)
        flash("An error occurred. Please try again.")
        return render_template('login.html', form=LoginForm())

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        form = LoginForm()
        if request.method == "GET":
             return render_template('login.html', form=LoginForm())
        if form.validate_on_submit():
            try:
                email = form.email.data.lower()
                passphrase = getHash(form.passphrase.data)
                user = (db.session.query(User).filter(
                    User.email == email, 
                    User.passphrase == passphrase, 
                    User.user_verified == 1
                ).first())

                if user is not None:
                    session['logged_in'] = True
                    session['user_id'] = user.id
                    session['email'] = user.email
                    session['username'] = f"{user.first_name} {user.last_name}"
                    InputPromptHistory = (db.session.query(InputPrompt).filter(InputPrompt.user_id == user.id))
                    chathistory = {}
                    for prmpt in InputPromptHistory:
                        chathistory[prmpt.internalPromptID]=prmpt.inputPrompt
                    return render_template('chat.html', InputPromptHistory=chathistory,email=user.email,username=user.first_name + " " + user.last_name,apis=apis,output=False,Logged_in=True)   
                else:
                    flash("Invalid email or password")
                    return render_template('login.html', form=LoginForm())
 
            except Exception as err:
                logging.error('An error occurred during login: %s', err)
                flash("An error occurred. Please try again.")
                return render_template('login.html', form=LoginForm())

    except Exception as err:
        logging.error('An error occurred during login: %s', err)
        flash("An error occurred. Please try again.")
        return render_template('login.html', form=LoginForm())
 

@app.route('/logout')
def logout():
    try:
        session.clear()
        flash("You have been logged out.")
        form = LoginForm()
        return render_template('login.html',form=form)
    except Exception as err:
        logging.error('An error occurred during logout: %s', err)
        flash("An error occurred. Please try again.")
        return render_template('login.html', form=LoginForm())
    

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    try:
        if not session.get('logged_in'):
            return render_template('login',form=LoginForm())

        user = (db.session.query(User).filter(User.email == session['email']).first())
        InputPromptHistory = (db.session.query(InputPrompt).filter(InputPrompt.user_id == user.id))
        chathistory = {prmpt.internalPromptID: prmpt.inputPrompt for prmpt in InputPromptHistory}                           
        if request.method == 'GET':
            if request.query_string is not None and request.query_string != "" and request.query_string.index(str("=").encode()) >0 and len(request.query_string.split('=')) >1:
                chatId = request.query_string.decode('utf-8').split('=')[1]
                rawInput = (db.session.query(InputPrompt).filter(InputPrompt.internalPromptID == str(chatId), InputPrompt.user_id == user.id).one_or_none())
                if rawInput is not None:
                    preprocPrompt = (db.session.query(PreProcInputPrompt).filter(PreProcInputPrompt.internalPromptID == str(chatId)).one_or_none())
                    if preprocPrompt:
                        postProcResp = (db.session.query(PostProcResponse).filter(PostProcResponse.inputPromptID == str(chatId)).one_or_none())
                        if postProcResp:
                            aiShieldsReport = (db.session.query(AiShieldsReport).filter(AiShieldsReport.internalPromptID == str(chatId)).one_or_none())
                            if aiShieldsReport:
                                rawInputStr = rawInput.inputPrompt
                                preprocPromptStr = preprocPrompt.preProcInputPrompt
                                apiResponse = (db.session.query(ApiResponse).filter(ApiResponse.internalPromptID == str(chatId)).one_or_none())
                                if apiResponse:
                                    rawOutputStr = apiResponse.rawoutput
                                    postProcRespStr = postProcResp.postProcOutputResponse
                                    findings = [
                                        {"category": "Sensitive Data", "details": aiShieldsReport.SensitiveDataSanitizerReport, "id": aiShieldsReport.internalPromptID},
                                        {"category": "Prompt Injection", "details": aiShieldsReport.PromptInjectionReport, "id": aiShieldsReport.internalPromptID},
                                        {"category": "Overreliance", "details": aiShieldsReport.OverrelianceReport, "id": aiShieldsReport.internalPromptID},
                                        {"category": "Insecure Output Handling", "details": aiShieldsReport.InsecureOutputReportHandling, "id": aiShieldsReport.internalPromptID}
                                    ]
                                    return render_template('chat.html', rawInput=rawInput.inputPrompt, preProcStr=preprocPrompt.preProcInputPrompt, rawResponse=rawOutputStr, InputPromptHistory=chathistory, PostProcResponseHistory=postProcRespStr, apis=apis, email=session['email'], username=session['username'], response=postProcRespStr, findings=findings, output=True, logged_in=True)
                return render_template('chat.html', apis=apis, email=session['email'], username=session['username'], InputPromptHistory=chathistory, logged_in=True)
            elif session.get['logged_in']:
                return render_template('chat.html', apis=apis, email=session['email'], username=session['username'], InputPromptHistory=chathistory, logged_in=True)
            else:
                return render_template('login.html', form=LoginForm())
        elif request.method == 'POST':
            if not session.get('logged_in'):
                form = LoginForm()
                return render_template('login',form=form)
            api = request.form.get('api')
            token = request.form.get('apitoken')
            username = session.get('username')
            email = session.get('email')
            inputprompt = request.form.get('inputprompt')
            user = (db.session.query(User).filter(User.email == email.lower(), User.user_verified == 1).order_by(desc(User.id)).first())
            if user is None:
                form = LoginForm()
                return render_template('login',form=form)
            userid = user.id if user else ""
            storetoken = request.form.get('storetoken', 'No')

            if not api or not token or not inputprompt or not username or not email:
                flash("Please fill out all required fields.")
                return render_template('chat.html', apis=apis, username=username, email=email, logged_in=True)

            strEncToken = encStandard(token)
            internalID = str(uuid.uuid4())
            lstApi = str(api).split(' ')
            strApi = lstApi[0]
            strModel = lstApi[1]

            rawInput = InputPrompt(internalPromptID=internalID, user_id=userid, username=username, email=email, api=api, inputPrompt=inputprompt)
            db.session.add(rawInput)
            db.session.commit()
            db.session.flush(objects=[rawInput])
            rawInputObj = db.session.query(InputPrompt).filter(InputPrompt.internalPromptID == internalID).one_or_none()

            apiObj = db.session.query(GenApi).filter(GenApi.model == str(strModel), GenApi.api_owner == strApi).one_or_none()
            strRole = request.form.get('role', 'user')

            if apiObj:
                preprocessedPromptString = aishields_sanitize_input(rawInput)
                preprocessedPrompt = PreProcInputPrompt(
                    internalPromptID=internalID,
                    user_id=userid,
                    api_id=apiObj.id,
                    api=apiObj.uri,
                    email=email,
                    rawInputPrompt_id=rawInputObj.id,
                    inputPrompt=rawInput.inputPrompt,
                    preProcInputPrompt=preprocessedPromptString,
                    username=username,
                    SensitiveDataSanitizerReport=str(preprocessedPromptString),
                    PromptInjectionReport="",
                    OverrelianceReport="",
                    OverrelianceKeyphraseData=""
                )
                db.session.add(preprocessedPrompt)
                db.session.commit()
                db.session.flush(objects=[preprocessedPrompt])

                strTempApiKey = str(decStandard(str(strEncToken)))
                client = openai.Client(api_key=str(strTempApiKey))
                stream = client.chat.completions.create(
                    model=strModel,
                    messages=[{"role": strRole.lower(), "content": inputprompt}],
                    stream=True,
                )
                strRawOutput = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        strRawOutput += chunk.choices[0].delta.content

                rawOutput = ApiResponse(
                    internalPromptID=internalID,
                    user_id=userid,
                    api_id=apiObj.id,
                    api=apiObj.uri,
                    email=email,
                    preProcPrompt_id=preprocessedPrompt.id,
                    rawInputPrompt_id=rawInput.id,
                    rawoutput=strRawOutput,
                    externalPromptID="",
                    username=username,
                )
                db.session.add(rawOutput)
                db.session.commit()
                db.session.flush(objects=[rawOutput])
                rawOutputObj = db.session.query(ApiResponse).filter(ApiResponse.internalPromptID == internalID).one_or_none()
                preProcObj = db.session.query(PreProcInputPrompt).filter(PreProcInputPrompt.internalPromptID == internalID).one_or_none()
                postProcPromptObj = PostProcResponse(
                    rawInputPrompt_id=rawInputObj.id,
                    inputPromptID=internalID,
                    preProcPrompt_id=preProcObj.id,
                    externalPromptID=rawOutput.externalPromptID,
                    user_id=userid,
                    username=username,
                    email=email,
                    api_id=apiObj.id,
                    api=apiObj.uri,
                    rawResponseID=rawOutputObj.id,
                    rawOutputResponse=rawOutputObj.rawoutput,
                    postProcOutputResponse="",
                    InsecureOutputHandlingReport="",
                    created_date=datetime.datetime.now(datetime.timezone.utc)
                )
                postProcPromptObj = aishields_postprocess_output(postProcPromptObj)
                preprocessedPrompt = aishields_overreliance_postProc(rawInput, preprocessedPrompt, postProcPromptObj, rawInput)
                db.session.add(postProcPromptObj)
                db.session.commit()
                db.session.flush(objects=[postProcPromptObj])

                aiShieldsReportObj = AiShieldsReport(
                    rawInputPrompt_id=rawInputObj.id,
                    internalPromptID=internalID,
                    preProcPrompt_id=preProcObj.id,
                    externalPromptID=rawOutput.externalPromptID,
                    user_id=userid,
                    username=username,
                    email=email,
                    api_id=apiObj.id,
                    api=apiObj.uri,
                    rawResponse_id=rawOutputObj.id,
                    postProcResponse_id=postProcPromptObj.id,
                    SensitiveDataSanitizerReport=preProcObj.SensitiveDataSanitizerReport,
                    PromptInjectionReport=preProcObj.PromptInjectionReport,
                    OverrelianceReport=preProcObj.OverrelianceReport,
                    InsecureOutputReportHandling=postProcPromptObj.InsecureOutputHandlingReport,
                    MDOSreport=getMDOSreport(rawInputObj),
                    created_date=datetime.datetime.now(datetime.timezone.utc),
                    updated_date=datetime.datetime.now(datetime.timezone.utc)
                )
                db.session.add(aiShieldsReportObj)
                db.session.commit()
                db.session.flush(objects=[aiShieldsReportObj])

                findings = [
                    {"category": "Sensitive Data", "details": aiShieldsReportObj.SensitiveDataSanitizerReport, "id": aiShieldsReportObj.internalPromptID},
                    {"category": "Prompt Injection", "details": aiShieldsReportObj.PromptInjectionReport, "id": aiShieldsReportObj.internalPromptID},
                    {"category": "Overreliance", "details": aiShieldsReportObj.OverrelianceReport, "id": aiShieldsReportObj.internalPromptID},
                    {"category": "MDOS", "details": aiShieldsReportObj.MDOSreport, "id": aiShieldsReportObj.MDOSreport},
                    {"category": "Insecure Output Handling", "details": aiShieldsReportObj.InsecureOutputReportHandling, "id": aiShieldsReportObj.internalPromptID}
                ]

                InputPromptHistory = (db.session.query(InputPrompt).filter(InputPrompt.user_id == userid).order_by(desc(InputPrompt.created_date)))
                chathistory = {prmpt.internalPromptID: prmpt.inputPrompt for prmpt in InputPromptHistory}
                PostProcResponseHistory = (db.session.query(PostProcResponse).filter(PostProcResponse.user_id == userid))
                return render_template('chat.html', rawInput=rawInputObj.inputPrompt, preProcStr=preProcObj.preProcInputPrompt, rawResponse=rawOutputObj.rawoutput, InputPromptHistory=chathistory, PostProcResponseHistory=PostProcResponseHistory, apis=apis, email=session['email'], username=session['username'], response=postProcPromptObj.postProcOutputResponse, findings=findings, output=True, logged_in=True)
        return render_template('chat.html', InputPromptHistory=chathistory, apis=apis, email=session['email'], username=session['username'], logged_in=True)
    except Exception as err:
        logging.error('An error occurred during chat processing: %s', err)
        flash(err)
        return render_template('login.html', form=LoginForm())

def getMDOSreport(input:InputPrompt):
        #sensitive data sanitization:
        # now sanitize for privacy protected data
    try:
        prompt = input.inputPrompt

        # Instantiate the analyzer
        analyzer = PromptAnalyzer()
        
        # Analyze the prompt
        is_expensive = analyzer.is_expensive_prompt(prompt)
        complexity = analyzer.complexity_metric(prompt)

        # Return the results as a dictionary
        result = {
            "prompt": prompt,
            "is_expensive": is_expensive,
            "complexity_metric": complexity
        }
        return str(result)
    except Exception as err:
        logging.error('An error occurred while generating the MDOS report: %s', err)
        flash(err)


def aishields_sanitize_input(input:InputPrompt):
      try: #now sanitize for Prompt Injection
      strPreProcInput = ""
      strRawInputPrompt = input.inputPrompt
  
  
  
      #sensitive data sanitization:
      # now sanitize for privacy protected data
      sds = SensitiveDataSanitizer()
      strSensitiveDataSanitized = sds.sanitize_input(input_content=strRawInputPrompt)           
      
      
      strPreProcInput += strRawInputPrompt    
      
      #now assess for Overreliance
      return strPreProcInput
          #sensitive data sanitization:
          # now sanitize for privacy protected data
      try:
          strPreProcInput = ""
          strRawInputPrompt = input.inputPrompt
          sanitizedInput = sanitize_input(strRawInputPrompt)
          sds = SensitiveDataSanitizer()
          strSensitiveDataSanitized = sds.sanitize_input(input_content=sanitizedInput)           
          strPreProcInput += str(strSensitiveDataSanitized)
          #now sanitize for Prompt Injection
          #now assess for Overreliance
          return strPreProcInput
      except Exception as err:
          logging.error('An error occurred during input sanitization: %s', err)
          flash(err) 
  except Exception as err:
      logging.error('An error occurred during input sanitization: %s', err)
      flash(err)


def aishields_overreliance_inputfunc(input:InputPrompt, preproc:PreProcInputPrompt):
        #sensitive data sanitization:
        # now sanitize for privacy protected data
    try:
        SITE_IGNORE_LIST = ["youtube.com"]
        NUMBER_OF_SEARCHES = 1
        NUMBER_OF_LINKS = 1
        STOPWORD_LIST = ["*", "$"]
        
        ods = ODS()

        overreliance_keyphrase_data_list = ods.get_keyphrases_and_links(preproc.preProcInputPrompt,NUMBER_OF_SEARCHES,link_number_limit=NUMBER_OF_LINKS, stopword_list=STOPWORD_LIST)
        
        overreliance_keyphrase_data_list = ods.get_articles(overreliance_keyphrase_data_list,site_ignore_list=SITE_IGNORE_LIST)
        #preproc.OverrelianceKeyphraseData = repr(overreliance_keyphrase_data_list)
        return overreliance_keyphrase_data_list
    except Exception as err:
        logging.error('An error occurred durring overreliance input processing: %s', err)
        flash(err)  

def aishields_overreliance_postProc(input:ApiResponse,preproc:PreProcInputPrompt, postproc:PostProcResponse,rawinput:InputPrompt):
        #sensitive data sanitization:
        # now sanitize for privacy protected data
    try:
        SITE_IGNORE_LIST = ["youtube.com"]
        NUMBER_OF_SEARCHES = 4
        NUMBER_OF_LINKS = 10
        STOPWORD_LIST = ["*", "$"]
        
        ods= ODS()
        overreliance_keyphrase_data_list = ods.get_keyphrases_and_links(preproc.preProcInputPrompt,NUMBER_OF_SEARCHES,link_number_limit=NUMBER_OF_LINKS, stopword_list=STOPWORD_LIST)
        overreliance_keyphrase_data_list = ods.get_articles(overreliance_keyphrase_data_list,site_ignore_list=SITE_IGNORE_LIST)
        data_summary_list = ods.compare(overreliance_keyphrase_data_list,postproc.rawOutputResponse)
        overreliance_string = str(f"score: {data_summary_list[0]['score']} of {data_summary_list[0]['link']}")
        preproc.OverrelianceReport = overreliance_string
        return preproc
    except Exception as err:
        logging.error('An error occurred during overreliance output processing: %s', err)
        flash(err)  


def aishields_postprocess_output(postProcResponseObj:PostProcResponse):
    #insecure output handing
    try:
        #strPostProcessedOutput = sanitize_input(postProcResponseObj.rawOutputResponse)
        output_sanitizer=InsecureOutputSanitizer()
        strPostProcessedOutput, outputSanitizationReport = output_sanitizer.generate_json_report(postProcResponseObj.rawOutputResponse)
        
        postProcResponseObj.postProcOutputResponse = escape(str(strPostProcessedOutput))
        postProcResponseObj.InsecureOutputHandlingReport = outputSanitizationReport
        #handle and sanitize raw output
        #return post processed Output
        return postProcResponseObj
    except Exception as err:
        logging.error('An error occurred during post processing: %s', err)
        flash(err) 

def aishields_store_cred(input:Credential):
    try:
        #insecure output handing
        db.session.add(input)
        db.session.commit()
        #handle and sanitize raw output
        #return post processed Output
        return True
    except Exception as err:
        logging.error('An error occurred while attempting to store creds: %s', err)
        flash(err)
      
  
def aishields_promptInjection_check(input:InputPrompt):
        #sensitive data sanitization:
        # now sanitize for privacy protected data
    try:
        promptInjectionOutput = {}
        #now sanitize for Prompt Injection PASS
        return promptInjectionOutput
    except Exception as err:
        logging.error('An error occurred during prompt injection check: %s', err)
        flash(err)
        
def aishields_get_string_diff(strA,strB):
    try:
        res = ""
        if len(str(strA))>len(str(strB)): 
            res=str(strA).replace(str(strB),'')            
        else: 
            res=str(strB).replace(str(strA),'')
        return res
    except Exception as err:
        print('An error occured: ' + str(err))  

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
        
        

