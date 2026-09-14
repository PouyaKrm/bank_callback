from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PaymentCallbackSerializer
from .services import handle_callback


class PaymentCallbackView(APIView):
    def get(self, request):
        serializer = PaymentCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = handle_callback(
            paymentID=serializer.validated_data['paymentID'],
            amount=serializer.validated_data['amount'],
            status=serializer.validated_data['status'],
            gatewayRefrenceID=serializer.validated_data['gatewayRefrenceID'],
        )

        return Response(result)
