from django.urls import path, include
from .routers import router
from . import views

urlpatterns = [
    path('', include(router.urls)),
    path('org-structure/', views.org_structure_view, name='org_structure_view'), 
]
