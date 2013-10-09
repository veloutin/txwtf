from twisted.web.template import Tag

from wtforms import widgets

class Input(widgets.Input):
    def __call__(self, field, **kwargs):
        kwargs['name'] = field.name
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return Tag('input', kwargs)

class TextInput(Input):
    """
    Render a single-line text input.
    """
    input_type = 'text'


class TextArea(object):
    def __call__(self, field, **kwargs):
        kwargs['name'] = field.name
        kwargs.setdefault('id', field.id)
        value = kwargs.pop('value') if 'value' in kwargs else field._value()
        return Tag('textarea', kwargs)(value)

class Select(widgets.Select):
    def __call__(self, field, **kwargs):
        kwargs['name'] = field.name
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = 'multiple'
        return Tag('select', kwargs, [
            self.render_option(*a)
            for a in field.iter_choices()
        ])

    @classmethod
    def render_option(cls, value, label, selected):
        options = {'value':value}
        if selected:
            options['selected'] = 'selected'
        return Tag("option", options, [label])
