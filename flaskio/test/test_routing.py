# coding: utf-8

import unittest, flask
from ..routing import *

class MethodHandlerTest(unittest.TestCase):
  def test_creation(self):
    handler = MethodHandler()

    @handler.add('GET')
    def get():
      pass

    @handler.add('POST')
    def post():
      pass

    self.assertEqual(2, len(handler.methods))
    self.assertIn('GET', handler.methods)
    self.assertIn('POST', handler.methods)

    @handler.add('PUT', 'DELETE')
    def put_delete():
      pass

    self.assertEqual(4, len(handler.methods))
    self.assertIn('PUT', handler.methods)
    self.assertIn('DELETE', handler.methods)

  def test_methods(self):
    handler = MethodHandler()

    @handler.add('GET')
    def get():
      return 'GET OK'

    @handler.add('POST', 'PUT')
    def post_put():
      return 'POST PUT OK'

    app = flask.Flask(__name__)
    handler.route(app.route, '/')
    app = app.test_client()

    res = app.get('/')
    self.assertEqual(200, res.status_code)
    self.assertEqual('GET OK', res.data)

    res = app.post('/')
    self.assertEqual(200, res.status_code)
    self.assertEqual('POST PUT OK', res.data)

    res = app.put('/')
    self.assertEqual(200, res.status_code)
    self.assertEqual('POST PUT OK', res.data)

    res = app.delete('/')
    self.assertEqual(405, res.status_code)
    self.assertIn('Allow', res.headers)
    allow = res.headers['Allow']
    self.assertIn('GET', allow)
    self.assertIn('POST', allow)
    self.assertIn('PUT', allow)

  def test_rule(self):
    handler = MethodHandler()

    @handler.add('GET')
    def handle(arg0, arg1):
      return '%s %s' % (arg0, arg1)

    app = flask.Flask(__name__)
    handler.route(app.route, '/some/<arg1>/<arg0>')
    app = app.test_client()

    res = app.get('/some/second/first')
    self.assertEqual(200, res.status_code)
    self.assertEqual('first second', res.data)
