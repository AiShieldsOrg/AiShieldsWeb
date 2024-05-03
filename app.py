from flask import Flask, request, abort,render_template, redirect, url_for, flash
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime,Column, ForeignKey, BigInteger,NVARCHAR,Integer, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from self_protection import protect,getS3cr3txLocalD,getS3cr3txLocalE  # Import your self-protection logic
import openai
import uuid
from sensitive_data_sanitizer import SensitiveDataSanitizer
from self_protection import getS3cr3txLocalE,getS3cr3txLocalD 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' #str(getS3cr3txLocalD('Tdr9azbcjb3SXdad0pHi7SyjPog6RRT1yFM7lCeyTz6dEQeEi0vfOo8mI4DM4Eh/ldrc7MlyTQ7ah+UrhXYSJ9dloEcsa6P1bMNfNTA6hKGrqZfozJLnb/W6dHLIMhhpn6dgON9jIFHJBSK4/g7AdkMc53q6r+pmjJn/epoIFDCj5iNkjPahFO+K3UtAMNJ0Ey64AM4eC7YgAUUasBmbfBxUqmCR3E1KB4Z3BNKLmX4YGB6A1qHTAs8q6OcXYuT01PcbMk64bHQ5aOkut5YxqOK9ljdqpvkmm4rTkc6sXxgx40rJJWDgBzbV7NSglndorqWXudSBvnTj25/UNfPXWF1kRdCnhqGs3zm8TAidXXebdKVEG3yx1w0JEqGeMbG+XNPkHQPJ7gej/Sxoi92fzIf5vCO9i1YoKFMMvZTnw7fEZPeHED7JkoogqTuaBid3Q8u/61HK0clNvQBNOjm9KT8P7vTwfHWzWRZp0zKgimYEKBeVRSp9vLIKMu1a8y2quD7qY7n0AYZuxwFyoHOL7bZq0Eru6lJofBizO5cEcn5EUyC1aS5+0fJwskBIRHz+2AzEVhLVkUAmLeoDmCYrdIFm05irJ8ajHoXM9SMrOJCnBL9RFsZm/9KHB1XrHN/cG/MQXomNWF68WJLigiy+cLbgNcnvLGuLn5brktIJ/MI=')).lstrip('b\'').rstrip('\'')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aishieldsDBsql3'
db = SQLAlchemy(app)

def app_context():
    app = Flask(__name__)
    with app.app_context():
        yield

Base = declarative_base()

user_prompt_api_model = Table(
    "user_prompt_api_model",
    Base.metadata,
    Column("user_id", BigInteger,ForeignKey("users.id")),
    Column("prompt_id", BigInteger, ForeignKey("inputPrompt.id")),
    Column("preproc_prompt_id",BigInteger,ForeignKey("preprocInputPrompt.id")),
    Column("apiresponse_id",BigInteger,ForeignKey("apiResponse.id")),
    Column("aishields_report_id",BigInteger,ForeignKey("aiShieldsReport.id")),
    Column("postproc_response_id",BigInteger,ForeignKey("postprocResponse.id")),
    Column("GenApi_id",BigInteger,ForeignKey("GenApi.id"))
)
user_api = Table(
    "user_api",
    Base.metadata,
    Column("user_id", BigInteger,ForeignKey("users.id")),
    Column("genapi_id", BigInteger, ForeignKey("GenApi.id")),
)

user_api_cred = Table(
    "user_api_cred",
    Base.metadata,
    Column("user_id", BigInteger),
    Column("api_id",BigInteger,ForeignKey("GenApi.id")),
    Column("cred_id",BigInteger,ForeignKey("cred")),
    Column("created_date",DateTime)
)

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    username = Column(NVARCHAR)
    first_name = Column(NVARCHAR)
    last_name = Column(NVARCHAR)
    passphrase = Column(NVARCHAR)
    email = Column(NVARCHAR)
    created_date = Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    inputPrompts = relationship("InputPrompt",secondary=user_prompt_api_model)
    preprocPrompts = relationship("PreProcInputPrompt", secondary=user_prompt_api_model)
    apiResponses = relationship("ApiResponse",secondary=user_prompt_api_model)
    postProcResponses = relationship("PostProcResponse",secondary=user_prompt_api_model)
    aiShieldsReports = relationship("AiShieldsReport",secondary=user_prompt_api_model)
    genApis = relationship(
        "GenApi", secondary=user_api, back_populates="users"
    )

