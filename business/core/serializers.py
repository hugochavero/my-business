from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "code",
            "title",
            "cost",
            "price",
        )


class ExtractOperationSerializer(serializers.Serializer):
    date_from = serializers.DateField(format="%d/%m/%Y")
    date_to = serializers.DateField(format="%d/%m/%Y")
