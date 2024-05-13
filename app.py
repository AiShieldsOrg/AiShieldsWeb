from flask import Flask, request, abort,render_template, redirect, url_for, flash
from flask_wtf import CSRFProtect
import bleach
from markupsafe import escape
from dateutil.relativedelta import relativedelta
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime,Column, ForeignKey, BigInteger,NVARCHAR,Integer, Table, desc, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from self_protection import protect,sanitize_input,getHash,encStandard,decStandard  
import openai
import uuid
from sensitive_data_sanitizer import SensitiveDataSanitizer
from aishieldsemail import send_secure_email
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = str(decStandard('OY/PyvGbiR1wZE+cbnnQt9xQ966z2GflY0E7nykRhfGh4CzfMThApARnADUuRG6qRK0apXfOHBD+GR5/cENiAAzrKhr4JBYexQaSTRTpvpH0PjG51O/L3okyW5GgNDXtPRUkruNJPtrmIjqnk9fy5LI/agzGN7nULnC1VUJosnmRXl57g6+TX8VBU2Q2HT8D5GXenELrN65QNka09tNBIblj+qKuWE9LEnkt1I+n0iTvjsoDi8i5szhVNsWy+WYcwRM7cFJq70ExUK61sr90hbitpWsgvgZjzTBI9xQwNKSMAG2HnJvCM/khkiqZEXZEObaq7kYtph0aR3BK6ANdT5ToW7w/Ct/qmZU74pr/rivvvbWbtgGv3gzLcvdhRS5nntezTWUda568iF18JhVrCyoZIwpvMbTWrF9baXGBCzEhyFLl4VAh8Gw36/1PFaqJCKMlCdQLUntQjqHkX/Kc+vIo58TlvC/rGIWYd2tPf8TDi/vuSeB3hPAkdTRv3eN+YTGC855AL2Nuu/N1i70IF6yGQ4lLSTSWGHEyx/z2nqkqhIkbF7W+4TXQaAXbJOaXOZgz6HiaUmM6eBQpiveKnGBT88IKmknPGgIzPr94iib0x2cgSwwmHXDzxADJJ3/UUYVg6m2/hF3/9Igjyt8N2dxJV/y2V8iPV7UONN1Nzy0='))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/JamesYu/Desktop/GitHub/AiShieldsFlaskWeb/AiShieldsWeb/instance/aiShieldsDB3.db'
email_from = "o0FXog44BPM62bHG96j9Ot9naWeswZibyGTt3x7eb1Oxtf4Wg3aaacJwEfbqZH7X2VbKqvcDv636sheQwlfMGx0ES23dm+Ea4ld4W6DcfP7rTj2RF8pAsqX5gGqakRebDF64nX/mcahSRhlA71JlVd6Bf9moq1f3OdvDeL5yebgnYVHTo9Ojn+s5uSk514chxV8pGgl92eHouVGFj9dh0111lAS9q7iTWOJq108owjQPMZzPD/AftdQFhorzGDqqQ62JMqlFVkZy4XCd9ui/sSr7CzdAaRZv+sAuF2dYX5EK8C537vCd7MjC1AB+o0UdnNcavIB/Kjv+7UdYw42pX1Rpe9fwBWDSDNpgitVkIYBRQjdgiois9XOYl2fhot3Y1l3XeWByFUplyTgoEAqv/mcWqIflsZIuOGQqmymEi0DHsRrW1ygkdUkyZJKma2J3O/TwxaKNqeGAW2dEeu06CS0cNNfyVzpJnRe6LeUOA2Ea5V5KGTR3gB1KqovGAcODpyrgg+dahjzGWFJVSAn6xpIxQggb5jKSwkgEaeE90dYa3eMx7wXpwCAGfZG3N8b/TeTCoNMrNEnmqITzEr67v5eja4cVUzDFz58x3gWb0Dc+3rIHvzdNfAbkCukcJmdJwiQjE17MAVofMECohKh41A7cuxXl6gDKDftmHio28bI="
smtpserver = "JUMDLB4OB2LGkiIfOH0fg+Icvt7oL3K9yrv/IL4jGeEFAuQsF3Beg5ccK+pL9dpHN+onlcCFjVYk2YDoJmfKpDulCo5W1I2Gq9QWF5jdBTcsMiUFciLnTGcBop0WNdV5mpWb/A5dw5319iRoXlC377nPCnJZFoy5B1DooQvkg4J+EZiF9CboDd84V6Av1uxm1iKUondXdq32q7b6kLFhtV2eZKlsbLb6QpIhhnfkPGt35Ob6xNyK4R4PX6NgjjjvuepEL4RV0g4QuR+jgDeuE4aLONiwv9ygtoa0cTq4aob8AoGNIJld5Q9vun5y7x7Tnp3drn9hvy1Mi2cs6wjQpNkPleYpemhTPeJrFM1OAOeTCfetEnn9tFiqdkBt+uW+V6mtXDVTVT/I1Xwuvl0db05tsFq8tXHqp+/QOtaZmqLincGXT1p/grLeFVDvYZdPPfz0czXDPiewKFX3DqmAgYG4DEazimVrpqsbbP4RHYYI4MCiXncypwgTEfLdP4i8ZvWcd/A27BiSW6fyv4fMjO0kCViJBlZ9Pj1QxfvqEwMPo7y/lJBwKIjspT50DF+U2iwDrNDzi2e7t/dsiQ9tTQ4y8DVwhyY8wE5dKQ2wqWRcpHU6ipMyxKq5Fs2WnVldZcn3g5buMrPRSMiJVY0DmnrPDmqUHRyvQzxlEg+uUKg="
smtpport = "WymM5C7FEi8IfMVTxBxV+JoJbnLApXfS1iHCnannQw9vHA9F33Z9E3p9YMjl7+rK9gAEZGgnLpUgSikhpBzDWDV4/sIBNUl0iuZq79Wk+2cPEROIq3ZZNJlwNbsvJoFvJ2T6laws5ObaleaGeN6LjaSURTFytRntT7NuunNylRvjFGHEMMYW/ONgx92XL0pr8XrPyNeaaEvWbR5ftENvjy27ZVRj+M1hl8y17H/pkXLzc/MQQCwBN0D2iMlHch3pVzxnwlgEAAlWMNf/euK9PPeg9NJuQG3bic3QLIOrlHkMvefdwPK1lkbIZJCjcoYFWuOoE5P/UPEWMpAox2EtbwgPNfVackbnOlpZv5hXfg0dtyDoefPBJevTBeIWUk+cyhvGmJ68flz1f+VL/ug4fy5bHfCcZ7v0ouLuB7g99MIr0gwt4lQA/esyybtImTRZMvC/RkYsoKiyNb1Bgp9qDGjLJYpolYUSR/ZO48whF90GoPrN8un4X9lyw0ffWtJUNkDlIK4j8UDbjVu0pE3QABYPFfEk+qGyzQdWgVe3mwcBEPkF5PohYjeSss162w5hXan8DE3+Lg22LS53WBfwp29qpe0nC/lrR/emianhTNT2u1cKP4zvf4bDjix4opZvu4xs3fO4xn62rkOImZiT3lUR1wx0pxfUd2C5f0NL9G4="
smtpp = "ZaWCMeTE17PO90tootuP0oOPJALMUPvk8zDdgaPn/sVP5Ge8JRIDxNgZBNlle7hfm0sdJrtTrLgcp6pN7Kkdm/GdUdj3eoCq2+omm74912GO/xwkLzY7cd6CUVPFNmE+1NR4TuJbk86Oz47DVhTbMwK+o2i6yCDZYe4BVUoIt7Tzne0zHcvaVxtkYP5WEfeq0fgLrCnemK5aQrHU5FlNNcHSrx4uvdXueoyIoL3F/GPUMloeSIYP6TlUQhGE1URADtkmegTwpLOus70LUbmbLRmXLtfw2s9QkZ1jovGfq8JCMFbUmjoLix1yxQhnaubs7vW72JoGNpQ6iQ490ucdW4bI4YsAFdIgmjLOTS7ip6K1uzVNadEIyLmAQgGZkfw4rdv/wP75hNxeVvqxHco4YKUIVMJQeujKDSXpM+q2bdt/mvTSqU0HF16Ktqb85pifvdrl+5KoukzkyO+3376Oe8s5qkXhWixqhCkXEA4NmWHSxRGtbkQsn/V4g0lWvUoKW7NKaPrbhPHtkTJ9PiCoLaQZTMb2TjHNxwRGFMotNCIR4AukgttDEQ2GTmBIHX7Ohk5Vl7f4urOjj3Hd69mdslLlsh6QavWu0MoZe5HG/rAUpWcDP6TmAccwEZXC1xTR3+044HjWQ4/eT2JJyt0keMCmmGe3wufKyKMNKoeFBLk="
smtpu = "o0FXog44BPM62bHG96j9Ot9naWeswZibyGTt3x7eb1Oxtf4Wg3aaacJwEfbqZH7X2VbKqvcDv636sheQwlfMGx0ES23dm+Ea4ld4W6DcfP7rTj2RF8pAsqX5gGqakRebDF64nX/mcahSRhlA71JlVd6Bf9moq1f3OdvDeL5yebgnYVHTo9Ojn+s5uSk514chxV8pGgl92eHouVGFj9dh0111lAS9q7iTWOJq108owjQPMZzPD/AftdQFhorzGDqqQ62JMqlFVkZy4XCd9ui/sSr7CzdAaRZv+sAuF2dYX5EK8C537vCd7MjC1AB+o0UdnNcavIB/Kjv+7UdYw42pX1Rpe9fwBWDSDNpgitVkIYBRQjdgiois9XOYl2fhot3Y1l3XeWByFUplyTgoEAqv/mcWqIflsZIuOGQqmymEi0DHsRrW1ygkdUkyZJKma2J3O/TwxaKNqeGAW2dEeu06CS0cNNfyVzpJnRe6LeUOA2Ea5V5KGTR3gB1KqovGAcODpyrgg+dahjzGWFJVSAn6xpIxQggb5jKSwkgEaeE90dYa3eMx7wXpwCAGfZG3N8b/TeTCoNMrNEnmqITzEr67v5eja4cVUzDFz58x3gWb0Dc+3rIHvzdNfAbkCukcJmdJwiQjE17MAVofMECohKh41A7cuxXl6gDKDftmHio28bI="

