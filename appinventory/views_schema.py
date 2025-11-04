from appinventory.models import UnitOfMeasure
from rest_framework.views import APIView
from rest_framework.response import Response


class ProductCategorySchemaView(APIView):
    def get(self, request):
        schema = {
            "name": {
                "type": "string",
                "label": "Category",
                "required": False
            },
            "description": {
                "type": "textarea",
                "label": "Description",
                "required": False
            },
            "is_active": {
                "type": "boolean",
                "label": "Active",
                "required": False
            }
        }
        return Response(schema)
    
class ProductBrandSchemaView(APIView):
    def get(self, request):
        schema = {
            "name": {
                "type": "string",
                "label": "Brand Name",
                "required": True
            },
            "is_active": {
                "type": "boolean",
                "label": "Active",
                "required": False
            },
            "is_default": {
                "type": "boolean",
                "label": "Default Brand",
                "required": False
            }
        }
        return Response(schema)
    
class UnitOfMeasureSchemaView(APIView):
    def get(self, request):
        schema = {
            "name": {
                "type": "string",
                "label": "Name",
                "required": True
            },
            "code": {
                "type": "string",
                "label": "Code",
                "required": True
            },
            "category": {
                "type": "select",
                "label": "Category",
                "required": True,
                "optionsEndpoint": "/api/unitcategories/"
            },
            "reference_unit": {
                "type": "boolean",
                "label": "Reference Unit",
                "required": False
            },
            "conversion_sign": {
                "type": "select",
                "label": "Conversion Sign",
                "required": True,
                "options": [
                    {"value": choice[0], "label": choice[1]}
                    for choice in UnitOfMeasure.SIGN_CHOICES
                ]
            },
            "conversion_factor": {
                "type": "string",
                "label": "Conversion Factor",
                "required": True
            },
            "is_active": {
                "type": "boolean",
                "label": "Active",
                "required": False
            }
        }
        return Response(schema)
    
class UnitCategorySchemaView(APIView):
    def get(self, request):
        schema = {
            "name": {
                "type": "string",
                "label": "Category Name",
                "required": True
            },
            "description": {
                "type": "textarea",
                "label": "Description",
                "required": False
            },
            "is_active": {
                "type": "boolean",
                "label": "Active",
                "required": False
            }
        }
        return Response(schema)
    
class PriceTypeSchemaView(APIView):
    def get(self, request):
        schema = {
            "name": {
                "type": "string",
                "label": "Price Type",
                "required": True
            },
            "description": {
                "type": "textarea",
                "label": "Description",
                "required": False
            },
            "is_active": {
                "type": "boolean",
                "label": "Active",
                "required": False
            }
        }
        return Response(schema)