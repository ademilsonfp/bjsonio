# coding: utf-8

import re
from gettext import gettext as _, ngettext as n_

class FieldError(Exception):
  def __init__(self, field, val, msg):
    self.field = field
    self.val = val
    self.msg = msg

class Field(object):
  def __init__(self, cannone=True):
    self.cannone = cannone

  def error(self, val, msg):
    raise FieldError(self, val, msg)

  def wipe(self, val):
    if not self.cannone and None is val:
      self.error(val, _('Needs to be filled.'))
    return val

  def json(self, val):
    return val

class TextField(Field):
  def __init__(self, cannone=True, strip=True, inline=False, minlen=None,
        maxlen=None):
    Field.__init__(self, cannone)
    self.strip = strip
    self.inline = inline
    self.minlen = minlen
    self.maxlen = maxlen

  def wipe(self, val):
    val = super(TextField, self).wipe(val)
    if None is val:
      return val
    if self.strip:
      val = val.strip()
    if self.inline:
      val = re.sub(r'\s+', ' ', val)

    msg = None
    size = len(val)
    if not self.cannone and 0 is size:
      msg = _('Needs to be filled.')
    elif None is not self.minlen and self.minlen > size:
      msg = n_('Should have %d character at least.',
          'Should have %d characters at least.', self.minlen) % self.minlen
    elif None is not self.maxlen and self.maxlen < size:
      msg = n_('Should not have more than %d character.',
          'Should not have more than %d characters.', self.maxlen) \
          % self.maxlen
    if None is not msg:
      self.error(val, msg)
    return val

class DictField(Field):
  def __init__(self, cannone=True, struct=None):
    Field.__init__(self, cannone)
    self.struct = struct

  def wipe(self, val):
    val = super(DictField, self).wipe(val)
    if None is val:
      return val
    elif not isinstance(val, dict):
      self.error(val, _('Should be a dictionary.'))
    elif 0 is len(val):
      if self.cannone:
        return val
      else:
        self.error(val, _('Needs to be filled.'))
    elif None is self.struct:
      return val

    data = val
    vals = {}
    errs = {}
    for name, field in self.struct.iteritems():
      val = data.get(name, None)
      try:
        vals[name] = field.wipe(val)
      except FieldError as err:
        errs[name] = err

    num_errs = len(errs)
    if 0 < num_errs:
      val = {'!errors': errs, 'values': vals}
      msg = n_('There is a field to be fixed.',
          'There are fields to be fixed.', num_errs)
      self.error(val, msg)
    return vals
