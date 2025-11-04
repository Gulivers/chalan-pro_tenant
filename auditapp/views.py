from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserActionLog
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')  # Deshabilita CSRF para esta vista

class LogUserActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        action = request.data.get('action')
        model_name = request.data.get('model_name')
        object_id = request.data.get('object_id')
        details = request.data.get('details', '')

        UserActionLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            details=details
        )

        return Response({"message": "Action logged successfully"}, status=201)

