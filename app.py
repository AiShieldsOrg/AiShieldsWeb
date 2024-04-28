from flask import Flask, request, abort,render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from self_protection import protect,getS3cr3txLocalD,getS3cr3txLocalE  # Import your self-protection logic
import openai
import uuid
from sensitive_data_sanitizer import SensitiveDataSanitizer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' #str(getS3cr3txLocalD('Tdr9azbcjb3SXdad0pHi7SyjPog6RRT1yFM7lCeyTz6dEQeEi0vfOo8mI4DM4Eh/ldrc7MlyTQ7ah+UrhXYSJ9dloEcsa6P1bMNfNTA6hKGrqZfozJLnb/W6dHLIMhhpn6dgON9jIFHJBSK4/g7AdkMc53q6r+pmjJn/epoIFDCj5iNkjPahFO+K3UtAMNJ0Ey64AM4eC7YgAUUasBmbfBxUqmCR3E1KB4Z3BNKLmX4YGB6A1qHTAs8q6OcXYuT01PcbMk64bHQ5aOkut5YxqOK9ljdqpvkmm4rTkc6sXxgx40rJJWDgBzbV7NSglndorqWXudSBvnTj25/UNfPXWF1kRdCnhqGs3zm8TAidXXebdKVEG3yx1w0JEqGeMbG+XNPkHQPJ7gej/Sxoi92fzIf5vCO9i1YoKFMMvZTnw7fEZPeHED7JkoogqTuaBid3Q8u/61HK0clNvQBNOjm9KT8P7vTwfHWzWRZp0zKgimYEKBeVRSp9vLIKMu1a8y2quD7qY7n0AYZuxwFyoHOL7bZq0Eru6lJofBizO5cEcn5EUyC1aS5+0fJwskBIRHz+2AzEVhLVkUAmLeoDmCYrdIFm05irJ8ajHoXM9SMrOJCnBL9RFsZm/9KHB1XrHN/cG/MQXomNWF68WJLigiy+cLbgNcnvLGuLn5brktIJ/MI=')).lstrip('b\'').rstrip('\'')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(app)

def app_context():
    app = Flask(__name__)
    with app.app_context():
        yield


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class InputPrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api = db.Column(db.String(512),unique=False,nullable=False)
    internalPromptID = db.Column(db.String(64),unique=True,nullable=False)
    inputPrompt = db.Column(db.Text,unique=False,nullable=False)
    
class PreProcInputPrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internalPromptID = db.Column(db.String(64),unique=True,nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api = db.Column(db.String(512),unique=False,nullable=False)
    rawInputPrompt = db.Column(db.Text,unique=False,nullable=False)
    preProcInputPrompt = db.Column(db.Text,unique=False,nullable=False)
    SensitiveDataSanitizerReport = db.Column(db.Text,unique=False,nullable=True)
    PromptInjectionReport = db.Column(db.Text,unique=False,nullable=True)    
    OverrelianceReport = db.Column(db.Text,unique=False,nullable=True)
   
 
class OutputResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    internalPromptID = db.Column(db.String(64),unique=True,nullable=False)
    externalPromptID = db.Column(db.String(256),unique=True,nullable=False)
    api = db.Column(db.String(512),unique=False,nullable=False) 
    rawoutput = db.Column(db.Text,unique=False,nullable=False)
      
class PostProcOutputResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internalPromptID = db.Column(db.String(64),unique=True,nullable=False)
    externalPromptID = db.Column(db.String(256),unique=True,nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api = db.Column(db.String(512),unique=False,nullable=False)
    rawOutputPrompt = db.Column(db.Text,unique=False,nullable=False)
    postProcOutputPrompt = db.Column(db.Text,unique=False,nullable=False)    

class OutputReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internalPromptID = db.Column(db.String(64),unique=True,nullable=False)
    externalPromptID = db.Column(db.String(256),unique=True,nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api = db.Column(db.String(512),unique=False,nullable=False)
    SensitiveDataSanitizerReport = db.Column(db.Text,unique=False,nullable=False)
    PromptInjectionReport = db.Column(db.Text,unique=False,nullable=False)    
    OverrelianceReport = db.Column(db.Text,unique=False,nullable=False)
    InsecureOutputReportHandling = db.Column(db.Text,unique=False,nullable=False)     
    
@app.before_request
def before_request():
    # Use your self-protection logic here
    if not protect(request):
       flash('Something went wrong, please try again', 'success')
       abort(400)
    
@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return "<!DOCTYPE html><html><head><title>AiShields</title></head><body><center><img src='http://127.0.0.1:5000/static/aishields.jpg' alt='AiShields' style='height:300px;width:300px'/><br/><br/><form method='POST' action='/'><label for='username'>Name:&nbsp;&nbsp;&nbsp;</label><input type='text' name='username' required><br/><br/><label for='email'>Email:&nbsp;&nbsp;&nbsp;</label><input type='email' name='email' required><br/><br/><input type='submit' name='submit' value='Go'/></form></center></body></html>"
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
      
               
        #,
       #"Claude": [
       #     {"model": "Lassie", "uri": 5},
        #    {"model": "Old Yeller", "uri": 12}
       # ]
            #}
        user = User(username=request.form["username"], email=request.form["email"])
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
        api = request.form['api']
        token = request.form['apitoken']
        username = request.form['username']
        email = request.form['email']
        inputprompt = request.form['inputprompt']
        #preprocess the prompt
        internalID = str(uuid.uuid4)
        lstApi = str(api).split('-')
        strApi = lstApi[0]
        strModel = ""
        for a in apis:
            if a["APIowner"] == lstApi[0]:
                for m in a["TextGen"]["Models"]:
                    if m["Name"] == lstApi[2]:
                        strModel == m["jsonv"] 
        rawInput = InputPrompt(internalPromptID=internalID,username=username,email=email,api=api,inputPrompt=inputprompt)
        db.session.add(rawInput)
        db.session.commit()
        preprocessedPrompt = aishields_sanitize_input(rawInput)
      
        client = openai.Client(api_key=token)
        stream = client.chat.completions.create(
            model=strModel,
            messages=[{"role": "user", "content": preprocessedPrompt}],
            stream=True,
        )
        strRawOutput = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                strRawOutput += chunk.choices[0].delta.content
        rawOutput = OutputResponse()
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
    strSensitiveDataSanitized = SensitiveDataSanitizer.sanitize_input(strRawInputPrompt)           
    strPreProcInput += strSensitiveDataSanitized
    #now sanitize for Prompt Injection
    #now assess for Overreliance
    return strPreProcInput
    
def aishields_postprocess_output(input:OutputResponse):
    #insecure output handing
    strPostProcessedOutput = ""
    #handle and sanitize raw output
    #return post processed Output
    return strPostProcessedOutput

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
        #app.run(ssl_context=('cert.pem', 'key.pem')) #to test with https self signed cert
        
