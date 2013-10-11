# coding: utf-8

import re
from gettext import gettext as _, ngettext as n_
import datetime

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

  def __str__(self):
    return '<FieldError:%s> %s' % (self.field.name, self.msg)

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
          'There are %d fields to be fixed.', num_errs) % num_errs
      self.error(val, msg)
    return vals

class DateTimeField(Field):
  FORMAT = re.compile(
      r'^(?P<year>\d{4})(?:-(?P<month>\d{2})(?:-(?P<day>\d{2}))?' + \
      r'(?:T(?P<hour>\d{2}):(?P<minute>\d{2})(?::(?P<second>\d{2})' + \
      r'(?P<microsecond>\.\d+)?)?(?P<tzinfo>Z|(?:-|\+)\d{2}:\d{2}))?)?$')

  class Tz(datetime.tzinfo):
    def __init__(self, **kwargs):
      self.offset = datetime.timedelta(**kwargs)

    def utcoffset(self, dt):
      return self.offset

  def wipe(self, val):
    'based on http://www.w3.org/TR/NOTE-datetime'

    val = Field.wipe(self, val)
    if None is val:
      return val

    regex = DateTimeField.FORMAT
    match = regex.match(val)
    if None is match:
      self.error(val, _('Should be a valid date and time.'))

    dt = match.groupdict()
    dt['year'] = int(dt['year'])

    month = dt['month']
    if None is not month:
      dt['month'] = int(month)

    day = dt['day']
    if None is not day:
      dt['day'] = int(day)

    hour = dt['hour']
    if None is not hour:
      dt['hour'] = int(hour)
      dt['minute'] = int(dt['minute'])

      second = dt['second']
      if None is not second:
        dt['second'] = int(second)

      microsecond = dt['microsecond']
      if None is not microsecond:
        dt['microsecond'] = int(1000000 * float(microsecond))

      tz = DateTimeField.Tz
      tzinf = dt['tzinfo']
      if 'Z' is tzinf:
        dt['tzinfo'] = tz()
      else:
        h, m = (int(i) for i in tzinf.split(':'))
        dt['tzinfo'] = tz(hours=h, minutes=m)

    dt = datetime.datetime(**dt)
    return dt
