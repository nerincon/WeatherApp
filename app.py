import os
import tornado.ioloop
import tornado.web
import tornado.log
import psycopg2
import datetime

import json
import requests


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
    page = page + '.html'
    city = self.get_query_argument('city', None)
    weather_data = None
    if city:
      payload = {'q': city, 'APPID':'02485176f4257a69383d168ccf8c169c', 'units':'imperial'}
      r = requests.get('https://api.openweathermap.org/data/2.5/weather', params=payload)
      weather_data = r.json()
      temp = weather_data['main']['temp']
      temp_min = weather_data['main']['temp_min']
      temp_max = weather_data['main']['temp_max']
      description = weather_data['weather'][0]['description']
      wind_speed = weather_data['wind']['speed']
      nextTime = datetime.datetime.now() + datetime.timedelta(minutes = 15)
      conn = psycopg2.connect("dbname=weather_db user=postgres")
      cur = conn.cursor()
      dt = datetime.datetime.now()
      cur.execute("INSERT INTO info VALUES (%s, %s, %s, %s, %s, %s, %s)",(city, temp, temp_min, temp_max, description, wind_speed, dt))
      conn.commit()
      cur.close()
      conn.close()
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template(page, {'weather_data': weather_data})


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
