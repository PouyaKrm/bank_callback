from django.urls import path

from .views import PaymentCallbackView

app_name = 'payment'

urlpatterns = [
    path('callback/', PaymentCallbackView.as_view(), name='callback'),
]
