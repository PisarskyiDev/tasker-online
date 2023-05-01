from django.urls import path

from catalog.views import (
    index,
    WorkersListView,

)

urlpatterns = [
    path("", index, name="index"),
    path("workers/", WorkersListView.as_view(), name="worker")
]

app_name = 'catalog'
