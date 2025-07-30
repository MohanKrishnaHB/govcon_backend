from django.contrib import admin
from .models import (
    ContactType,
    Group,
    Department,
    GovernamentOffice,
    PrimaryDesignation,
    Position,
    PositionContact,
)

admin.site.register(ContactType)
admin.site.register(Group)
admin.site.register(Department)
admin.site.register(GovernamentOffice)
admin.site.register(PrimaryDesignation)
admin.site.register(Position)
admin.site.register(PositionContact)
