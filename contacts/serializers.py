from rest_framework import serializers
from .models import (
    ContactType, Group, Department, GovernamentOffice,
    PrimaryDesignation, Position, PositionContact
)

class ContactTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactType
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class GovernamentOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernamentOffice
        fields = '__all__'

class PrimaryDesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrimaryDesignation
        fields = '__all__'

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

class PositionContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionContact
        fields = '__all__'
