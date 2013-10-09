
from wtforms import form

class RequestWrapper(object):
    def __init__(self, request):
        self.r = request
        self.encoding = "utf-8"

        #Attempt to get a content type encoding
        header = request.getHeader("Content-Type")
        if header:
            ctype_param = header.partition(";")[2]
            encoding = ctype_param.partition("=")[2].strip()
            if encoding:
                self.encoding = encoding

    def __contains__(self, key):
        return key in self.r.args

    def __getitem__(self, k):
        return [value.decode(self.encoding) for value in self.r.args[k]]

    getlist = __getitem__


class Form(form.Form):
    def __init__(self, request, obj=None, prefix='', **kwargs):
        self._request = request

        formdata = RequestWrapper(request)
        form.Form.__init__(self, formdata, obj, prefix, **kwargs)

    def _get_translations(self):
        return getattr(self._request, "catalog", None)


