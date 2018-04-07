import os
import tornado.ioloop
import tornado.web
import tornado.log


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
    message = "Please put in city name"
    if city:
      payload = {'q': city, 'APPID':'02485176f4257a69383d168ccf8c169c'}
      r = requests.get('https://api.openweathermap.org/data/2.5/weather', params=payload)
      weather_data = r.json()
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template(page, {'weather_data': weather_data, 'message':message})



def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/static/(.*)", 
      tornado.web.StaticFileHandler, {'path': 'static'}),
  ], autoreload=True)


if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(int(os.environ.get('PORT', '8080')))
  tornado.ioloop.IOLoop.current().start()