class Credential(Base):
    __tablename__ = "cred"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger,ForeignKey("users.id"))
    api_id = Column(BigInteger,ForeignKey("GenApi.id"))
    username = Column(NVARCHAR)
    email = Column(NVARCHAR)
    token = Column(NVARCHAR, unique=False, nullable=True)
    jwt = Column(NVARCHAR, unique=False, nullable=True)
    header = Column(NVARCHAR, unique=False, nullable=True)
    formfield = Column(NVARCHAR, unique=False, nullable=True)
    created_date = Column(DateTime,unique=False, default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = Column(DateTime, unique=False, nullable=True)

class GenApi(Base):
    __tablename__ = "GenApi"
    id = Column(BigInteger, primary_key=True)
    uri = Column(NVARCHAR, unique=False, nullable=False)
    headers = Column(NVARCHAR, unique=False, nullable=False)
    formfields = Column(NVARCHAR, unique=False, nullable=False)
    model = Column(NVARCHAR, unique=True, nullable=False)
    created_date = Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = Column(DateTime)
    inputPrompts = relationship("InputPrompt", secondary=user_prompt_api_model)
    preprocPrompts = relationship("PreProcInputPrompt", secondary=user_prompt_api_model)
    apiResponses = relationship("ApiResponse",secondary=user_prompt_api_model)
    postProcResponses = relationship("PostProcResponse",secondary=user_prompt_api_model)
    aiShieldsReports = relationship("AiShieldsReport",secondary=user_prompt_api_model)
    users = relationship(
        "User", secondary=user_api, back_populates="genApis"
    )
# class User(db.Model):
#     id = db.Column(BigInteger, primary_key=True)
#     username = db.Column(NVARCHAR, unique=True, nullable=False)
#     email = db.Column(NVARCHAR, unique=True, nullable=False)
    
class InputPrompt(Base):
    __tablename__ = "inputPrompt"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger,ForeignKey("users.id"))
    cred_id = Column(BigInteger, ForeignKey("cred.id"))
    username = Column(NVARCHAR)
    email = Column(NVARCHAR)
    api_id = Column(BigInteger,ForeignKey("GenApi.id"))
    api = Column(NVARCHAR)
    internalPromptID = Column(NVARCHAR,unique=True)
    inputPrompt = Column(NVARCHAR)
    created_date = Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
  
    
class PreProcInputPrompt(Base):
    __tablename__ = "preprocInputPrompt"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger,ForeignKey("users.id"))
    username = Column(NVARCHAR)
    email = Column(NVARCHAR)
    api_id = Column(BigInteger,ForeignKey("GenApi.id"))
    api = Column(NVARCHAR,unique=False,nullable=False)
    internalPromptID = Column(NVARCHAR,nullable=False)
    rawInputPrompt_id = Column(BigInteger,ForeignKey("inputPrompt.id"),nullable=False)
    inputPrompt = Column(NVARCHAR,unique=False,nullable=False)
    preProcInputPrompt = Column(NVARCHAR,unique=False,nullable=False)
    SensitiveDataSanitizerReport = Column(NVARCHAR,unique=False,nullable=True)
    PromptInjectionReport = Column(NVARCHAR,unique=False,nullable=True)    
    OverrelianceReport = Column(NVARCHAR,unique=False,nullable=True)
    created_date = Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
 
class ApiResponse(Base):
    __tablename__ = "apiResponse"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger,ForeignKey("users.id"))
    username = Column(NVARCHAR)
    email = Column(NVARCHAR)
    internalPromptID = Column(NVARCHAR,unique=False,nullable=False)
    preProcPrompt_id = Column(BigInteger,ForeignKey("preprocInputPrompt.id"))
    rawInputPrompt_id = Column(BigInteger,ForeignKey("inputPrompt.id"))
    externalPromptID = Column(NVARCHAR,unique=False,nullable=False)
    api_id = Column(BigInteger,ForeignKey("GenApi.id"))
    api = Column(NVARCHAR) 
    rawoutput = Column(NVARCHAR)
    created_date = Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
      
class PostProcResponse(Base):
    __tablename__ = "postprocResponse"
    id = Column(BigInteger, primary_key=True)
    rawInputPrompt_id = Column(BigInteger, ForeignKey("inputPrompt.id"))
    internalPromptID = Column(NVARCHAR,unique=False,nullable=False)
    preProcPrompt_id = Column(BigInteger, ForeignKey("preprocInputPrompt.id"))
    externalPromptID = Column(NVARCHAR,unique=False,nullable=False)
    user_id = Column(BigInteger,ForeignKey("users.id"))
    username = Column(NVARCHAR)
    email = Column(NVARCHAR)
    api_id = Column(BigInteger,ForeignKey("GenApi.id"))
    api = Column(NVARCHAR,unique=False,nullable=False)
    rawResponseID = Column(BigInteger,ForeignKey("apiResponse.id"))
    rawOutputResponse = Column(NVARCHAR,unique=False,nullable=False)
    postProcOutputResponse = Column(NVARCHAR,unique=False,nullable=False)    
    created_date = Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    
