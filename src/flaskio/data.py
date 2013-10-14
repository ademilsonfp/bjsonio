# coding: utf-8

import re
from gettext import gettext as _, ngettext as n_
import datetime

class FieldError(Exception):
  def __init__(self, field, val, msg):
    self.field = field
    self.val = val
    self.msg = msg

  def __str__(self):
    cls = self.field.__class__.__name__
    return '%s\n%s: %s' % (self.msg, cls, self.val)

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
    val = Field.wipe(self, val)
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
    val = Field.wipe(self, val)
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
          'There are %d fields to be fixed.' % num_errs, num_errs)
      self.error(val, msg)
    return vals

class DateTimeField(Field):
  FORMAT = re.compile(
      r'^(?P<year>\d{4})(?:-(?P<month>\d{2})(?:-(?P<day>\d{2})' + \
      r'(?:T(?P<hour>\d{2}):(?P<minute>\d{2})(?::(?P<second>\d{2})' + \
      r'(?P<microsecond>\.\d+)?)?(?P<tzinfo>Z|(?:-|\+)\d{2}:\d{2}))?)?)?$')

  class Tz(datetime.tzinfo):
    def __init__(self, hours=0, minutes=0):
      self.offset = datetime.timedelta(hours=hours, minutes=minutes)

    def utcoffset(self, dt):
      return self.offset

    def dst(self, dt):
      return datetime.timedelta(0)

    def __repr__(self):
      return repr(self.offset)

  def wipe(self, val):
    'based on http://www.w3.org/TR/NOTE-datetime'

    val = Field.wipe(self, val)
    if None is val:
      return val

    match = DateTimeField.FORMAT.match(val)
    if None is match:
      self.error(val, _('Should be a valid date and time.'))

    year, month, day, hour, minute, second, microsecond, tzinfo = \
        match.groups()

    dt = {'year': int(year)}
    if None is month:
      dt['month'] = 1
      dt['day'] = 1
    else:
      dt['month'] = int(month)
      if None is day:
        dt['day'] = 1
      else:
        dt['day'] = int(day)
        if None is not hour:
          tz = DateTimeField.Tz
          dt['hour'] = int(hour)
          dt['minute'] = int(minute)

          if 'Z' == tzinfo:
            dt['tzinfo'] = tz()
          else:
            delta = [int(i) for i in tzinfo.split(':')]
            if 0 > delta[0]:
              delta[1] *= -1
            dt['tzinfo'] = tz(*delta)

          if None is not second:
            dt['second'] = int(second)
          if None is not microsecond:
            dt['microsecond'] = int(1000000 * float(microsecond))

    dt = datetime.datetime(**dt)
    return dt

  def json(self, val):
    if None is val:
      return None
    elif not isinstance(val, datetime.datetime):
      raise TypeError('Invalid %s' % datetime.datetime)

    ms = re.sub(r'(\d)0+$', r'\1', val.strftime('%f'))
    tz = val.strftime('%z')
    tz = 'Z' if '' == tz or '+0000' == tz else '%s:%s' % (tz[:3], tz[3:])
    js = ''.join([val.strftime('%Y-%m-%dT%H:%M:%S.'), ms, tz])
    return js
