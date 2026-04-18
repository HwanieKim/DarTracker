#hadle http request and response 

from .models import Corporation
from .serializer import CorporationSerializer

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class CorporationListAPI(APIView):
    def get(self, request, format = None):
        corporations = Corporation.objects.all()
        serializer = CorporationSerializer(corporations, many = True)
        return Response(serializer.data)
    
    
class CorporationDetailAPI(APIView):
    def get_corp(self, pk):
        try:
            return Corporation.objects.get(pk = pk)
        except Corporation.DoesNotExist:
            raise Http404

    
    def get(self, request, pk, format = None):
        corporation = self.get_corp(pk)
        serializer = CorporationSerializer(corporation)
        return Response(serializer.data)
    
   

    

   


