#
# Copyright (c) 2013, Digium, Inc.
#

"""Swagger processors enrich and validate the Swagger data model.

This can be to make templating easier, or ensure values required for a
particular use case (such as ensuring that description and summary fields
exist)
"""

class ParsingContext(object):
    """Context information for parsing.

    This object is immutable. To change contexts (like adding an item to the
    stack), use the next() and next_stack() functions to build a new one.
    """

    def __init__(self):
        self.type_stack = []
        self.id_stack = []
        self.args = {'context': self}

    def __repr__(self):
        zipped = list(zip(self.type_stack, self.id_stack))
        strs = ["%s=%s" % (t, i) for (t, i) in zipped]
        return "ParsingContext(stack=%r)" % strs

    async def is_empty(self):
        """Tests whether context is empty.

        :return: True if empty, False otherwise.
        """
        return not self.type_stack and not self.id_stack

    async def push(self, obj_type, json, id_field):
        """Pushes a new self-identifying object into the context.

        :type obj_type: str
        :param json: Specifies type of object json represents
        :type json: dict
        :param json: Current Jsonified object.
        :type id_field: str
        :param id_field: Field name in json that identifies it.
        """
        if id_field not in json:
            raise BaseException ("Missing id_field: %s" % id_field)
        await self.push_str(obj_type, json, str(json[id_field]))

    async def push_str(self, obj_type, json, id_string):
        """Pushes a new object into the context.

        :type obj_type: str
        :param obj_type: Specifies type of object json represents
        :type json: dict
        :param json: Current Jsonified object.
        :type id_string: str
        :param id_string: Identifier of the given json.
        """
        self.type_stack.append(obj_type)
        self.id_stack.append(id_string)
        self.args[obj_type] = json

    async def pop(self):
        """Pops the most recent object out of the context
        """
        del self.args[self.type_stack.pop()]
        self.id_stack.pop()


async def SwaggerError(error):
    """Raised when an error is encountered mapping the JSON objects into the
    model.
    """
    raise BaseException (error)


class SwaggerProcessor(object):
    """Post processing interface for Swagger API's.

    This processor can add fields to model objects for additional
    information to use in the templates.
    """

    async def apply(self, resources):
        """Apply this processor to a loaded Swagger definition.

        :param resources: Top level Swagger definition.
        :type  resources: dict
        """
        context = ParsingContext()
        print(context)
        resources_url = resources.get('url') or 'json:resource_listing'
        print(resources_url)
        await context.push_str('resources', resources, resources_url)
        print(context)
        await self.process_resource_listing(**context.args)
        for listing_api in resources['apis']:
            await context.push('listing_api', listing_api, 'path')
            await self.process_resource_listing_api(**context.args)
            await context.pop()

            api_url = listing_api.get('url') or 'json:api_declaration'
            await context.push_str('resource', listing_api['api_declaration'], api_url)
            await self.process_api_declaration(**context.args)

            for api in listing_api['api_declaration']['apis']:
                await context.push('api', api, 'path')
                await self.process_resource_api(**context.args)
                for operation in api['operations']:
                    await context.push('operation', operation, 'nickname')
                    await self.process_operation(**context.args)
                    for parameter in operation.get('parameters', []):
                        await context.push('parameter', parameter, 'name')
                        await self.process_parameter(**context.args)
                        await context.pop()
                    for response in operation.get('errorResponses', []):
                        await context.push('error_response', response, 'code')
                        await self.process_error_response(**context.args)
                        await context.pop()
                    await context.pop()
                await context.pop()
            models = listing_api['api_declaration'].get('models', {})
            for (name, model) in list(models.items()):
                await context.push('model', model, 'id')
                await self.process_model(**context.args)
                for (name, prop) in list(model['properties'].items()):
                    await context.push('prop', prop, 'name')
                    await self.process_property(**context.args)
                    await context.pop()
                await context.pop()
            await context.pop()
        await context.pop()
        assert await context.is_empty(), "Expected %r to be empty" % context

    async def process_resource_listing(self, resources, context):
        """Post process a resources.json object.

        :param resources: ResourceApi object.
        :type context: ParsingContext
        :param context: Current context in the API.
        """
        pass

    async def process_resource_listing_api(self, resources, listing_api, context):
        """Post process entries in a resource.json's api array.

        :param resources: Resource listing object
        :param listing_api: ResourceApi object.
        :type context: ParsingContext
        :param context: Current context in the API.
        """
        pass

    async def process_api_declaration(self, resources, resource, context):
        """Post process a resource object.

        This is parsed from a .json file reference by a resource listing's
        'api' array.

        :param resources: Resource listing object
        :param resource: resource object.
        :type context: ParsingContext
        :param context: Current context in the API.
        """
        pass

    async def process_resource_api(self, resources, resource, api, context):
        """Post process entries in a resource's api array

        :param resources: Resource listing object
        :param resource: resource object.
        :param api: API object
        :type context: ParsingContext
        :param context: Current context in the API.
        """
        pass

    async def process_operation(self, resources, resource, api, operation, context):
        """Post process an operation on an api.

        :param resources: Resource listing object
        :param resource: resource object.
        :param api: API object
        :param operation: Operation object.
        :type context: ParsingContext
        :param context: Current context in the API.
        """
        pass

    async def process_parameter(self, resources, resource, api, operation, parameter,
                          context):
        """Post process a parameter on an operation.

        :param resources: Resource listing object
        :param resource: resource object.
        :param api: API object
        :param operation: Operation object.
        :param parameter: Parameter object.
        :type context: ParsingContext
        :param context: Current context in the API.
        """
        pass

    async def process_error_response(self, resources, resource, api, operation,
                               error_response, context):
        """Post process an errorResponse on an operation.

        :param resources: Resource listing object
        :param resource: resource object.
        :param api: API object
        :param operation: Operation object.
        :param error_response: Response object.
        :type context: ParsingContext
        :param context: Current context in the API.
        """
        pass

    async def process_model(self, resources, resource, model, context):
        """Post process a model from a resources model dictionary.

        :param resources: Resource listing object
        :param resource: resource object.
        :param model: Model object.
        :type context: ParsingContext
        :param context: Current context in the API.
        """
        pass

    async def process_property(self, resources, resource, model, prop, context):
        """Post process a property from a model.

        :param resources: Resource listing object
        :param resource: resource object.
        :param model: Model object.
        :param prop: Property object.
        :type context: ParsingContext
        :param context: Current context in the API.
        """
        pass


# noinspection PyDocstring
class WebsocketProcessor(SwaggerProcessor):
    """Process the WebSocket extension for Swagger
    """

    async def process_resource_api(self, resources, resource, api, context):
        api.setdefault('has_websocket', False)

    async def process_operation(self, resources, resource, api, operation, context):
        operation['is_websocket'] = operation.get('upgrade') == 'websocket'

        if operation['is_websocket']:
            api['has_websocket'] = True
            if operation['httpMethod'] != 'GET':
                raise SwaggerError(
                    "upgrade: websocket is only valid on GET operations",
                    context
                )


# noinspection PyDocstring
class FlatenningProcessor(SwaggerProcessor):
    """Flattens model and property dictionaries into lists.

    Mustache requires a regular schema.
    """

    async def process_api_declaration(self, resources, resource, context):
        resource.model_list = list(resource.models.values())

    async def process_model(self, resources, resource, model, context):
        # Convert properties dict to list
        model.property_list = list(model.properties.values())