smtp_server = str(decStandard(smtpserver))
smtp_port = str(decStandard(smtpport))
smtp_p = str(decStandard(smtpp))
smtp_u = str(decStandard(smtpu))
db = SQLAlchemy(app)
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
    strAppKey = ''
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

class RequestLog(db.Model):
    __tablename__ = "request_logs"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(255), nullable=False)  # Assuming client ID is a string
    request_type = db.Column(db.String(255))
    headers = db.Column(db.Text)  # Using Text instead of NVARCHAR for compatibility
    body = db.Column(db.Text)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    def __init__(self, client_id, request_type, headers, body):
        self.client_id = client_id
        self.request_type = request_type
        self.headers = headers
        self.body = body

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
    created_date = db.Column(DateTime,default=datetime.datetime.now(datetime.timezone.utc))
    updated_date = db.Column(DateTime)
    
import json

@app.before_request
def before_request():
    # Save the request data for MDOS protection
    request_data = RequestLog(
        client_id=request.remote_addr,  # Assuming client IP is sufficient
        request_type=request.method,
        headers=json.dumps(dict(request.headers)),
        body=request.data.decode('utf-8')
    )
    db.session.add(request_data)
    db.session.commit()

    # MDOS (Model Denial of Service entrypoint)
    # James Yu can add code here to handle MDOS protection
    client_id = request.remote_addr
    request_count = RequestLog.get_request_count(client_id)
    if not protect(request):
        # MDOS (Model Denial of Service entrypoint)
        flash('Something went wrong, please try again', 'success')
        abort(400)
    elif request_count >= 10:  # Adjust the limit as needed
        flash('Too many requests, please try again later', 'danger')
        print(request_count)
        abort(429)  # Too Many Requests status code
    
