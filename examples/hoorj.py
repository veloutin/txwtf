#coding: utf-8
import gettext

from twisted.application import internet, service
from twisted.web.resource import Resource
from twisted.web.template import (
    XMLString, Element, TagLoader,
    renderer, flatten, tags
)

import wtforms as wtf
from wtforms import validators

from txwtf import forms, fields

def NewProjectForm(request):
    try:
        _ = request.catalog.gettext
    except AttributeError:
        _ = lambda o:o

    class NewProjectForm(forms.Form):
        client_long = fields.TextField(_("Client Name"),
                                       id="parent",
                                       validators=[validators.Required()])
        bill_method = fields.SelectField(_("Billing Method"),
                                    choices=(
                                        ("hourly", _("Hourly")),
                                        ("project", _("Project")),
                                        ("mixed", _("Part Hourly, Part Project")),
                                    )
                                    )

        estimated_hours = fields.IntegerField(_("Estimated Hours"),
                                           validators=[
                                               validators.NumberRange(min=0),
                                               validators.Required(),
                                           ])
        deadline = fields.DateField(_("Deadline"))

        comments = fields.TextAreaField(_("Comments"))

    return NewProjectForm(request)

_transcache = {}
def get_translations(languages=None, cache=_transcache):
    domain = gettext.textdomain()
    lang = tuple(languages) if languages else None
    key = (domain, lang)
    if key not in cache:
        cache[key] = gettext.Catalog(
            domain,
            localedir=gettext.bindtextdomain(domain),
            fallback=True,
            languages=languages)

    return cache[key]

def parseAcceptLanguage(header):
    if header is None:
        return header
    else:
        return [
            "_".join([o.lower(), u.upper()]) if sep else o.lower()
            for o, sep, u in [
                lang.strip().partition(";")[0].partition("-")
                for lang in sorted(
                    header.split(","),
                    key=lambda o:-float(
                        o.partition(";")[2].partition("=")[2] or "1.0"
                    ))
            ]
        ]

def setRequestCatalog(request):
    languages = parseAcceptLanguage(request.getHeader("Accept-Language"))
    request.catalog = get_translations(languages)
    return request



TEMPLATE="""
<div xmlns:t="http://twistedmatrix.com/ns/twisted.web.template/0.1"
    id="NewProjectForm"
    title="New Project"
    t:render="gettext">
    <form>
    <t:attr name="action"><t:slot name="action" default="." /></t:attr>
    <t:attr name="method">POST</t:attr>
    <div t:render="hidden_tag" />
    <table>
    <tr t:render="visible_fields">
        <th t:render="label" />
        <td t:render="field" />
        <td class="errors" t:render="errors">
          <ul>
            <li t:render="error" />
          </ul>
        </td>
    </tr>
    <tr><td>
    <input type="submit">
        <t:attr name="value"><t:slot name="submit" default="Submit" /></t:attr>
    </input>
    </td></tr>
    </table>
    </form>
</div>
"""
class FieldElement(Element):
    def __init__(self, loader, field):
        Element.__init__(self, loader)
        self.f = field

    @renderer
    def label(self, request, tag):
        return tag(self.f.label())

    @renderer
    def field(self, request, tag):
        return tag(self.f())

    @renderer
    def errors(self, request, tag):
        if self.f.errors:
            return tag
        else:
            tag.clear()
            return ''

    @renderer
    def error(self, request, tag):
        for error in self.f.errors:
            yield tag.clone()(error)


class FormElement(Element):
    """
    Form Element renderer
    """

    loader = XMLString(TEMPLATE)
    def __init__(self, form, attrs=None):
        self.form = form
        if attrs is None:
            attrs = {}
        self.attrs = attrs

    @renderer
    def action(self, request, tag):
        return tag('')

    @renderer
    def hidden_tag(self, request, tag):
        tag.attributes["display"] = "none"
        for field in self.form:
            if getattr(field.widget, "input_type", "") == "hidden":
                tag(field(**self.attrs.get(field.id, {})))
        return tag

    @renderer
    def visible_fields(self, request, tag):
        for field in self.form:
            if getattr(field.widget, "input_type", "") != "hidden":
                yield FieldElement(TagLoader(tag), field)

    @renderer
    def gettext(self, request, tag):
        _ = request.catalog.gettext
        return tag.fillSlots(
            submit=_("Submit"),
        )

LAYOUT = """<html xmlns:t="http://twistedmatrix.com/ns/twisted.web.template/0.1">
<head>
    <meta http-equiv="Content-type" content="text/html;charset=UTF-8" />
    <title t:render="title" />
</head>
<body>
    <div class="page" t:render="content" />
</body>
</html>"""

class Layout(Element):
    loader = XMLString(LAYOUT)

    def __init__(self, content):
        Element.__init__(self)
        self._content = content

    @renderer
    def title(self, request, tag):
        _ = request.catalog.gettext
        return tag(_('Hoorj!'))

    @renderer
    def content(self, request, tag):
        return self._content

class MyResource(Resource):
    def __init__(self, form_factory):
        Resource.__init__(self)
        self.form = form_factory

    def getChild(self, path, request):
        return self

    def render(self, request):
        setRequestCatalog(request)
        form = self.form(request)
        request.write('<!DOCTYPE html>\n')
        if request.method == "POST" and form.validate():
            content = tags.span("Form Valid!")
        else:
            content = FormElement(form)

        done = flatten(request, Layout(content), request.write)
        done.addCallback(lambda r: request.finish())
        return server.NOT_DONE_YET

from twisted.web import server
from twisted.internet import reactor
site = server.Site(MyResource(NewProjectForm))
application = service.Application('web')

sc = service.IServiceCollection(application)
i = internet.TCPServer(8000, site)
i.setServiceParent(sc)
