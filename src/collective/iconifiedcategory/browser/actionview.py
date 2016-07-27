# -*- coding: utf-8 -*-
"""
collective.iconifiedcategory
----------------------------

Created by mpeeters
:license: GPL, see LICENCE.txt for more details.
"""

from Products.Five import BrowserView
from z3c.json.interfaces import IJSONWriter
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
from zope.lifecycleevent import ObjectModifiedEvent

from collective.iconifiedcategory import _
from collective.iconifiedcategory import utils
from collective.iconifiedcategory.event import IconifiedPrintChangedEvent
from collective.iconifiedcategory.event import IconifiedConfidentialChangedEvent


class BaseView(BrowserView):
    attribute_mapping = {}

    def _translate(self, msgid):
        return translate(
            msgid,
            domain='collective.iconifiedcategory',
            context=self.request,
        )

    def __call__(self):
        writer = getUtility(IJSONWriter)
        values = {'status': 0, 'msg': 'success'}
        try:
            self.request.response.setHeader('content-type',
                                            'application/json')
            status, msg = self.set_values(self.get_values())
            values['status'] = status
            if msg:
                values['msg'] = self._translate(msg)
            notify(ObjectModifiedEvent(self.context))
        except Exception:
            values['status'] = 1
            values['msg'] = self._translate(_('Error during process'))
        return writer.write(values)

    def get_current_values(self):
        return {k: self.context.get(k) for k in self.attribute_mapping.keys()}

    def get_values(self):
        return {k: self.request.get(v)
                for k, v in self.attribute_mapping.items()}

    def set_values(self, values):
        for key, value in values.items():
            self.set_value(key, value)

    def set_value(self, attrname, value):
        setattr(self.context, attrname, value)

    @staticmethod
    def convert_boolean(value):
        values = {
            'false': False,
            'true': True,
        }
        return values.get(value, value)


class ToPrintChangeView(BaseView):
    attribute_mapping = {
        'to_print': 'iconified-value',
    }

    def set_values(self, values):
        old_values = self.get_current_values()
        values['to_print'] = self.convert_boolean(values['to_print'])
        super(ToPrintChangeView, self).set_values(values)
        notify(IconifiedPrintChangedEvent(
            self.context,
            old_values,
            values,
        ))
        return 0, utils.print_message(self.context)


class ConfidentialChangeView(BaseView):
    attribute_mapping = {
        'confidential': 'iconified-value',
    }

    def set_values(self, values):
        old_values = self.get_current_values()
        values['confidential'] = self.convert_boolean(values['confidential'])
        super(ConfidentialChangeView, self).set_values(values)
        notify(IconifiedConfidentialChangedEvent(
            self.context,
            old_values,
            values,
        ))
        return 0, utils.confidential_message(self.context)