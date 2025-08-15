from django.urls import path, include
from .routers import router
from . import views

urlpatterns = [
    path('', include(router.urls)),
    path('org-structure/', views.org_structure_view, name='org_structure_view'),
    path('insert-designation/', views.insert_positions_with_contacts, name='insert_positions_with_contacts'),
    path('delete-all-positions/', views.delete_all_positions_and_contacts, name='delete_all_positions_and_contacts'),
    path('json-to-xlsx/', views.save_json_to_xlsx, name='save_json_to_xlsx'),
    path('backup/', views.backup_data, name='backup_data'),
    path('restore/', views.restore_data, name='restore_data')
]
