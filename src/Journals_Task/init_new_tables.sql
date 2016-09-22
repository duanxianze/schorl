-- 领域
CREATE TABLE SJR_Area
( id serial,
  name varchar(50) NOT NULL,
  SJR_id int,
  CONSTRAINT area_pk PRIMARY KEY(id)
);

-- 学科
CREATE TABLE SJR_Category
( id serial ,
  name varchar(50) NOT NULL,
  area_id int NOT NULL,
  SJR_id int,
  CONSTRAINT category_pk PRIMARY KEY(id),
  CONSTRAINT area_fk FOREIGN KEY(area_id)
    REFERENCES SJR_Area(sjr_id)
);

-- 杂志和专业（多对多）
CREATE TABLE Journal_Category(
    id serial ,
    journal_id int NOT NULL,
    category_id int NOT NULL,
    CONSTRAINT JC_pk PRIMARY KEY(id)
);

-- 杂志
CREATE TABLE Journal
( id serial ,
  SJR_id int,
  name varchar(255) NOT NULL,
  publisher_id int NOT NULL,
  country varchar(200),
  CONSTRAINT journal_pk PRIMARY KEY(id),
  CONSTRAINT publisher_fk
    FOREIGN KEY(publisher_id) REFERENCES Publisher(id)
);

-- 出版商
CREATE TABLE Publisher
( id serial ,
  name varchar(255) NOT NULL,
  domain_source varchar(100),
  CONSTRAINT publisher_pk PRIMARY KEY(id)
);

CREATE TABLE Journal_Area(
  id SERIAL,
  journal_id int NOT NULL,
  area_id int NOT NULL,
  CONSTRAINT JA_pk PRIMARY KEY(id)
);



CREATE TABLE Temp_Scholar(
  id SERIAL,
  name VARCHAR(100) NOT NULL,
  CONSTRAINT TS_pk PRIMARY KEY(id),
  CONSTRAINT name_unique UNIQUE(name),
);

CREATE TABLE Scholar_Category(
  id SERIAL,
  temp_scholar_id int NOT NULL,
  category_id int NOT NULL,
  CONSTRAINT SC_pk PRIMARY KEY(id)
);

CREATE TABLE Scholar_Article(
  id SERIAL,
  temp_scholar_id int NOT NULL,
  article_id int NOT NULL,
  CONSTRAINT SA_pk PRIMARY KEY(id)
);