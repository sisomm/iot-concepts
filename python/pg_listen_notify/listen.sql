CREATE TABLE departments (
  id SERIAL PRIMARY KEY,
  deptname VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(50) NOT NULL UNIQUE
);

CREATE OR REPLACE FUNCTION notify() RETURNS trigger AS $$
DECLARE
  payload TEXT;
BEGIN
/*  PERFORM pg_notify('notification', NEW.username::text); */
  payload := json_build_object('timestamp',CURRENT_TIMESTAMP,'action',LOWER(TG_OP),'schema',TG_TABLE_SCHEMA,'identity',TG_TABLE_NAME,'record',row_to_json(NEW));
  PERFORM pg_notify('notification', payload); 
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_notify_trigger
AFTER INSERT ON users
FOR EACH ROW EXECUTE PROCEDURE notify();

CREATE TRIGGER departments_notify_trigger
AFTER INSERT ON departments
FOR EACH ROW EXECUTE PROCEDURE notify();
