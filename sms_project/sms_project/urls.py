from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='dashboard:home', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('academics/', include('academics.urls')),
    path('attendance/', include('attendance.urls')),
    path('exams/', include('exams.urls')),
    path('fees/', include('fees.urls')),
    path('timetable/', include('timetable.urls')),

    # Advanced feature apps
    path('notifications/', include('notifications.urls')),
    path('reports/', include('reports.urls')),
    path('announcements/', include('announcements.urls')),
    path('calendar/', include('calendarapp.urls')),
    path('assignments/', include('assignments.urls')),
    path('library/', include('library.urls')),
    path('transport/', include('transport.urls')),
    path('hostel/', include('hostel.urls')),
    path('parents/', include('parents.urls')),
    path('audit-logs/', include('auditlog.urls')),

    # REST API (Module: API Integration)
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
