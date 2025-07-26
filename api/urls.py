from django.urls import path

from .views import StoreOutputView,GetOutputsView


urlpatterns = [
    path('store-output/', StoreOutputView.as_view(), name='store_output'),
    path('get-outputs/', GetOutputsView.as_view(), name='get_outputs'),
]