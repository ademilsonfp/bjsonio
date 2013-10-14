# coding: utf-8

import unittest
from datetime import datetime, timedelta

from .. import data

class FieldTest(unittest.TestCase):
  def test_creation(self):
    field = data.Field()
    self.assertEqual(True, field.cannone)

  def test_wipe(self):
    field = data.Field()
    self.assertEqual(1, field.wipe(1))

    field = data.Field(cannone=False)
    self.assertRaises(data.FieldError, field.wipe, None)

class TextFieldTest(unittest.TestCase):
  def test_creation(self):
    field = data.TextField()
    self.assertEqual(True, field.strip)
    self.assertEqual(False, field.inline)
    self.assertEqual(None, field.minlen)
    self.assertEqual(None, field.maxlen)

  def test_wipe(self):
    # empty test
    field = data.TextField()
    self.assertEqual(None, field.wipe(None))
    self.assertEqual('', field.wipe(''))

    field = data.TextField(cannone=False)
    self.assertEqual('foo', field.wipe('foo'))
    self.assertRaises(data.FieldError, field.wipe, None)
    self.assertRaises(data.FieldError, field.wipe, '')

    # strip test
    field.strip = False
    self.assertEqual(' foo ', field.wipe(' foo '))
    field.strip = True
    self.assertEqual('foo', field.wipe(' foo '))

    # inline test
    self.assertEqual('foo  bar', field.wipe('foo  bar '))
    field.inline = True
    self.assertEqual('foo bar', field.wipe('foo  bar '))
    self.assertEqual('foo bar', field.wipe('foo\nbar\n '))

    # minlen test
    self.assertEqual('a', field.wipe('a'))
    field.minlen = 2
    self.assertRaises(data.FieldError, field.wipe, 'a ')

    # maxlen test
    self.assertEqual('foo', field.wipe('foo'))
    field.maxlen = 2
    self.assertRaises(data.FieldError, field.wipe, 'foo')
    self.assertEqual('fo', field.wipe('fo '))

class DictFieldTest(unittest.TestCase):
  def test_creation(self):
    field = data.DictField()
    self.assertEqual(True, field.cannone)
    self.assertEqual(None, field.struct)

  def test_wipe(self):
    # empty test
    field = data.DictField()
    self.assertEqual(None, field.wipe(None))
    self.assertEqual({}, field.wipe({}))

    field = data.DictField(cannone=False)
    self.assertEqual({'k': 'v'}, field.wipe({'k': 'v'}))
    self.assertRaises(data.FieldError, field.wipe, {})
    self.assertRaises(data.FieldError, field.wipe, None)

    # type test
    self.assertRaises(data.FieldError, field.wipe, 'invalid')

    # struct test
    field = data.DictField(struct={'k': data.TextField(cannone=False)})
    self.assertEqual(None, field.wipe(None))
    self.assertEqual({}, field.wipe({}))
    self.assertEqual({'k': 'foo'}, field.wipe({'k': ' foo ', 'l': None}))
    self.assertRaises(data.FieldError, field.wipe, {'l': None})
    self.assertRaises(data.FieldError, field.wipe, {'k': None})

    # error test
    try:
      field.wipe({'k': None})
    except data.FieldError as err:
      self.assertEqual(True, isinstance(err.val, dict))
      self.assertIn('!errors', err.val)

    try:
      struct = {'a': data.TextField(), 'b': data.Field(cannone=False)}
      field = data.DictField(struct=struct)
      field.wipe({'a': ' foo '})
    except data.FieldError as err:
      self.assertEqual(True, isinstance(err.val, dict))
      self.assertIn('!errors', err.val)
      self.assertIn('b', err.val['!errors'])
      self.assertIn('values', err.val)
      self.assertIn('a', err.val['values'])
      self.assertEqual('foo', err.val['values']['a'])

