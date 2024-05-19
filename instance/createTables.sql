CREATE TABLE users (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    username VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    passphrase VARCHAR,
    user_verified INTEGER DEFAULT(0),
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    updated_date DATETIME NOT NULL DEFAULT(datetime())
);

CREATE TABLE user_codes (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR,
    email VARCHAR,
    code VARCHAR,
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
insert into user_codes(id,user_id,email,code)
values(1,1,"patrick@gratitech.org","123456");

CREATE TABLE request_logs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    request_type VARCHAR,
    headers TEXT,
    body TEXT,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cred (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT,
    api_id BIGINT,
    username VARCHAR,
    email Varchar,
    token Varchar,
    jwt Varchar,
    header Varchar,
    formfield Varchar,
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    updated_date DATETIME NOT NULL DEFAULT(datetime()),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (api_id) REFERENCES GenApi(id)
);
insert into cred(id,api_id,username,user_id,email,token,jwt,header,formfield)
values(1,1,'Patrick Kelly',1,"patrick@gratitech.org","UFO19/34gQDiTUagB+qMVEtcuMhMrrmuwb5Zv+lQwIQRA0euVnAjR82wAhFR/Jhu7AzPz7ugf90v4W0KRdwB0oO40+ZAnyiRLwLMMtUy1Ripbsu4BoHjC7DUHcEik+TfTWusm3NdVJNrRR2gPNxLBy2do3iWKvQlnk5XbD7mf5gg8MjytkLNOYK2/Ziyi2sk7omRjKJfPZCMvYmrS2CCeah/gP67JA8oIxJmEmN6fntraziZ1k1UDZb2emHRjSEzZySV8KiozdeukjC5GZ8RDBq41xvNP8tf2Oje9cKa6VYFWbjDOrv3/yJ5HdW7/Le0GuAqVAMhqQsiG+8MstOzPemr56ZHI7j6vw0coc6RW1BGnV5UiSKOFqaNDUy0EidG+Ot4hI81Y0eslRN4TUhLl6/P45+lkTRhahov3DHyqd/W1cPtUVxlv0HpdYJQquoVK9AaWL0u3RfhBz363IN6mrEsELaPz4vZCCMQFY5IlfmnBdct+jttufz+jlRT4NjeiwTyQVd2Dc4JYt0pUovTYEIXNjtLOrTefHy5QmTXK5rsdxHEChAhB1cc1zKbUX113GI32ensEWL8/nfO0ntk3mjI7le5EPmFBJp8uGm9EgrtzVM0by2OI776hkoQRTR3MqV2oyjT/XtrRj7fk960/OJ9eUArZmQYidnW2i/EP2w=","None","None","None");


CREATE TABLE GenApi (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    api_owner VARCHAR,
    api_name VARCHAR,
    uri VARCHAR,
    headers VARCHAR,
    formfields VARCHAR,
    model VARCHAR,
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    updated_date DATETIME NOT NULL DEFAULT(datetime())
);

CREATE TABLE inputPrompt (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR,
    cred_id VARCHAR,
    username VARCHAR,
    email VARCHAR,
    api_id BIGINT,
    api VARCHAR,
    internalPromptID VARCHAR,
    inputPrompt VARCHAR,
    role VARCHAR DEFAULT('user'),
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    updated_date DATETIME NOT NULL DEFAULT(datetime()),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (cred_id) REFERENCES cred(id),
    FOREIGN KEY (api_id) REFERENCES GenApi(id)
);
insert into inputPrompt(id,user_id,cred_id,username,email,api_id,api,internalPromptID,inputPrompt)
values(1,1,1,'Patrick Kelly','patrick@gratitech.org',1,'https://api.openai.com/v1/chat/completions','dace3b2a-9b5f-450b-97fb-813f80ddc50e','What are QR codes and who invented them?');

DROP TABLE IF EXISTS preprocInputPrompt;
CREATE TABLE preprocInputPrompt (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR,
    username VARCHAR,
    email VARCHAR,
    api_id BIGINT,
    api VARCHAR,
    internalPromptID VARCHAR,
    rawInputPrompt_id BIGINT,
    inputPrompt VARCHAR,
    preProcInputPrompt VARCHAR,
    SensitiveDataSanitizerReport VARCHAR,
    MDOSReport VARCHAR,
    PromptInjectionReport VARCHAR,
    OverrelianceReport VARCHAR,
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    updated_date DATETIME NOT NULL DEFAULT(datetime()),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (api_id) REFERENCES GenApi(id),
    FOREIGN KEY (rawInputPrompt_id) REFERENCES inputPrompt(id)
);
insert into preprocInputPrompt(id,user_id,username,email,api_id,api,internalPromptID,rawInputPrompt_id,inputPrompt,preProcInputPrompt,SensitiveDataSanitizerReport,MDOSReport,PromptInjectionReport,OverrelianceReport)
values(1,1,'Patrick Kelly','patrick@gratitech.org',1,'https://api.openai.com/v1/chat/completions','dace3b2a-9b5f-450b-97fb-813f80ddc50e',1,'What are QR codes and who invented them?','What are QR codes and who invented them?','No sensitive data was found in the input prompt','Not Implemented Yet','Not Implemented Yet','Not Implemented Yet');


CREATE TABLE apiResponse (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR,
    username VARCHAR,
    email VARCHAR,
    internalPromptID VARCHAR,
    preProcPrompt_id BIGINT,
    rawInputPrompt_id BIGINT,
    externalPromptID VARCHAR,
    api_id BIGINT,
    api VARCHAR,
    rawoutput VARCHAR,
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (api_id) REFERENCES GenApi(id),
    FOREIGN KEY (rawInputPrompt_id) REFERENCES inputPrompt(id),
    FOREIGN KEY (preProcPrompt_id) REFERENCES preprocInputPrompt(id)
);

insert into apiResponse(id,user_id,username,email,internalPromptID,preProcPrompt_id,rawInputPrompt_id,externalPromptID,api_id,api,rawoutput)
values(1,1,'Patrick Kelly','patrick@gratitech.org','dace3b2a-9b5f-450b-97fb-813f80ddc50e',1,1,'dace3b2a-9b5f-450b-97fb-813f80ddc50e2',1,'https://api.openai.com/v1/chat/completions','Toyota invented QR codes and they are codes that store information that includes URL/URIs');


CREATE TABLE postprocResponse (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    rawInputPrompt_id BIGINT,
    inputPromptID VARCHAR,
    preProcPrompt_id BIGINT,
    externalPromptID VARCHAR,
    user_id VARCHAR,
    username VARCHAR,
    email VARCHAR,
    api_id BIGINT,
    api VARCHAR,
    rawResponseID BIGINT,
    rawOutputResponse VARCHAR,
    InsecureOutputHandlingReport VARCHAR,
    OverellianceOutput VARCHAR,
    postProcOutputResponse VARCHAR,
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (api_id) REFERENCES GenApi(id),
    FOREIGN KEY (rawInputPrompt_id) REFERENCES inputPrompt(id),
    FOREIGN KEY (preProcPrompt_id) REFERENCES preprocInputPrompt(id),
    FOREIGN KEY (rawResponseID) REFERENCES apiResponse(id)
);
insert into postProcResponse(id,rawInputPrompt_id,inputPromptID,preProcPrompt_id,externalPromptID,user_id,username,email,api_id,api,rawResponseID,rawOutputResponse,InsecureOutputHandlingReport,postProcOutputResponse)
values(1,1,'dace3b2a-9b5f-450b-97fb-813f80ddc50e',1,'dace3b2a-9b5f-450b-97fb-813f80ddc50e2',1,'Patrick Kelly','patrick@gratitech.org',1,'https://api.openai.com/v1/chat/completions',1,'Toyota invented QR codes and they are codes that store information that includes URL/URIs','No insecure output was detected','Toyota invented QR codes and they are codes that store information that includes URL/URIs');

CREATE TABLE aiShieldsReport (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    rawInputPrompt_id BIGINT,
    preProcPrompt_id BIGINT,
    rawResponse_id BIGINT,
    postProcResponse_id BIGINT,
    internalPromptID VARCHAR,
    externalPromptID VARCHAR,
    user_id VARCHAR,
    username VARCHAR,
    email VARCHAR,
    api_id BIGINT,
    api VARCHAR,
    SensitiveDataSanitizerReport VARCHAR,
    MDOSReport VARCHAR,
    PromptInjectionReport VARCHAR,
    OverrelianceReport VARCHAR,
    InsecureOutputReportHandling VARCHAR,
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    updated_date DATETIME NOT NULL DEFAULT(datetime()),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (api_id) REFERENCES GenApi(id),
    FOREIGN KEY (rawInputPrompt_id) REFERENCES inputPrompt(id),
    FOREIGN KEY (rawResponse_id) REFERENCES apiResponse(id),
    FOREIGN KEY (postProcResponse_id) REFERENCES postprocResponse(id)
);

insert into aiShieldsReport(id,rawInputPrompt_id,preProcPrompt_id,rawResponse_id,postProcResponse_id,internalPromptID,externalPromptID,user_id,username,email,api_id,api,SensitiveDataSanitizerReport,MDOSReport,PromptInjectionReport,OverrelianceReport,InsecureOutputReportHandling)
values(1,1,1,1,1,'dace3b2a-9b5f-450b-97fb-813f80ddc50e','dace3b2a-9b5f-450b-97fb-813f80ddc50e2',1,'Patrick Kelly','patrick@gratitech.org',1,'https://api.openai.com/v1/chat/completions','No Sensitive Data was found in the input','Not Implemented Yet','Not Implemented Yet','No insecure output was detected');


INSERT INTO users
    (id, username,first_name, last_name, email, user_verified,passphrase)
VALUES (1,'Patrick Kelly', 'Patrick','Kelly','patrick@gratitech.org',1,'503b545192978f81f85696f362314ba468e872f75aab028a75e9115802690d0bc10e2d5f129a3bd724065e13cfb5559ead24e9c72c2b5f04ff887ae0e328865b');

INSERT INTO GenApi
    (id, api_owner, api_name, uri,model)
VALUES (1,'OpenAI', 'ChatGPT','https://api.openai.com/v1/chat/completions','gpt-4'),
(2,'OpenAI', 'ChatGPT','https://api.openai.com/v1/chat/completions','gpt-4-turbo-preview'),
(3,'OpenAI', 'ChatGPT','https://api.openai.com/v1/chat/completions','gpt-3.5-turbo'),
(4,'Anthropic', 'Claude: June 1, 2023','https://api.anthropic.com/v1/messages','anthropic-version: 2023-06-01'),
(5,'Perplexity', 'Perplexity.ai: mistral-7b-instruct','https://api.perplexity.ai/chat/completions','mistral-7b-instruct'),
(6,'Perplexity', 'Perplexity.ai: mixtral-8x7b-instruct','https://api.perplexity.ai/chat/completions','mixtral-8x7b-instruct'),
(7,'Perplexity', 'Perplexity.ai: sonar-medium-online','https://api.perplexity.ai/chat/completions','sonar-medium-online'),
(8,'Perplexity', 'Perplexity.ai: sonar-small-online','https://api.perplexity.ai/chat/completions','sonar-small-online'),
(9,'Perplexity', 'Perplexity.ai: sonar-medium-chat','https://api.perplexity.ai/chat/completions','sonar-medium-chat'),
(10,'Perplexity', 'Perplexity.ai: sonar-small-chat','https://api.perplexity.ai/chat/completions','sonar-small-chat'),
(11,'aiShields', 'aiShields: CleanGPT','https://api.aishields.org/api/chat/completions','aiShields-CleanGPT');
