import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from ocpp.v16 import ChargePoint as cp, call_result, call
from ocpp.routing import on
from datetime import datetime

class ChargePoint(cp):
    def __init__(self, id, connection):
        super().__init__(id, connection)
        self.id = id
        self.status = "Available"

    @on("BootNotification")
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=300,
            status="Accepted"
        )

    @on("Heartbeat")
    async def on_heartbeat(self):
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().isoformat()
        )

    @on("StartTransaction")
    async def on_start_transaction(self, connector_id, id_tag, meter_start, **kwargs):
        return call_result.StartTransactionPayload(
            transaction_id=1,
            id_tag_info={"status": "Accepted"}
        )

    @on("StopTransaction")
    async def on_stop_transaction(self, meter_stop, timestamp, transaction_id, **kwargs):
        return call_result.StopTransactionPayload(
            id_tag_info={"status": "Accepted"}
        )

class OCPPConsumer(AsyncWebsocketConsumer):
    active_chargers = {}

    async def connect(self):
        self.charge_point_id = self.scope['url_route']['kwargs']['charge_point_id']
        await self.accept()
        
        # Create ChargePoint instance
        charge_point = ChargePoint(self.charge_point_id, self)
        self.active_chargers[self.charge_point_id] = charge_point
        
        # Start the ChargePoint handler
        await charge_point.start()

    async def disconnect(self, close_code):
        if self.charge_point_id in self.active_chargers:
            del self.active_chargers[self.charge_point_id]

    async def receive(self, text_data):
        try:
            charge_point = self.active_chargers[self.charge_point_id]
            await charge_point.receive_message(text_data)
        except Exception as e:
            print(f"Error handling message: {e}")
