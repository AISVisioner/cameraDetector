from django.urls import include, path
from rest_framework.routers import DefaultRouter

from lookup.api import views as lv

app_name = "lookup"

router = DefaultRouter()
router.register(r"lookup", lv.LookupViewSet)

urlpatterns = [
    path("", include(router.urls)),
]