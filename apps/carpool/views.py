from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
# Create your views here.


def auth(request):
    if request.method == 'GET':
        return JsonResponse({'status': 'success', 'message': 'GET'})
    elif request.method == 'POST':
        return JsonResponse({'status': 'success', 'message': 'POST'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Unsupported method'})


class UserView(APIView):
    def get(self, request):
        return Response({'status': 'success', 'message': 'GET'})

    def post(self, request):
        print(request.data)
        return Response({'status': 'success', 'message': 'POST'})