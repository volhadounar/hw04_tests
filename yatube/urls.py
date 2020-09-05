from django.contrib import admin
from django.urls import include, path
from django.contrib.flatpages import views

urlpatterns = [
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path("", include("posts.urls")),
]

urlpatterns += [
        path('about-me/', views.flatpage, {'url': '/about-author/'}, name='about'),
        path('terms/', views.flatpage, {'url': '/about-spec/'}, name='terms'),
        path('rasskaz-o-tom-kakie-my-horoshie/', views.flatpage, {'url': '/about-author/'}, name='about'),
]