class AiShieldsReport(Base):
    __tablename__ = "aiShieldsReport"
    id = Column(BigInteger, primary_key=True)
    rawInputPrompt_id = Column(BigInteger, ForeignKey("inputPrompt.id"))
    preProcPrompt_id = Column(BigInteger, ForeignKey("preprocInputPrompt.id"))
    rawResponse_id = Column(BigInteger, ForeignKey("apiResponse.id"))
    postProcResponse_id = Column(BigInteger, ForeignKey("postprocResponse.id"))
    internalPromptID = Column(NVARCHAR,unique=False,nullable=False)
    externalPromptID = Column(NVARCHAR,unique=False,nullable=True)
    user_id = Column(BigInteger,ForeignKey("users.id"))
    username = Column(NVARCHAR, unique=False, nullable=False)
    email = Column(NVARCHAR, unique=False, nullable=False)
    api = Column(NVARCHAR,unique=False,nullable=False)
    SensitiveDataSanitizerReport = Column(NVARCHAR,unique=False,nullable=True)
    PromptInjectionReport = Column(NVARCHAR,unique=False,nullable=True)    
    OverrelianceReport = Column(NVARCHAR,unique=False,nullable=True)
    InsecureOutputReportHandling = Column(NVARCHAR,unique=False,nullable=True)     
    created_date = Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = Column(DateTime)
    
@app.before_request
def before_request():
    # Use your self-protection logic here
    if not protect(request):
       flash('Something went wrong, please try again', 'success')
       abort(400)
    
