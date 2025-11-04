from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class BuilderSchemaView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        schema = {
            "name": {
                "type": "string",
                "label": "Party Name",
                "required": True
            },
            "trim_amount": {
                "type": "string",
                "label": "Trim Price SqFt",
                "required": False
            },
            "rough_amount": {
                "type": "string",
                "label": "Rough Price SqFt",
                "required": False
            },
            "travel_price_amount": {
                "type": "string",
                "label": "Travel Amount",
                "required": False
            },
            "rfc": {
                "type": "string",
                "label": "RFC",
                "required": False
            },
            "street": {
                "type": "string",
                "label": "Street",
                "required": False
            },
            "floor_office": {
                "type": "string",
                "label": "Floor/Office",
                "required": False
            },
            "city": {
                "type": "string",
                "label": "City",
                "required": False
            },
            "state": {
                "type": "string",
                "label": "State",
                "required": False
            },
            "zipcode": {
                "type": "string",
                "label": "Zip Code",
                "required": False
            },
            "country": {
                "type": "string",
                "label": "Country",
                "required": False
            },
            "phone": {
                "type": "string",
                "label": "Phone",
                "required": False
            },
            "email": {
                "type": "string",
                "label": "Email",
                "required": False
            },
            "types": {
                "type": "select",
                "label": "Party Types",
                "required": False,
                "optionsEndpoint": "/api/party-types/?ordering=name",
                "multiple": True
            },
            "category": {
                "type": "select",
                "label": "Category",
                "required": False,
                "optionsEndpoint": "/api/party-categories/?ordering=name"
            },
            "default_price_type": {
                "type": "select",
                "label": "Default Price Type",
                "required": False,
                "optionsEndpoint": "/api/pricetypes/?ordering=name"
            },
            "customer_rank": {
                "type": "boolean",
                "label": "Is Customer",
                "required": False
            },
            "supplier_rank": {
                "type": "boolean",
                "label": "Is Supplier",
                "required": False
            },
            "is_active": {
                "type": "boolean",
                "label": "Active",
                "required": False
            }
        }
        return Response(schema)


class JobSchemaView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        schema = {
            "name": {
                "type": "string",
                "label": "Job Name",
                "required": True
            },
            "builder": {
                "type": "select",
                "label": "Party",
                "required": True,
                "optionsEndpoint": "/api/builder/"
            },
            "address": {
                "type": "string",
                "label": "Address",
                "required": False
            },
            "latitude": {
                "type": "string",
                "label": "Latitude",
                "required": False
            },
            "longitude": {
                "type": "string",
                "label": "Longitude",
                "required": False
            }
        }
        return Response(schema)


class HouseModelSchemaView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        schema = {
            "name": {
                "type": "string",
                "label": "House Model Name",
                "required": True
            },
            "jobs": {
                "type": "select",
                "label": "Jobs",
                "required": False,
                "optionsEndpoint": "/api/job/",
                "multiple": True
            }
        }
        return Response(schema)
