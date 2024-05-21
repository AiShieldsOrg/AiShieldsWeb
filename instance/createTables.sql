CREATE TABLE GenApi (    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,api_owner VARCHAR,api_name VARCHAR,uri VARCHAR,headers VARCHAR,formfields VARCHAR,model VARCHAR,created_date DATETIME NOT NULL DEFAULT(datetime()),updated_date DATETIME NOT NULL DEFAULT(datetime()));
INSERT INTO "GenApi" VALUES(1,'OpenAI','ChatGPT','https://api.openai.com/v1/chat/completions',NULL,NULL,'gpt-4','2024-05-14 14:42:27','2024-05-14 14:42:27'),
(2,'OpenAI', 'ChatGPT','https://api.openai.com/v1/chat/completions',NULL,NULL,'gpt-4-turbo-preview','2024-05-14 14:42:27','2024-05-14 14:42:27'),
(3,'OpenAI', 'ChatGPT','https://api.openai.com/v1/chat/completions',NULL,NULL,'gpt-3.5-turbo','2024-05-14 14:42:27','2024-05-14 14:42:27'),
(4,'Anthropic', 'Claude: June 1, 2023','https://api.anthropic.com/v1/messages',NULL,NULL,'anthropic-version: 2023-06-01','2024-05-14 14:42:27','2024-05-14 14:42:27'),
(5,'Perplexity', 'Perplexity.ai: mistral-7b-instruct','https://api.perplexity.ai/chat/completions',NULL,NULL,'mistral-7b-instruct','2024-05-14 14:42:27','2024-05-14 14:42:27'),
(6,'Perplexity', 'Perplexity.ai: mixtral-8x7b-instruct','https://api.perplexity.ai/chat/completions',NULL,NULL,'mixtral-8x7b-instruct','2024-05-14 14:42:27','2024-05-14 14:42:27'),
(7,'Perplexity', 'Perplexity.ai: sonar-medium-online','https://api.perplexity.ai/chat/completions',NULL,NULL,'sonar-medium-online','2024-05-14 14:42:27','2024-05-14 14:42:27'),
(8,'Perplexity', 'Perplexity.ai: sonar-small-online','https://api.perplexity.ai/chat/completions',NULL,NULL,'sonar-small-online','2024-05-14 14:42:27','2024-05-14 14:42:27'),
(9,'Perplexity', 'Perplexity.ai: sonar-medium-chat','https://api.perplexity.ai/chat/completions',NULL,NULL,'sonar-medium-chat','2024-05-14 14:42:27','2024-05-14 14:42:27'),
(10,'Perplexity', 'Perplexity.ai: sonar-small-chat','https://api.perplexity.ai/chat/completions',NULL,NULL,'sonar-small-chat','2024-05-14 14:42:27','2024-05-14 14:42:27'),
(11,'aiShields', 'aiShields: CleanGPT','https://api.aishields.org/api/chat/completions',NULL,NULL,'aiShields-CleanGPT','2024-05-14 14:42:27','2024-05-14 14:42:27');
CREATE TABLE aiShieldsReport (    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,    rawInputPrompt_id BIGINT,    preProcPrompt_id BIGINT,    rawResponse_id BIGINT,    postProcResponse_id BIGINT,    internalPromptID VARCHAR,    externalPromptID VARCHAR,    user_id VARCHAR,    username VARCHAR,    email VARCHAR,    api_id BIGINT,    api VARCHAR,    SensitiveDataSanitizerReport VARCHAR,    PromptInjectionReport VARCHAR,    OverrelianceReport VARCHAR,    InsecureOutputReportHandling VARCHAR,    MDOSreport VARCHAR,    created_date DATETIME NOT NULL DEFAULT(datetime()),    updated_date DATETIME NOT NULL DEFAULT(datetime()),    FOREIGN KEY (user_id) REFERENCES users(id),    FOREIGN KEY (api_id) REFERENCES GenApi(id),    FOREIGN KEY (rawInputPrompt_id) REFERENCES inputPrompt(id),    FOREIGN KEY (rawResponse_id) REFERENCES apiResponse(id),    FOREIGN KEY (postProcResponse_id) REFERENCES postprocResponse(id));
INSERT INTO "aiShieldsReport" VALUES(1,1,1,1,1,'dace3b2a-9b5f-450b-97fb-813f80ddc50e','dace3b2a-9b5f-450b-97fb-813f80ddc50e2','1','Patrick Kelly','patrick@gratitech.org',1,'https://api.openai.com/v1/chat/completions','No Sensitive Data was found in the input','Not Implemented Yet','Not Implemented Yet','No insecure output was detected','Not Implemented Yet','2024-05-14 14:42:27','2024-05-14 14:42:27');
CREATE TABLE apiResponse (    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,    user_id VARCHAR,    username VARCHAR,    email VARCHAR,    internalPromptID VARCHAR,    preProcPrompt_id BIGINT,    rawInputPrompt_id BIGINT,    externalPromptID VARCHAR,    api_id BIGINT,    api VARCHAR,    rawoutput VARCHAR,    created_date DATETIME NOT NULL DEFAULT(datetime()),    FOREIGN KEY (user_id) REFERENCES users(id),    FOREIGN KEY (api_id) REFERENCES GenApi(id),    FOREIGN KEY (rawInputPrompt_id) REFERENCES inputPrompt(id),    FOREIGN KEY (preProcPrompt_id) REFERENCES preprocInputPrompt(id));
INSERT INTO "apiResponse" VALUES(1,'1','Patrick Kelly','patrick@gratitech.org','dace3b2a-9b5f-450b-97fb-813f80ddc50e',1,1,'dace3b2a-9b5f-450b-97fb-813f80ddc50e2',1,'https://api.openai.com/v1/chat/completions','Toyota invented QR codes and they are codes that store information that includes URL/URIs','2024-05-14 14:37:52');
CREATE TABLE clients(    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,    IPaddress Varchar,    MacAddress Varchar,    create_date DATETIME NOT NULL DEFAULT(datetime())   );
INSERT INTO "clients" VALUES(1,'127.0.0.1','MACADDRESS0101010101010','2024-05-14 14:37:52');
CREATE TABLE cred (    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,    user_id BIGINT,    api_id BIGINT,    username VARCHAR,    email Varchar,    token Varchar,    jwt Varchar,    header Varchar,    formfield Varchar,    created_date DATETIME NOT NULL DEFAULT(datetime()),    updated_date DATETIME NOT NULL DEFAULT(datetime()),    FOREIGN KEY (user_id) REFERENCES users(id),    FOREIGN KEY (api_id) REFERENCES GenApi(id));
INSERT INTO "cred" VALUES(1,1,1,'Patrick Kelly','patrick@gratitech.org','UFO19/34gQDiTUagB+qMVEtcuMhMrrmuwb5Zv+lQwIQRA0euVnAjR82wAhFR/Jhu7AzPz7ugf90v4W0KRdwB0oO40+ZAnyiRLwLMMtUy1Ripbsu4BoHjC7DUHcEik+TfTWusm3NdVJNrRR2gPNxLBy2do3iWKvQlnk5XbD7mf5gg8MjytkLNOYK2/Ziyi2sk7omRjKJfPZCMvYmrS2CCeah/gP67JA8oIxJmEmN6fntraziZ1k1UDZb2emHRjSEzZySV8KiozdeukjC5GZ8RDBq41xvNP8tf2Oje9cKa6VYFWbjDOrv3/yJ5HdW7/Le0GuAqVAMhqQsiG+8MstOzPemr56ZHI7j6vw0coc6RW1BGnV5UiSKOFqaNDUy0EidG+Ot4hI81Y0eslRN4TUhLl6/P45+lkTRhahov3DHyqd/W1cPtUVxlv0HpdYJQquoVK9AaWL0u3RfhBz363IN6mrEsELaPz4vZCCMQFY5IlfmnBdct+jttufz+jlRT4NjeiwTyQVd2Dc4JYt0pUovTYEIXNjtLOrTefHy5QmTXK5rsdxHEChAhB1cc1zKbUX113GI32ensEWL8/nfO0ntk3mjI7le5EPmFBJp8uGm9EgrtzVM0by2OI776hkoQRTR3MqV2oyjT/XtrRj7fk960/OJ9eUArZmQYidnW2i/EP2w=','None','None','None','2024-05-14 14:37:52','2024-05-14 14:37:52');
CREATE TABLE inputPrompt (    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,    user_id VARCHAR,    cred_id VARCHAR,    username VARCHAR,    email VARCHAR,    api_id BIGINT,    api VARCHAR,    internalPromptID VARCHAR,    inputPrompt VARCHAR,    role VARCHAR DEFAULT('user'),    created_date DATETIME NOT NULL DEFAULT(datetime()),    updated_date DATETIME NOT NULL DEFAULT(datetime()),    FOREIGN KEY (user_id) REFERENCES users(id),    FOREIGN KEY (cred_id) REFERENCES cred(id),    FOREIGN KEY (api_id) REFERENCES GenApi(id));
INSERT INTO "inputPrompt" VALUES(1,'1','1','Patrick Kelly','patrick@gratitech.org',1,'https://api.openai.com/v1/chat/completions','dace3b2a-9b5f-450b-97fb-813f80ddc50e','What are QR codes and who invented them?','user','2024-05-14 14:37:52','2024-05-14 14:37:52');
CREATE TABLE postprocResponse (    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,    rawInputPrompt_id BIGINT,    inputPromptID VARCHAR,    preProcPrompt_id BIGINT,    externalPromptID VARCHAR,    user_id VARCHAR,    username VARCHAR,    email VARCHAR,    api_id BIGINT,    api VARCHAR,    rawResponseID BIGINT,    rawOutputResponse VARCHAR,    InsecureOutputHandlingReport VARCHAR,    OverellianceOutput NVARCHAR,    postProcOutputResponse VARCHAR,    created_date DATETIME NOT NULL DEFAULT(datetime()),    FOREIGN KEY (user_id) REFERENCES users(id),    FOREIGN KEY (api_id) REFERENCES GenApi(id),    FOREIGN KEY (rawInputPrompt_id) REFERENCES inputPrompt(id),    FOREIGN KEY (preProcPrompt_id) REFERENCES preprocInputPrompt(id),    FOREIGN KEY (rawResponseID) REFERENCES apiResponse(id));
INSERT INTO "postprocResponse" VALUES(1,2,'eb55363e-6cef-4d25-8196-f343e2ded6dc',2,'','3','Patrick Kelly','pmkelly2@icloud.com',1,'https://api.openai.com/v1/chat/completions',2,'Sorry, as an AI, I don''t have real-time capabilities and can''t provide the current time. You can quickly check this by searching "current time in San Diego" in a search engine.','AiShields Data Sanitizer removed the following from the raw output
 for your safety: 
',NULL,'Sorry, as an AI, I don&#39;t have real-time capabilities and can&#39;t provide the current time. You can quickly check this by searching &#34;current time in San Diego&#34; in a search engine.','2024-05-14 22:53:23.746712');
CREATE TABLE preprocInputPrompt (    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,    user_id VARCHAR,    username VARCHAR,    email VARCHAR,    api_id BIGINT,    api VARCHAR,    internalPromptID VARCHAR,    rawInputPrompt_id BIGINT,    inputPrompt VARCHAR,    preProcInputPrompt VARCHAR,    SensitiveDataSanitizerReport VARCHAR,    PromptInjectionReport VARCHAR,    OverrelianceReport VARCHAR,    created_date DATETIME NOT NULL DEFAULT(datetime()),    updated_date DATETIME NOT NULL DEFAULT(datetime()), OverrelianceKeyphraseData nvarchar,    FOREIGN KEY (user_id) REFERENCES users(id),    FOREIGN KEY (api_id) REFERENCES GenApi(id),    FOREIGN KEY (rawInputPrompt_id) REFERENCES inputPrompt(id));
INSERT INTO "preprocInputPrompt" VALUES(1,'1','Patrick Kelly','patrick@gratitech.org',1,'https://api.openai.com/v1/chat/completions','dace3b2a-9b5f-450b-97fb-813f80ddc50e',1,'What are QR codes and who invented them?','What are QR codes and who invented them?','No sensitive data was found in the input prompt','Not Implemented Yet','Not Implemented Yet','2024-05-14 14:37:52','2024-05-14 14:37:52',NULL);
CREATE TABLE requests(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,    url varchar,    request_type varchar,    Headers varchar,    Body varchar,    client_id BIGINT,    create_date DATETIME NOT NULL DEFAULT(datetime()), client_ip varchar,     FOREIGN KEY (client_id) REFERENCES clients(id)   );
INSERT INTO "requests" VALUES(1,'https://dev.aishields.org','GET','accept: text/json',NULL,1,'2024-05-14 14:33:44',NULL);
CREATE TABLE requests_client (
	request_id BIGINT, 
	client_id BIGINT, 
	FOREIGN KEY(request_id) REFERENCES requests (id), 
	FOREIGN KEY(client_id) REFERENCES clients (id)
);
insert into requests_client(request_id,client_id) values(1,1);
CREATE TABLE user_api (
	user_id BIGINT, 
	genapi_id BIGINT, 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(genapi_id) REFERENCES GenApi (id)
);
insert into user_api(user_id,genapi_id) values(1,1);

CREATE TABLE user_api_cred (
	user_id BIGINT, 
	api_id BIGINT, 
	cred_id BIGINT, 
	created_date DATETIME DEFAULT(datetime()), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(api_id) REFERENCES GenApi (id), 
	FOREIGN KEY(cred_id) REFERENCES cred (id)
);
insert into user_api_cred(user_id,api_id,cred_id) values(1,1,1);

CREATE TABLE user_codes (    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,    user_id VARCHAR,    email VARCHAR,    code VARCHAR,    created_date DATETIME NOT NULL DEFAULT(datetime()),    FOREIGN KEY (user_id) REFERENCES users(id));
INSERT INTO user_codes VALUES(1,'1','patrick@gratitech.org','123456','2024-05-14 14:26:21');
CREATE TABLE user_codes_users (
	user_id BIGINT, 
	user_codes_id BIGINT, 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(user_codes_id) REFERENCES user_codes (id)
);
insert into user_codes_users(user_id,user_codes_id) values(1,1);

CREATE TABLE user_prompt_api_model (
	user_id BIGINT, 
	prompt_id BIGINT, 
	preproc_prompt_id BIGINT, 
	apiresponse_id BIGINT, 
	aishields_report_id BIGINT, 
	postproc_response_id BIGINT, 
	GenApi_id BIGINT, 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(prompt_id) REFERENCES "inputPrompt" (id), 
	FOREIGN KEY(preproc_prompt_id) REFERENCES "preprocInputPrompt" (id), 
	FOREIGN KEY(apiresponse_id) REFERENCES "apiResponse" (id), 
	FOREIGN KEY(aishields_report_id) REFERENCES "aiShieldsReport" (id), 
	FOREIGN KEY(postproc_response_id) REFERENCES "postprocResponse" (id), 
	FOREIGN KEY("GenApi_id") REFERENCES "GenApi" (id)
);
insert into user_prompt_api_model(user_id,prompt_id,preproc_prompt_id,apiresponse_id,aishields_report_id,postproc_response_id,GenApi_id) values(1,1,1,1,1,1,1);
CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, username VARCHAR,first_name VARCHAR,last_name VARCHAR,email VARCHAR,passphrase VARCHAR,user_verified INTEGER DEFAULT(0),created_date DATETIME NOT NULL DEFAULT(datetime()),updated_date DATETIME NOT NULL DEFAULT(datetime()));
INSERT INTO "users" VALUES(1,'Patrick Kelly','Patrick','Kelly','patrick@gratitech.org','71c01631d884f748bc65b4e05676b4003de99ea0b4fc0bb734938096918155600c04e6feb808b91c1e671f0866c4c07da92c48e93ecc10271df5e33a522122d5',1,'2024-05-14 14:42:27','2024-05-14 14:42:27');
