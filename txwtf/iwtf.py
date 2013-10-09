from zope.interface import Interface

class ITranslations(Interface):

    def gettext(message):
        """
        Return the localized translation of message
        """

    def ngettext(singular, plural, n):
        """
        Do a plural-forms lookup of a message id. singular is used as the
        message id for purposes of lookup in the catalog, while n is used to
        determine which plural form to use. The returned message string is a
        Unicode string.
        """
