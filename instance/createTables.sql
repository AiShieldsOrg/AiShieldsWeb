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
INSERT INTO "users" VALUES(2,'Patrick Kelly','Patrick','Kelly','pmkelly2@icloud.com','5b55fceddeb1b8c282c10b0f6826ebd0c13390e79acce8f69419757bdbdf9086e55231d8a82356dab2decc812d1d15bd046cc7c16d2c014229dc414d804e9303',0,'2024-05-14 22:35:27.573493','2024-05-14 22:32:36.803482');
INSERT INTO "users" VALUES(3,'Patrick Kelly','Patrick','Kelly','pmkelly2@icloud.com','6ed01ed66835408e8940f2049582a245544899df3ea4a4eeeaa71bb7873687fef2c1438087574963c5a6d5ad460377880acb13bcda930ab4957e1c6c6c5416ec',1,'2024-05-14 22:40:01.806128','2024-05-14 22:32:36.803482');
INSERT INTO "users" VALUES(4,'P J','p','j','philrechani@gmail.com','e9a75486736a550af4fea861e2378305c4a555a05094dee1dca2f68afea49cc3a50e8de6ea131ea521311f4d6fb054a146e8282f8e35ff2e6368c1a62e909716',1,'2024-05-16 00:04:43.951828','2024-05-16 00:01:24.585324');
INSERT INTO "users" VALUES(5,'Akerke Kass','Akerke','Kass','akerke.kass@gmail.com','d760688da522b4dc3350e6fb68961b0934f911c7d0ff337438cabf4608789ba94ce70b6601d7e08a279ef088716c4b1913b984513fea4c557d404d0598d4f2f1',1,'2024-05-16 16:55:06.357050','2024-05-16 16:53:58.609128');
INSERT INTO "users" VALUES(6,'Patrick Kelly','Patrick','Kelly','salanghaeai123@gmail.com','9e48bce0870263f489587436e78582f197d95c3ff7836924f7a642e96fe75f090babaaf7d22dc785a68b231316f415b1f16a16f4613b92895ca0500e01d46f19',0,'2024-05-18 22:14:49.475415','2024-05-18 22:08:56.732943');
INSERT INTO "users" VALUES(7,'Patrick Kelly','Patrick','Kelly','salanghaeai123@gmail.com','04d26e4f759bc57f15996fcf364b990c29e7065e080be139f818521c5b7ee24a8e8cb5cc91a3bf8e666c8e527a571ba40d4c603aaa27bd9aa2df77334de435cf',0,'2024-05-18 22:15:10.090337','2024-05-18 22:08:56.732943');
INSERT INTO "users" VALUES(8,'Patrick Kelly','Patrick','Kelly','salanghaeai123@gmail.com','47379f11aa2ca45433b0868100e71abcabc95602dd90b9ba16b659b854a79b4a850b77635a7a7cd5d2017ee92675778029052ae485c9ff3bfb10a8cb82a9be2d',0,'2024-05-18 22:19:05.492566','2024-05-18 22:08:56.732943');
INSERT INTO "users" VALUES(9,'Patrick Kelly','Patrick','Kelly','salanghaeai123@gmail.com','cf5474c3be7190c8b41b71996eeafd1405072bc3805a26ffb3aa395ab004c49c94ef94cced179a6be748f794ec2232722c9d71316429a65351e66eecaa568bc2',0,'2024-05-18 22:19:26.254510','2024-05-18 22:08:56.732943');
INSERT INTO "users" VALUES(10,'Patrick Kelly','Patrick','Kelly','salanghaeai123@gmail.com','cf5474c3be7190c8b41b71996eeafd1405072bc3805a26ffb3aa395ab004c49c94ef94cced179a6be748f794ec2232722c9d71316429a65351e66eecaa568bc2',0,'2024-05-18 22:19:44.604489','2024-05-18 22:08:56.732943');
INSERT INTO "users" VALUES(11,'Patrick Kelly','Patrick','Kelly','patrick@gratitech.com','d9fc70c5d69603d6a45e9a62b9e032e541195bdef42059a78aa3f8ceb98dd686aa5884190bcaef306e872720b5ad7e5d291c10ea1dda50b99f53e30de80d54ce',0,'2024-05-18 22:35:53.769931','2024-05-18 22:34:04.481268');
INSERT INTO "users" VALUES(12,'Patrick Kelly','Patrick','Kelly','patrick@gratitech.com','d957c5d81acb23af053603120e3aca9a5c91e4c7b5d732514bb89b0b4b4756755797300c57a03f9f609833465c7faa4a11ad1686e0ec5636714eda392a84dc03',1,'2024-05-18 23:30:37.714793','2024-05-18 23:29:03.128762');
INSERT INTO "users" VALUES(13,'Patrick Kelly','Patrick','Kelly','05-boxiest.bushel@icloud.com','785e5ae17fd02a543e6e1f33de5fc3bf4f6a699ab344522b9a55f70e52b740ddb7477033c0cc3201549fbdf77b3f2325586bf449128ea29ffe5aeb035adf8389',1,'2024-05-19 00:37:24.296790','2024-05-19 00:31:11.506403');
INSERT INTO "users" VALUES(14,'James Yu','James','Yu','jamesyongyu@gmail.com','4289eb15f257890fc072a2f2b1c3775cb29f615c2eca89c3b345722e154403d81047d8038822967901fa7b03f7f7f2cf851d152556b737664cbb7e46be48a479',1,'2024-05-19 03:56:37.096906','2024-05-19 03:49:28.078057');
INSERT INTO "users" VALUES(15,'Manda Li','Manda','Li','manda.li8686@gmail.com','78608d88b6b6c1705f61723a686d3cf57595cb9a6332f45ec69fc1eab9704f393ea3573d9d26f58741172a871ed8a6da7788c8d35c0fc97b1604ced6c6d30bd8',1,'2024-05-19 15:49:13.409772','2024-05-19 15:48:28.276791');
INSERT INTO "users" VALUES(16,'Patrick Kelly','Patrick','Kelly','support@gratitech.com','94d72cc838a0ed81fd67c028392b5a8575c2a6ecfc1900a5c86ba1908334490d5640d75c2793bf5551a65afb11a8d7612558749d2d6dff123beeaaa68b58df5c',1,'2024-05-19 19:48:23.955217','2024-05-19 19:48:23.530222');
INSERT INTO "users" VALUES(17,'Tyler Lachney','Tyler','Lachney','tlachney.tl@gmail.com','e9a75486736a550af4fea861e2378305c4a555a05094dee1dca2f68afea49cc3a50e8de6ea131ea521311f4d6fb054a146e8282f8e35ff2e6368c1a62e909716',1,'2024-05-20 01:08:22.045891','2024-05-20 01:07:08.715139');
