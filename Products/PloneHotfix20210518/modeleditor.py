# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from lxml import etree
from plone.app.dexterity.browser.modeleditor import AjaxSaveHandler
from plone.app.dexterity.browser.modeleditor import authorized
from plone.supermodel.parser import SupermodelParseError
from Products.CMFPlone.utils import safe_unicode
from zope.i18nmessageid import MessageFactory

import json
import plone.supermodel


_ = MessageFactory("plone")
NAMESPACE = '{http://namespaces.plone.org/supermodel/schema}'


def __call__(self):
    """Handle AJAX save post.

    This is a copy of the code from plone.app.dexterity version 2.6.8,
    where we fixed this in November 2020.
    We did not think a hotfix was needed then, but now we have a few similar patches.
    """

    if not authorized(self.context, self.request):
        raise Unauthorized

    source = self.request.form.get('source')
    if source:
        # Is it valid XML?
        # Some safety measures.
        # We do not want to load entities, especially file:/// entities.
        # Also discard processing instructions.
        parser = etree.XMLParser(resolve_entities=False, remove_pis=True)
        try:
            root = etree.fromstring(source, parser=parser)
        except etree.XMLSyntaxError as e:
            return json.dumps({
                'success': False,
                'message': 'XMLSyntaxError: {0}'.format(
                    safe_unicode(e.args[0])
                )
            })

        # a little more sanity checking, look at first two element levels
        if root.tag != NAMESPACE + 'model':
            return json.dumps({
                'success': False,
                'message': _(u"Error: root tag must be 'model'")
            })
        for element in root.getchildren():
            if element.tag != NAMESPACE + 'schema':
                return json.dumps({
                    'success': False,
                    'message': _(
                        u"Error: all model elements must be 'schema'"
                    )
                })

        # can supermodel parse it?
        # This is mainly good for catching bad dotted names.
        try:
            plone.supermodel.loadString(source, policy=u'dexterity')
        except SupermodelParseError as e:
            message = e.args[0].replace('\n  File "<unknown>"', '')
            return json.dumps({
                'success': False,
                'message': u'SuperModelParseError: {0}'.format(message)
            })

        # clean up formatting sins
        source = etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding='utf8'
        )
        # and save to FTI
        fti = self.context.fti
        fti.manage_changeProperties(model_source=source)

        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps({'success': True, 'message': _(u'Saved')})


AjaxSaveHandler.__call__ = __call__
