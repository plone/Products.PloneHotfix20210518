# -*- coding: utf-8 -*-
from ._compat import string_types
from lxml import etree
from plone.supermodel import parser as supermodel_parser
from plone.supermodel.debug import parseinfo
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.interfaces import I18N_NAMESPACE
from plone.supermodel.interfaces import IFieldExportImportHandler
from plone.supermodel.interfaces import IFieldMetadataHandler
from plone.supermodel.interfaces import ISchemaMetadataHandler
from plone.supermodel.interfaces import ISchemaPolicy
from plone.supermodel.model import Fieldset
from plone.supermodel.model import Model
from plone.supermodel.model import Schema
from plone.supermodel.model import SchemaClass
from plone.supermodel.utils import ns
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component import queryUtility
from zope.dottedname.resolve import resolve
from zope.schema import getFields


try:
    from plone.supermodel.interfaces import IInvariant
except ImportError:
    # IInvariant was added in plone.supermodel 1.2.5, Plone 4.3.4.
    IInvariant = None

try:
    from plone.supermodel.interfaces import DEFAULT_ORDER
except ImportError:
    # DEFAULT_ORDER was added in plone.supermodel 1.3.0, Plone 5.0.5.
    DEFAULT_ORDER = None


def _parse(source, policy):
    # Some safety measures.
    # We do not want to load entities, especially file:/// entities.
    # Also discard processing instructions.
    parser = etree.XMLParser(resolve_entities=False, remove_pis=True)
    tree = etree.parse(source, parser=parser)
    root = tree.getroot()

    parseinfo.i18n_domain = root.attrib.get(
        ns('domain', prefix=I18N_NAMESPACE)
    )

    model = Model()

    handlers = {}
    schema_metadata_handlers = tuple(getUtilitiesFor(ISchemaMetadataHandler))
    field_metadata_handlers = tuple(getUtilitiesFor(IFieldMetadataHandler))

    policy_util = getUtility(ISchemaPolicy, name=policy)

    def readField(fieldElement, schemaAttributes, fieldElements, baseFields):

        # Parse field attributes
        fieldName = fieldElement.get('name')
        fieldType = fieldElement.get('type')

        if fieldName is None or fieldType is None:
            raise ValueError(
                'The attributes \'name\' and \'type\' are required for each '
                '<field /> element'
            )

        handler = handlers.get(fieldType)
        if handler is None:
            handler = handlers[fieldType] = queryUtility(
                IFieldExportImportHandler,
                name=fieldType
            )
            if handler is None:
                raise ValueError(
                    'Field type {0} specified for field {1} is not '
                    'supported'.format(fieldType, fieldName)
                )

        field = handler.read(fieldElement)

        # Preserve order from base interfaces if this field is an override
        # of a field with the same name in a base interface
        base_field = baseFields.get(fieldName)
        if base_field is not None:
            field.order = base_field.order

        # Save for the schema
        schemaAttributes[fieldName] = field
        fieldElements[fieldName] = fieldElement

        return fieldName

    for schema_element in root.findall(ns('schema')):
        parseinfo.stack.append(schema_element)
        schemaAttributes = {}

        schemaName = schema_element.get('name')
        if schemaName is None:
            schemaName = u""

        bases = ()
        baseFields = {}
        based_on = schema_element.get('based-on')
        if based_on is not None:
            bases = tuple([resolve(dotted) for dotted in based_on.split()])
            for base_schema in bases:
                baseFields.update(getFields(base_schema))

        fieldElements = {}

        # Read global fields
        for fieldElement in schema_element.findall(ns('field')):
            parseinfo.stack.append(fieldElement)
            readField(
                fieldElement,
                schemaAttributes,
                fieldElements,
                baseFields
            )
            parseinfo.stack.pop()

        # Read invariants, fieldsets and their fields
        invariants = []
        fieldsets = []
        fieldsets_by_name = {}

        for subelement in schema_element:
            parseinfo.stack.append(subelement)

            if subelement.tag == ns('field'):
                readField(
                    subelement,
                    schemaAttributes,
                    fieldElements,
                    baseFields
                )

            elif subelement.tag == ns('fieldset'):

                fieldset_name = subelement.get('name')
                if fieldset_name is None:
                    raise ValueError(
                        u'Fieldset in schema {0} has no name'.format(
                            schemaName
                        )
                    )

                fieldset = fieldsets_by_name.get(fieldset_name)
                if fieldset is None:
                    fieldset_label = subelement.get('label')
                    fieldset_description = subelement.get('description')
                    if DEFAULT_ORDER is None:
                        fieldset = fieldsets_by_name[fieldset_name] = Fieldset(
                            fieldset_name,
                            label=fieldset_label,
                            description=fieldset_description,
                        )
                    else:
                        fieldset_order = subelement.get('order')
                        if fieldset_order is None:
                            fieldset_order = DEFAULT_ORDER
                        elif isinstance(fieldset_order, string_types):
                            fieldset_order = int(fieldset_order)
                        fieldset = fieldsets_by_name[fieldset_name] = Fieldset(
                            fieldset_name,
                            label=fieldset_label,
                            description=fieldset_description,
                            order=fieldset_order,
                        )
                    fieldsets_by_name[fieldset_name] = fieldset
                    fieldsets.append(fieldset)

                for fieldElement in subelement.findall(ns('field')):
                    parseinfo.stack.append(fieldElement)
                    parsed_fieldName = readField(
                        fieldElement,
                        schemaAttributes,
                        fieldElements,
                        baseFields
                    )
                    if parsed_fieldName:
                        fieldset.fields.append(parsed_fieldName)
                    parseinfo.stack.pop()

            elif IInvariant is not None and subelement.tag == ns('invariant'):
                dotted = subelement.text
                invariant = resolve(dotted)
                if not IInvariant.providedBy(invariant):
                    raise ImportError(
                        u'Invariant functions must provide '
                        u'plone.supermodel.interfaces.IInvariant'
                    )
                invariants.append(invariant)
            parseinfo.stack.pop()

        schema = SchemaClass(
            name=policy_util.name(schemaName, tree),
            bases=bases + policy_util.bases(schemaName, tree) + (Schema,),
            __module__=policy_util.module(schemaName, tree),
            attrs=schemaAttributes
        )

        # add invariants to schema as tagged values
        if invariants:
            schema_invariants = schema.queryTaggedValue('invariants', [])
            schema.setTaggedValue('invariants', schema_invariants + invariants)

        # Save fieldsets
        schema.setTaggedValue(FIELDSETS_KEY, fieldsets)

        # Let metadata handlers write metadata
        for handler_name, metadata_handler in field_metadata_handlers:
            for fieldName in schema:
                if fieldName in fieldElements:
                    metadata_handler.read(
                        fieldElements[fieldName],
                        schema,
                        schema[fieldName]
                    )

        for handler_name, metadata_handler in schema_metadata_handlers:
            metadata_handler.read(schema_element, schema)

        model.schemata[schemaName] = schema
        parseinfo.stack.pop()

    parseinfo.i18n_domain = None
    return model


supermodel_parser._parse = _parse
