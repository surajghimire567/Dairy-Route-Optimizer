from django.urls import path
from .views import ImportView

urlpatterns = [
    path("import/", ImportView.as_view(), name="import-workbook"),
]