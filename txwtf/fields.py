from twisted.web.template import Tag
from types import FunctionType

from wtforms import fields

from txwtf import widgets

def hijack_globals(f, **kw):
    func = f.im_func
    new_globals = dict(func.func_globals)
    new_globals.update(kw)
    return FunctionType(func.func_code,
                        new_globals,
                        func.func_name,
                        func.func_defaults,
                        func.func_closure,
                       )


class Label(fields.Label):
    def __call__(self, text=None, **kwargs):
        kwargs['for'] = self.field_id
        return Tag('label', kwargs, [text or self.text])

class Field(fields.Field):
    __init__ = hijack_globals(
        fields.Field.__init__,
        Label=Label,
    )

class TextField(fields.TextField, Field):
    widget = widgets.TextInput()

class TextAreaField(fields.TextAreaField, Field):
    widget = widgets.TextArea()

class SelectField(fields.SelectField, Field):
    widget = widgets.Select()

class IntegerField(fields.IntegerField, Field):
    widget = widgets.TextInput()

class DecimalField(fields.DecimalField, Field):
    widget = widgets.TextInput()

class DateTimeField(fields.DateTimeField, Field):
    """
    A text field which stores a `datetime.datetime` matching a format.
    """
    widget = widgets.TextInput()


class DateField(fields.DateField, Field):
    """
    Same as DateTimeField, except stores a `datetime.date`.
    """
    widget = widgets.TextInput()
