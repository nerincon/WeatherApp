CREATE TABLE info (
  city VARCHAR,
  temp VARCHAR,
  temp_min VARCHAR,
  temp_max VARCHAR,
  description VARCHAR,
  wind_speed VARCHAR,
  time_stamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);