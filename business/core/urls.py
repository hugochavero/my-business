from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, SellOperationViewSet

router = DefaultRouter()

router.register("product", ProductViewSet)
router.register("sell-operation", SellOperationViewSet)


urlpatterns = router.urls
