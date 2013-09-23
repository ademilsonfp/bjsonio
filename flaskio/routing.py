# coding: utf-8

import flask, re

class MethodHandler:
  def __init__(self):
    self.methods = {}

  def add(self, *methods):
    def decor(handler):
      for method in methods:
        self.methods[method] = handler
      return handler
    return decor

  def route(self, route, rule):
    def fn(*args, **kwargs):
      return self(*args, **kwargs)
    name = rule.replace('/', '_')
    name = re.sub(r'[^_a-zA-Z0-9]', '', name)
    fn.__name__ = name
    decor = route(rule, methods=self.methods.keys())
    decor(fn)

  def __call__(self, *args, **kwargs):
    method = str(flask.request.method)
    handler = self.methods[method]
    return handler(*args, **kwargs)
