from rest_framework import generics

from .models import ZProduct
from .serializers import ZProductSerializer


class ZProductList(generics.ListCreateAPIView):
    queryset = ZProduct.objects.all()
    serializer_class = ZProductSerializer


class ZProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ZProduct.objects.all()
    serializer_class = ZProductSerializer
