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
    # empty
    field = data.TextField(cannone=False)
    self.assertEqual('foo', field.wipe('foo'))
    self.assertRaises(data.FieldError, field.wipe, None)
    self.assertRaises(data.FieldError, field.wipe, '')

    # strip
    field.strip = False
    self.assertEqual(' foo ', field.wipe(' foo '))
    field.strip = True
    self.assertEqual('foo', field.wipe(' foo '))

    # inline
    self.assertEqual('foo  bar', field.wipe('foo  bar '))
    field.inline = True
    self.assertEqual('foo bar', field.wipe('foo  bar '))
    self.assertEqual('foo bar', field.wipe('foo\nbar\n '))

    # minlen
    self.assertEqual('a', field.wipe('a'))
    field.minlen = 2
    self.assertRaises(data.FieldError, field.wipe, 'a ')

    # maxlen
    self.assertEqual('foo', field.wipe('foo'))
    field.maxlen = 2
    self.assertRaises(data.FieldError, field.wipe, 'foo')
    self.assertEqual('fo', field.wipe('fo '))

