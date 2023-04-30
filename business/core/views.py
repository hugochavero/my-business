from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['get'], url_path='values-by-qty')
    def get_values_by_qty(self, request, pk):
        qty = int(request.query_params['qty'])

        amount = Product.get_total_price(qty, pk)
        cost = Product.get_total_cost(qty, pk)
        profit = amount - cost

        values = {
            "amount": amount,
            "cost": cost,
            "profit": profit
        }
        return Response(values)
