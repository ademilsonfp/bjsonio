# coding: utf-8

import unittest
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
    field = data.DictField(struct={'k': data.Field(cannone=False)})
    self.assertEqual(None, field.wipe(None))
    self.assertEqual({}, field.wipe({}))
    self.assertEqual({'k': 'hello'}, field.wipe({'k': 'hello', 'a': None}))
    self.assertRaises(data.FieldError, field.wipe, {'a': None})
    self.assertRaises(data.FieldError, field.wipe, {'k': None})
