from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .consumers import OCPPConsumer

# Create your views here.

class ChargerListView(APIView):
    def get(self, request):
        chargers = {
            cp_id: {
                "id": cp.id,
                "status": cp.status
            } for cp_id, cp in OCPPConsumer.active_chargers.items()
        }
        return Response(chargers)

class RemoteStartView(APIView):
    async def post(self, request, charger_id):
        if charger_id not in OCPPConsumer.active_chargers:
            return Response({"error": "Charger not found"}, status=404)
        
        charger = OCPPConsumer.active_chargers[charger_id]
        try:
            response = await charger.call(call.RemoteStartTransaction(
                connector_id=1,
                id_tag="test_user"
            ))
            return Response({"status": "Command sent", "response": response.status})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
