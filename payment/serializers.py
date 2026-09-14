from rest_framework import serializers


class PaymentCallbackSerializer(serializers.Serializer):
    paymentID = serializers.CharField(max_length=600)
    amount = serializers.IntegerField(
        min_value=-(2**63), max_value=2**63 - 1,
    )
    status = serializers.CharField()
    gatewayRefrenceID = serializers.CharField()
