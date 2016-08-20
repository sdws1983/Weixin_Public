# coding: UTF-8
import sys
import os
app_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(app_root, 'beautifulsoup4-4.3.2'))
sys.path.insert(0, os.path.join(app_root, 'requests-2.10.0'))
import sae
import web

from weixinInterface import WeixinInterface

urls = (
'/weixin','WeixinInterface'
)

app_root = os.path.dirname(__file__)
templates_root = os.path.join(app_root, 'templates')
render = web.template.render(templates_root)

app = web.application(urls, globals()).wsgifunc()        
application = sae.create_wsgi_app(app)