@app.route("/",methods=['GET','POST'])
def home():
    return redirect(url_for('index'))

@app.route("/index",methods=['GET','POST'])
def index():
    try:
        if request.method == 'GET':
            return render_template('index.html',apis=apis, email=request.form.get("email"))
        if request.method == 'POST':
            #,
                #{"model": "GPT 3.5 Turbo Instruct", "uri": "https://api.anthropic.com/v1/messages","jsonv":"gpt-3.5-turbo-instruct"},
                #{"model": "Babbage 2", "uri": "https://api.anthropic.com/v1/messages","jsonv":"babbage-002" },
                #{"model": "DaVinci 2","uri":"https://api.anthropic.com/v1/messages","jsonv": "davinci-002"},
            email = (
                db.session.query(User)
                .filter(User.email == str(request.form.get('email')).lower(),User.user_verified==1).order_by(desc(User.id))
                .first()
            )
            if email is None:
                flash("Please create an account")
                return render_template('newaccount.html',apis=apis, email=request.form.get("email"))
            else:
                # user = User(username="", email=str(request.form["email"]).lower(),user_verified=0,created_date=datetime.datetime.now(datetime.timezone.utc))
                # db.session.add(user)
                # db.session.commit()
                return render_template('login.html',apis=apis, email=request.form.get("email"))
    except Exception as err:
        print('An error occured: ' + str(err))  
        return render_template('index.html',apis=apis, email=request.form.get("email"))
     
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
            return render_template("login.html")
    except Exception as err:
        print('An error occured: ' + str(err))