@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return "<!DOCTYPE html><html><head><title>AiShields</title></head><body><br/><br/><center><img src='http://127.0.0.1:5000/static/aishields.jpg' alt='AiShields' style='height:300px;width:300px'/><br/><br/><form method='POST' action='/'><label for='username'>Name:&nbsp;&nbsp;&nbsp;</label><input type='text' name='username' required><br/><br/><label for='email'>Email:&nbsp;&nbsp;&nbsp;</label><input type='email' name='email' required><br/><br/><input type='submit' name='submit' value='Go'/></form></center></body></html>"
    if request.method == 'POST':
        apis = [{"APIowner":"OpenAI","TextGen": {"Name":"ChatGPT","Models":[
                {"Name":"GPT 4","details":{ "uri": "https://api.openai.com/v1/chat/completions","jsonv":"gpt-4"}},
                {"Name":"GPT 4 Turbo Preview","details":{ "uri": "https://api.openai.com/v1/chat/completions","jsonv":"gpt-4-turbo-preview" }},
                {"Name":"GPT 3.5 Turbo","details":{"uri":"https://api.openai.com/v1/chat/completions","jsonv": "gpt-3.5-turbo"}}
                ]}},
                {"APIowner":"Anthropic","TextGen": {"Name":"Claude","Models":[
                {"Name":"Most recent","details":{"uri": "https://api.anthropic.com/v1/messages","jsonv":"anthropic-version: 2023-06-01"}}]}}]
                   #,
            #{"model": "GPT 3.5 Turbo Instruct", "uri": "https://api.anthropic.com/v1/messages","jsonv":"gpt-3.5-turbo-instruct"},
            #{"model": "Babbage 2", "uri": "https://api.anthropic.com/v1/messages","jsonv":"babbage-002" },
            #{"model": "DaVinci 2","uri":"https://api.anthropic.com/v1/messages","jsonv": "davinci-002"},
        username = (
            db.session.query(User.username)
            .filter(User.username == str(request.form["username"]).upper())
            .one_or_none()
        )
        # Does the book by the author and publisher already exist?
        if username is not None:
            return render_template('chat.html',apis=apis, email=request.form.get("email"),username=request.form.get("username"))
        email = (
            db.session.query(User.id)
            .filter(User.email == str(request.form["email"]).lower())
            .one_or_none()
        )
        if email is not None:
            return render_template('chat.html',apis=apis, email=request.form.get("email"),username=request.form.get("username"))
        user = User(username=str(request.form["username"]).lower(), email=str(request.form["email"]).lower(),created_date=datetime.datetime.now(datetime.timezone.utc))
        db.session.add(user)
        db.session.commit()
        return render_template('chat.html',apis=apis, email=request.form.get("email"),username=request.form.get("username"))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    apis = [{"APIowner":"OpenAI","TextGen": {"Name":"ChatGPT","Models":[
                {"Name":"GPT 4","details":{ "uri": "https://api.openai.com/v1/chat/completions","jsonv":"gpt-4"}},
                {"Name":"GPT 4 Turbo Preview","details":{ "uri": "https://api.openai.com/v1/chat/completions","jsonv":"gpt-4-turbo-preview" }},
                {"Name":"GPT 3.5 Turbo","details":{"uri":"https://api.openai.com/v1/chat/completions","jsonv": "gpt-3.5-turbo"}}
                ]}},
                {"APIowner":"Anthropic","TextGen": {"Name":"Claude","Models":[
                {"Name":"Claude - most recent","details":{"uri": "https://api.anthropic.com/v1/messages","jsonv":"anthropic-version: 2023-06-01"}}
                 ]}}]
    if request.method == 'GET':
        return render_template('chat.html',apis=apis)
    if request.method == 'POST':
        #if protect(request):
        message = ""
        api = ""
        if request.form['api'] is not None:
            api = request.form['api']
        else:
            flash("Please select an api and model from the list")
            return render_template('chat.html',apis=apis, username=username,email=email)
        token = ""
        if request.form['apitoken'] is not None:
            token = request.form['apitoken']
        else:
            flash("Please enter an api token for the api you select")
            return render_template('chat.html',apis=apis, username=username,email=email)
        #securely store cred:
        strEncToken = getS3cr3txLocalE(token)
        token = ""
        username = ""
        if request.form['username'] is not None:
            username = str(request.form['username']).upper()
        email = ""
        if request.form['email'] is not None:
            email = str(request.form['email']).lower()
        inputprompt = ""
        if request.form['inputprompt'] is not None:
            inputprompt = request.form['inputprompt']
        else:
            flash("Please enter a prompt message to send to the api you select")
            return render_template('chat.html',apis=apis, username=username,email=email)
        user = (
            db.session.query(User.id)
            .filter(User.email == str(email).lower())
            .one_or_none()
        )
        userid = ""
        if user is not None:
            userid = user[0]
        else:
            message = "Please enter your email"
            return render_template('chat.html',apis=apis, username=username,email=email)
        storetoken = "No"
        if request.form['storetoken'] is not None:
            storetoken = request.form['storetoken']
        if storetoken == "Yes":
            cred = Credential(user_id=userid,username=str(username).upper(),email=str(email).lower(),token=strEncToken)
            db.session.add(cred)
        #preprocess the prompt
        internalID = str(uuid.uuid4())
        lstApi = str(api).split('-')
        strApi = lstApi[0]
        strModel = ""
        for a in apis:
            if a["APIowner"] == lstApi[0]:
                for m in a["TextGen"]["Models"]:
                    if m["Name"] == lstApi[2]:
                        strModel = m["details"]["jsonv"]
                        break 
                    else:
                        continue
    
        rawInput = InputPrompt(internalPromptID=internalID,user_id=userid,username=username,email=email,api=api,inputPrompt=inputprompt)
        db.session.add(rawInput)
        db.session.commit()
        preprocessedPrompt = aishields_sanitize_input(rawInput)
        strTempApiKey = str(getS3cr3txLocalD(str(strEncToken).lstrip('b\'').rstrip('\''))).lstrip('b\'').rstrip('\'')
        client = openai.Client(api_key=str(getS3cr3txLocalD(str(strEncToken).lstrip('b\'').rstrip('\''))).lstrip('b\'').rstrip('\''))
        stream = client.chat.completions.create(
            model=strModel,
            messages=[{"role": "user", "content": preprocessedPrompt}],
            stream=True,
        )
        strRawOutput = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                strRawOutput += chunk.choices[0].delta.content
        
        postprocessedPrompt = aishields_postprocess_output(strRawOutput)
        # Basic input validation (you should improve this)
            # if not username or not email:
            #     flash('Both username and email are required.', 'error')
            # else:
            #     user = User(username=username, email=email)
            #     db.session.add(user)
            #     db.session.commit()
            #     flash('User added successfully!', 'success')
    # Fetch the list of users from the database
        # prepare report
        
    return render_template('chat.html',apis=apis)
def aishields_sanitize_input(input:InputPrompt):
    #sensitive data sanitization:
    # now sanitize for privacy protected data
    strPreProcInput = ""
    strRawInputPrompt = input.inputPrompt
    sds = SensitiveDataSanitizer()
    strSensitiveDataSanitized = sds.sanitize_input(input_content=strRawInputPrompt)           
    strPreProcInput += strSensitiveDataSanitized
    #now sanitize for Prompt Injection
    #now assess for Overreliance
    return strPreProcInput
    
def aishields_postprocess_output(input:ApiResponse):
    #insecure output handing
    strPostProcessedOutput = ""
    #handle and sanitize raw output
    #return post processed Output
    return strPostProcessedOutput

def aishields_store_cred(input:Credential):
    #insecure output handing
    db.session.add(input)
    db.session.commit()
    #handle and sanitize raw output
    #return post processed Output
    return True

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
        #app.run(ssl_context=('cert.pem', 'key.pem')) #to test with https self signed cert
        
