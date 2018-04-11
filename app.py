import os
import tornado.ioloop
import tornado.web
import tornado.log
import psycopg2
import datetime

import json
import requests

from weather_func import get_db_data, get_api_data

from jinja2 import \
  Environment, PackageLoader, select_autoescape

ENV = Environment(
  loader=PackageLoader('myapp', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)


class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))


class MainHandler(TemplateHandler):
  def get (self, page='index'):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    page = page + '.html'
    city = self.get_query_argument('city', None)
    timeDelta = datetime.timedelta(minutes=15)
    weather_data = None
    conn = psycopg2.connect("dbname=weather_db user=postgres")
    cur = conn.cursor()
    if city:
      payload = {'q': city, 'APPID':'02485176f4257a69383d168ccf8c169c', 'units':'imperial'}
      r = requests.get('https://api.openweathermap.org/data/2.5/weather', params=payload)
      weather_data = r.json()
      dt = datetime.datetime.utcnow()
      print(city, type(city))
      cur.execute("SELECT DISTINCT(city) FROM info WHERE city = %s", [city])
      row = cur.fetchone()
      db_city = None
      if row:
        db_city = row[0]
      cur.execute("SELECT time_stamp FROM info WHERE city = %s", [city])
      row = cur.fetchone()
      db_timestamp = None
      if row:
        db_timestamp = row[0]
      print(db_city, dt, db_timestamp)
      if db_city is None:
        print("{} not in database".format(city))
        temp, temp_min, temp_max, description, wind_speed = get_api_data(city)
        cur.execute("INSERT INTO info VALUES (%s, %s, %s, %s, %s, %s, %s)",(city, temp, temp_min, temp_max, description, wind_speed, dt))
        conn.commit()
        weather_data_db = get_db_data(city, cur)
        self.render_template(page, {'weather_data_db': weather_data_db})
      elif city in db_city  and (dt - db_timestamp) > timeDelta:
        print("{} will be stored in db again to update city info".format(city))
        temp, temp_min, temp_max, description, wind_speed = get_api_data(city)
        cur.execute("DELETE FROM info WHERE city = (%s)",[city])
        cur.execute("INSERT INTO info VALUES (%s, %s, %s, %s, %s, %s, %s)",(city, temp, temp_min, temp_max, description, wind_speed, dt))
        conn.commit()
        weather_data_db = get_db_data(city, cur)
        print(weather_data_db)
        self.render_template(page, {'weather_data_db': weather_data_db})
      elif city in db_city and (dt - db_timestamp) < timeDelta:
        weather_data_db = get_db_data(city, cur)
        self.render_template(page, {'weather_data_db': weather_data_db})
    cur.close()
    conn.close()
    if not weather_data:
      self.render_template(page, {})


def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/static/(.*)", 
      tornado.web.StaticFileHandler, {'path': 'static'}),
  ], autoreload=True)


if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(int(os.environ.get('PORT', '8000')))
  tornado.ioloop.IOLoop.current().start()
