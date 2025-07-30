from rest_framework import viewsets
from .models import (
    ContactType, Group, Department, GovernamentOffice,
    PrimaryDesignation, Position, PositionContact
)
from .serializers import (
    ContactTypeSerializer, GroupSerializer, DepartmentSerializer,
    GovernamentOfficeSerializer, PrimaryDesignationSerializer,
    PositionSerializer, PositionContactSerializer
)

class ContactTypeViewSet(viewsets.ModelViewSet):
    queryset = ContactType.objects.all()
    serializer_class = ContactTypeSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class GovernamentOfficeViewSet(viewsets.ModelViewSet):
    queryset = GovernamentOffice.objects.all()
    serializer_class = GovernamentOfficeSerializer

class PrimaryDesignationViewSet(viewsets.ModelViewSet):
    queryset = PrimaryDesignation.objects.all()
    serializer_class = PrimaryDesignationSerializer

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class PositionContactViewSet(viewsets.ModelViewSet):
    queryset = PositionContact.objects.all()
    serializer_class = PositionContactSerializer
