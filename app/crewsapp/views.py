from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import connection
from django.contrib.auth import get_user_model
from .models import Crew, Truck, TruckAssignment, Category
from .serializers import (
    CrewSerializer, TruckSerializer, TruckAssignmentSerializer,
    CategorySerializer
)

User = get_user_model()


# ViewSet para Truck
class TruckViewSet(viewsets.ModelViewSet):
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    permission_classes = [IsAuthenticated]


# ViewSet para Crew (listado completo para admin CRUD; schedule puede filtrar en frontend)
class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all().order_by('id')
    serializer_class = CrewSerializer
    permission_classes = [IsAuthenticated]


# ViewSet para TruckAssignment
class TruckAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TruckAssignment.objects.all().order_by('-assigned_at')
    serializer_class = TruckAssignmentSerializer
    permission_classes = [IsAuthenticated]


# ViewSet para Category (CRUD)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.values('id', 'name')
        return Response(categories)


class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.filter(is_active=True).order_by('username').values('id', 'username')
        return Response(list(users))


class SupervisorCommunitiesView(APIView):
    def get(self, request):
        query = """
        SELECT
            au.username AS supervisor,
            j.name AS community_job
        FROM crewsapp_crew_members crm
        JOIN auth_user au ON crm.user_id = au.id
        JOIN crewsapp_crew_jobs crj ON crm.crew_id = crj.crew_id
        JOIN ctrctsapp_job j ON crj.job_id = j.id
        GROUP BY au.username, j.name
        ORDER BY au.username, j.name;
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        result = {}
        for supervisor, community in rows:
            result.setdefault(supervisor, []).append(community)

        return Response(result)
    
class CrewPermissionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        crew = Crew.objects.filter(members=user).first()

        is_coordinator = crew is None
        can_create_event = crew.permission_create_event if crew else False

        return Response({
            "username": user.username,
            "crew": {
                "id": crew.id,
                "name": crew.name,
                "category": {
                    "id": crew.category.id,
                    "name": crew.category.name
                } if crew.category else None,
                "permission_create_event": crew.permission_create_event,
                "members": list(crew.members.values_list('id', flat=True))
            } if crew else None,
            "can_create_event": can_create_event,
            "is_coordinator": is_coordinator
        })
