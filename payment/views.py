from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PaymentCallbackSerializer


class PaymentCallbackView(APIView):
    def get(self, request):
        serializer = PaymentCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
