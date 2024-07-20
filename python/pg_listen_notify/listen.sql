CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(50) NOT NULL UNIQUE
);

CREATE OR REPLACE FUNCTION notify_new_user() RETURNS trigger AS $$
DECLARE
  payload TEXT;
BEGIN
/*  PERFORM pg_notify('users_notification', NEW.username::text); */
  payload := json_build_object('timestamp',CURRENT_TIMESTAMP,'action',LOWER(TG_OP),'schema',TG_TABLE_SCHEMA,'identity',TG_TABLE_NAME,'record',row_to_json(NEW));
  PERFORM pg_notify('users_notification', payload); 
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_notify_trigger
AFTER INSERT ON users
FOR EACH ROW EXECUTE PROCEDURE notify_new_user();