@app.route('/login',methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'GET':
            return render_template('login.html', email=request.form.get("email"),username=request.form.get("username"))
        if request.method == 'POST':
            user_entered_code = getHash(str(request.form["passphrase"]))
            user =  (db.session.query(User)
                .filter(User.email == str(request.form["email"]).lower(), User.passphrase==str(user_entered_code),User.user_verified==1).order_by(desc(User.created_date))
                .one_or_none()
                ) 
            if user is not None:
                #print(str(user().id))
                if str(user.passphrase) == user_entered_code:
                    if int(user.user_verified) == 1:
                        return render_template('chat.html', email=user.email,username=user.first_name + " " + user.last_name,apis=apis)
                    else:
                        strCode = ""
                        for i in range(6):
                            strCode += str(secrets.randbelow(10))
                        user_id = user().id
                        code = UserCode(user_id=user_id,email=user().email,code=strCode)
                        db.session.add(code)
                        db.session.commit()
                        db.session.flush(objects=[code])
                        to_email = user().email
                        from_email = smtp_u
                        s_server = smtp_server
                        s_port = smtp_port
                        s_p = smtp_p
                        m_subj = "Please verify your email for AiShields.org"
                        m_message = "Dear " + user().first_name + ", \n\n Please enter the following code: " + strCode + " in the email verification form. \n\n Thank you, \n\n Support@AiShields.org"
                        send_secure_email(to_email,from_email,s_server,s_port,from_email,s_p,m_subj,m_message)
                        return render_template('verifyemail.html',apis=apis, email=user().email,username=user().first_name + " " + user().last_name)
                else:
                    flash("The username and password combination you used did not match our records")
                    return render_template('login.html')
            else:
                return render_template('login.html')
    except Exception as err:
        print('An error occured: ' + str(err))   
        
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
        print('An error occured: ' + str(err))  
 
@app.route('/reset',methods=['GET','POST'])
def reset():
    try:
        if request.method == 'GET':
            strCode = request.query_string.decode('utf-8').split('=')[1]
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
                return render_template('login.html')
            else:
                return render_template("login.html")
        else:
            return render_template("login.html")
    except Exception as err:
        print('An error occured: ' + str(err))
        return render_template("login.html")

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
                .one_or_none()
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
                    m_subj = "Please reset your email for AiShields.org"
                    m_message = "Dear " + user.first_name + ", \n\n Please click this link: <a href='http://127.0.0.1:5000/reset?code=" + strCode +"' or paste it into your browser address bar to change your password. \n\nThis link will expire in 20 minutes. \n\n Thank you, \n\n Support@AiShields.org"
                    send_secure_email(to_email,from_email,s_server,s_port,from_email,s_p,m_subj,m_message)
                    return render_template('login.html')
            else:
                return render_template("login.html")
        else:
            return render_template("login.html")
    except Exception as err:
        print('An error occured: ' + str(err))
        return render_template("login.html")
        

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    try:
        if request.method == 'GET':
            user = (
                        db.session.query(User)
                        .filter(User.email == str(email).lower(),User.user_verified == 1)
                        .one_or_none()
                    )
            if user is not None:
                return render_template('newaccount.html',apis=apis,email=request.form["email"])
            return render_template('chat.html',apis=apis,email=request.form["email"],username=user.username)
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
            strEncToken = encStandard(token)
            token = ""
            username = ""
            if request.form['username'] is not None:
                username = str(request.form['username'])
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
                db.session.query(User)
                .filter(User.email == str(email).lower(),User.user_verified ==1).order_by(desc(User.id))
                .first()
            )
            userid = ""
            if user is not None:
                userid = user.id
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
            lstApi = str(api).split(' ')
            strApi = lstApi[0]
            strModel = lstApi[1]
            rawInput = InputPrompt(internalPromptID=internalID,user_id=userid,username=username,email=email,api=api,inputPrompt=inputprompt)
            db.session.add(rawInput)
            db.session.commit()
            db.session.flush(objects=[rawInput])
            rawInputObj = (
                db.session.query(InputPrompt)
                .filter(InputPrompt.internalPromptID == internalID)
                .one_or_none)
            apiObj = (
                db.session.query(GenApi)
                .filter(GenApi.model == str(strModel),GenApi.api_owner == strApi)
                .one_or_none)
            strRole = "user"
            if request.form['role'] is not None:
                strRole = request.form['role']
            if apiObj:
                preprocessedPromptString = aishields_sanitize_input(rawInput)
                preprocessedPrompt = PreProcInputPrompt(
                    internalPromptID=internalID,
                    user_id=userid,
                    api_id=apiObj().id,
                    api=apiObj().uri,
                    email=email,
                    rawInputPrompt_id=rawInputObj().id,
                    inputPrompt=rawInput.inputPrompt,
                    preProcInputPrompt=preprocessedPromptString,
                    username=username,
                    SensitiveDataSanitizerReport = "AiShields Data Sanitizer removed the following from the raw input\n for your safety: \n" + str(escape(aishields_get_string_diff(rawInput.inputPrompt,preprocessedPromptString))),
                    PromptInjectionReport = "",
                    OverrelianceReport = ""
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
                    api_id=apiObj().id,
                    api=apiObj().uri,
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
                rawOutputObj = (
                    db.session.query(ApiResponse)
                        .filter(ApiResponse.internalPromptID == internalID)
                        .one_or_none)
                preProcObj = (
                    db.session.query(PreProcInputPrompt)
                        .filter(PreProcInputPrompt.internalPromptID == internalID)
                        .one_or_none)
                postProcPromptObj = PostProcResponse(
                    rawInputPrompt_id = rawInputObj().id,
                    inputPromptID = internalID,
                    preProcPrompt_id = preProcObj().id,
                    externalPromptID = rawOutput.externalPromptID,
                    user_id = userid,
                    username = username,
                    email = email,
                    api_id = apiObj().id,
                    api = apiObj().uri,
                    rawResponseID = rawOutputObj().id,
                    rawOutputResponse = rawOutputObj().rawoutput,
                    postProcOutputResponse = "",
                    InsecureOutputHandlingReport = "",
                    created_date = datetime.datetime.now(datetime.timezone.utc)
                )
                postProcPromptObj = aishields_postprocess_output(postProcPromptObj)
                db.session.add(postProcPromptObj)
                db.session.commit()
                db.session.flush(objects=[postProcPromptObj])
                postProcRespObj = (
                    db.session.query(PostProcResponse)
                        .filter(PostProcResponse.inputPromptID == internalID)
                        .one_or_none)
                postProcID = -1
                if postProcRespObj is not None:
                    postProcID = postProcRespObj().id 
                # prepare report
                aiShieldsReportObj = AiShieldsReport(
                    rawInputPrompt_id = rawInputObj().id,
                    internalPromptID = internalID,
                    preProcPrompt_id = preProcObj().id,
                    externalPromptID = rawOutput.externalPromptID,
                    user_id = userid,
                    username = username,
                    email = email,
                    api_id = apiObj().id,
                    api = apiObj().uri,
                    rawResponse_id = rawOutputObj().id,
                    #rawOutputResponse = rawOutputObj().rawoutput,
                    #postProcOutputResponse = postProcRespObj().postProcOutputResponse,    
                    created_date = datetime.datetime.now(datetime.timezone.utc),
                    postProcResponse_id = postProcRespObj().id,
                    SensitiveDataSanitizerReport = preProcObj().SensitiveDataSanitizerReport,
                    PromptInjectionReport = preProcObj().PromptInjectionReport,    
                    OverrelianceReport = preProcObj().OverrelianceReport,
                    InsecureOutputReportHandling = postProcRespObj().InsecureOutputHandlingReport,     
                    updated_date = datetime.datetime.now(datetime.timezone.utc)
                )
                db.session.add(aiShieldsReportObj)
                db.session.commit()
                db.session.flush(objects=[aiShieldsReportObj])
                findings = [{"category":"Sensitive Data","details":aiShieldsReportObj.SensitiveDataSanitizerReport,"id":aiShieldsReportObj.internalPromptID},
                { "category":"Prompt Injection","details":aiShieldsReportObj.PromptInjectionReport,"id":aiShieldsReportObj.internalPromptID},
                {"category":"Overreliance","details":aiShieldsReportObj.OverrelianceReport,"id":aiShieldsReportObj.internalPromptID},
                {"category":"Insecure Output Handling","details":aiShieldsReportObj.InsecureOutputReportHandling,"id":aiShieldsReportObj.internalPromptID}]
                
        return render_template('chat.html',apis=apis,email=email,username=username,response=postProcRespObj().postProcOutputResponse,findings=findings,output=True)
    except Exception as err:
        print('An error occured: ' + str(err)) 
        return render_template('chat.html',apis=apis,email=email,username=username) 

def aishields_sanitize_input(input:InputPrompt):
        #sensitive data sanitization:
        # now sanitize for privacy protected data
    try:
        strPreProcInput = ""
        strRawInputPrompt = input.inputPrompt
        sanitizedInput = sanitize_input(strRawInputPrompt)
        #sds = SensitiveDataSanitizer()
        #strSensitiveDataSanitized = sds.sanitize_input(input_content=strRawInputPrompt)           
        strPreProcInput += str(sanitizedInput)
        #now sanitize for Prompt Injection
        #now assess for Overreliance
        return strPreProcInput
    except Exception as err:
        print('An error occured: ' + str(err))  
    
def aishields_postprocess_output(postProcResponseObj:PostProcResponse):
    #insecure output handing
    try:
        strPostProcessedOutput = sanitize_input(postProcResponseObj.rawOutputResponse)
        postProcResponseObj.postProcOutputResponse = escape(str(strPostProcessedOutput))
        postProcResponseObj.InsecureOutputHandlingReport = "AiShields Data Sanitizer removed the following from the raw output\n for your safety: \n" + str(escape(aishields_get_string_diff(postProcResponseObj.rawOutputResponse,strPostProcessedOutput)))
        #handle and sanitize raw output
        #return post processed Output
        return postProcResponseObj
    except Exception as err:
        print('An error occured: ' + str(err))  

def aishields_store_cred(input:Credential):
    try:
        #insecure output handing
        db.session.add(input)
        db.session.commit()
        #handle and sanitize raw output
        #return post processed Output
        return True
    except Exception as err:
        print('An error occured: ' + str(err))  
        
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
        db.session.query(UserCode).filter(UserCode.id > 1, UserCode.id < 38).delete()
        db.commit()
        #app.run(ssl_context=('cert.pem', 'key.pem')) #to test with https self signed cert
        
