CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(50) NOT NULL UNIQUE
);

CREATE OR REPLACE FUNCTION notify_new_user() RETURNS trigger AS $$
BEGIN
  PERFORM pg_notify('users_notification', NEW.username::text);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_notify_trigger
AFTER INSERT ON users
FOR EACH ROW EXECUTE PROCEDURE notify_new_user();
