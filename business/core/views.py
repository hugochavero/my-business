import datetime

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet

from .models import Product, SellOperation
from .serializers import ProductSerializer, ExtractOperationSerializer


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=["get"], url_path="values-by-qty")
    def get_values_by_qty(self, request, pk):
        qty = int(request.query_params["qty"])

        amount = Product.get_total_price(qty, pk)
        cost = Product.get_total_cost(qty, pk)
        profit = amount - cost

        values = {"amount": amount, "cost": cost, "profit": profit}
        return Response(values)


class SellOperationViewSet(ViewSet):
    queryset = SellOperation.objects.all()

    @action(methods=["get"], detail=False, url_path="values-by-date-range")
    def get_values_by_date_range(self, request):
        serializer = ExtractOperationSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        values = SellOperation.get_values_by_date_range(
            serializer.validated_data["date_from"],
            serializer.validated_data["date_to"],
        )
        return Response(values)
