from rest_framework.routers import DefaultRouter
from .viewsets import (
    ContactTypeViewSet,
    GroupViewSet,
    DepartmentViewSet,
    GovernamentOfficeViewSet,
    PrimaryDesignationViewSet,
    PositionViewSet,
    PositionContactViewSet
)

router = DefaultRouter()
router.register(r'contact-types', ContactTypeViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'government-offices', GovernamentOfficeViewSet)
router.register(r'primary-designations', PrimaryDesignationViewSet)
router.register(r'positions', PositionViewSet)
router.register(r'position-contacts', PositionContactViewSet)