class DateTimeFieldTest(unittest.TestCase):
  def test_creation(self):
    field = data.DateTimeField()
    self.assertEqual(True, field.cannone)

  def test_wipe(self):
    # empty test
    field = data.DateTimeField()
    self.assertEqual(None, field.wipe(None))

    field = data.DateTimeField(cannone=False)
    self.assertRaises(data.FieldError, field.wipe, None)

    # test full format
    tz = data.DateTimeField.Tz
    val = datetime(1997, 7, 16, 19, 20, 30, 450000, tz(1))
    self.assertEqual(val, field.wipe('1997-07-16T19:20:30.45+01:00'))

    val = datetime(1997, 7, 16, 19, 20, 30, 450000, tz(-2, -50))
    self.assertEqual(val, field.wipe('1997-07-16T19:20:30.45-02:50'))

    val = datetime(1997, 7, 16, 19, 20, 30, 450000, tz())
    self.assertEqual(val, field.wipe('1997-07-16T19:20:30.45Z'))

    # test format without decimal part of seconds
    val = datetime(1997, 7, 16, 19, 20, 30, tzinfo=tz(1))
    self.assertEqual(val, field.wipe('1997-07-16T19:20:30+01:00'))

    val = datetime(1997, 7, 16, 19, 20, 30, tzinfo=tz(-2, -50))
    self.assertEqual(val, field.wipe('1997-07-16T19:20:30-02:50'))

    val = datetime(1997, 7, 16, 19, 20, 30, tzinfo=tz())
    self.assertEqual(val, field.wipe('1997-07-16T19:20:30Z'))

    # test format without seconds
    val = datetime(1997, 7, 16, 19, 20, tzinfo=tz(1))
    self.assertEqual(val, field.wipe('1997-07-16T19:20+01:00'))

    val = datetime(1997, 7, 16, 19, 20, tzinfo=tz(-2, -50))
    self.assertEqual(val, field.wipe('1997-07-16T19:20-02:50'))

    val = datetime(1997, 7, 16, 19, 20, tzinfo=tz())
    self.assertEqual(val, field.wipe('1997-07-16T19:20Z'))

    # test format without time
    val = datetime(1997, 7, 16)
    self.assertEqual(val, field.wipe('1997-07-16'))

    # test format without day
    val = datetime(1997, 7, 1)
    self.assertEqual(val, field.wipe('1997-07'))

    # test format without month
    val = datetime(1997, 1, 1)
    self.assertEqual(val, field.wipe('1997'))

    # test some invalids
    self.assertRaises(data.FieldError, field.wipe, 'foo')
    self.assertRaises(data.FieldError, field.wipe, '1997-07-16T19:20')
    self.assertRaises(data.FieldError, field.wipe, '1997-07-1619:20Z')
    self.assertRaises(data.FieldError, field.wipe, '1997-07T19:20Z')
    self.assertRaises(data.FieldError, field.wipe, '1997-07-16T19Z')
    self.assertRaises(data.FieldError, field.wipe, '1997-07-16T19:20:Z')

  def test_json(self):
    # empty test
    field = data.DateTimeField()
    self.assertEqual(None, field.json(None))

    # test all arguments
    tz = data.DateTimeField.Tz
    dt = datetime(1997, 7, 16, 19, 20, 30, 450000, tz(1))
    self.assertEqual('1997-07-16T19:20:30.45+01:00', field.json(dt))

    dt = datetime(1997, 7, 16, 19, 20, 30, 450000, tz(-2, -50))
    self.assertEqual('1997-07-16T19:20:30.45-02:50', field.json(dt))

    dt = datetime(1997, 7, 16, 19, 20, 30, 450000, tz())
    self.assertEqual('1997-07-16T19:20:30.45Z', field.json(dt))

    # test format without microtime
    dt = datetime(1997, 7, 16, 19, 20, 30, tzinfo=tz(1))
    self.assertEqual('1997-07-16T19:20:30.0+01:00', field.json(dt))

    dt = datetime(1997, 7, 16, 19, 20, 30, tzinfo=tz(-2, -50))
    self.assertEqual('1997-07-16T19:20:30.0-02:50', field.json(dt))

    dt = datetime(1997, 7, 16, 19, 20, 30, tzinfo=tz())
    self.assertEqual('1997-07-16T19:20:30.0Z', field.json(dt))

    # test format without second
    dt = datetime(1997, 7, 16, 19, 20, tzinfo=tz(1))
    self.assertEqual('1997-07-16T19:20:00.0+01:00', field.json(dt))

    dt = datetime(1997, 7, 16, 19, 20, tzinfo=tz(-2, -50))
    self.assertEqual('1997-07-16T19:20:00.0-02:50', field.json(dt))

    dt = datetime(1997, 7, 16, 19, 20, tzinfo=tz())
    self.assertEqual('1997-07-16T19:20:00.0Z', field.json(dt))

    # test format without time
    dt = datetime(1997, 7, 16)
    self.assertEqual('1997-07-16T00:00:00.0Z', field.json(dt))

    # test invalid
    self.assertRaises(TypeError, field.json, 'foo')
