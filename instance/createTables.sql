CREATE TABLE users (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    username VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    passphrase VARCHAR,
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    updated_date DATETIME NOT NULL DEFAULT(datetime())
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

CREATE TABLE GenApi (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
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
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    updated_date DATETIME NOT NULL DEFAULT(datetime()),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (cred_id) REFERENCES cred(id),
    FOREIGN KEY (api_id) REFERENCES GenApi(id)

);

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
    PromptInjectionReport VARCHAR,
    OverrelianceReport VARCHAR,
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    updated_date DATETIME NOT NULL DEFAULT(datetime()),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (api_id) REFERENCES GenApi(id),
    FOREIGN KEY (rawInputPrompt_id) REFERENCES inputPrompt(id)
);

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
    postProcOutputResponse VARCHAR,
    created_date DATETIME NOT NULL DEFAULT(datetime()),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (api_id) REFERENCES GenApi(id),
    FOREIGN KEY (rawInputPrompt_id) REFERENCES inputPrompt(id),
    FOREIGN KEY (preProcPrompt_id) REFERENCES preprocInputPrompt(id),
    FOREIGN KEY (rawResponseID) REFERENCES apiResponse(id)
);

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

INSERT INTO users
    (id, username,first_name, last_name, email)
VALUES (1,'Patrick Kelly', 'Patrick','Kelly','patrick@gratitech.org');