from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('job/new/', views.JobCreateView.as_view(), name='job_create'),
    path('job/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('job/<int:pk>/delete/', views.JobDeleteView.as_view(), name='job_delete'),
    path('job/<int:job_id>/upload/', views.upload_candidates, name='upload_candidates'),
    path('job/<int:job_id>/export/', views.export_job_report, name='job_export'),
    path('job/<int:pk>/toggle_status/', views.toggle_job_status, name='job_toggle_status'),
]
