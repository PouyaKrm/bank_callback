from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PaymentCallbackSerializer
from .services import process_order


class PaymentCallbackView(APIView):
    def get(self, request):
        serializer = PaymentCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = process_order(
            paymentID=serializer.validated_data['paymentID'],
            amount=serializer.validated_data['amount'],
            status=serializer.validated_data['status'],
            gatewayRefrenceID=serializer.validated_data['gatewayRefrenceID'],
        )

        return Response(result)
