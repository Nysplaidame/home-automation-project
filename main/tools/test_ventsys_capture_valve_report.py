import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from ventsys_capture_valve_report import capture

class FakeClient:
    identity = "aa:bb:cc:dd:ee:ff"
    def __init__(self,*args,**kwargs): self.disconnected=False
    async def connect(self,login): pass
    async def disconnect(self): self.disconnected=True
    async def device_info(self): return SimpleNamespace(mac_address=self.identity,compilation_time="build")
    async def list_entities_services(self):
        return ([SimpleNamespace(key=i,name=n) for i,n in enumerate(["Valve Position","Valve Open Position","Valve Closed Position","PWM Commanded Active","Uptime"])],[])
    def subscribe_states(self,callback):
        for key,value in enumerate([60,60,30,False,100]): callback(SimpleNamespace(key=key,state=value))

class CaptureTests(unittest.TestCase):
    @patch("ventsys_capture_valve_report.APIClient",FakeClient)
    def test_valid_capture_and_identity_guard(self):
        result=asyncio.run(capture("localhost",6053,FakeClient.identity,"key",True,0))
        self.assertEqual(result["position"],60)
        with self.assertRaises(ValueError): asyncio.run(capture("localhost",6053,"00:00:00:00:00:00","key",True,0))
        with self.assertRaises(ValueError): asyncio.run(capture("localhost",6053,FakeClient.identity,"key",False,0))

if __name__ == "__main__": unittest.main()
