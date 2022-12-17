from django.urls import path
from . import views
urlpatterns=[
    path("facebook/login/", views.FacebookLogin.as_view(), name="facebook-login"),
    path("google/login/", views.GoogleLogin.as_view(), name="guthub-login")
]