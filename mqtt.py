import json
import ssl
import time
import paho.mqtt.client as mqtt

BROKER = "1c3070463886424684be8c4f3c5941fe.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "mateus"
PASSWORD = "MateusTest123"
TOPIC = "prothesis/logs/raw"

payload_data = [
    {"cJ": -4481.79, "cJl": -500, "cJp": 0.42, "cP": 0, "cPl": 0, "cPp": 0.5, "pJ": 0, "pP": 0},
    {"cJ": -4481.79, "cJl": -500, "cJp": 0.42, "cP": 0, "cPl": 0, "cPp": 0.5, "pJ": 0, "pP": 0},
    {"cJ": -4481.79, "cJl": -500, "cJp": 0.42, "cP": 0, "cPl": 0, "cPp": 0.5, "pJ": 0, "pP": 0},
    {"cJ": -4481.79, "cJl": -500, "cJp": 0.42, "cP": 0, "cPl": 0, "cPp": 0.5, "pJ": 0, "pP": 0},
    {"cJ": -4481.79, "cJl": -500, "cJp": 0.42, "cP": 0, "cPl": 0, "cPp": 0.5, "pJ": 0, "pP": 0},
    {"cJ": -4481.79, "cJl": -500, "cJp": 0.42, "cP": 0, "cPl": 0, "cPp": 0.5, "pJ": 0, "pP": 0},
    {"cJ": -4481.79, "cJl": -500, "cJp": 0.42, "cP": 0, "cPl": 0, "cPp": 0.5, "pJ": 0, "pP": 0},
    {"cJ": -4481.79, "cJl": -500, "cJp": 0.42, "cP": 0, "cPl": 0, "cPp": 0.5, "pJ": 0, "pP": 0},
    {"cJ": -4481.79, "cJl": -500, "cJp": 0.42, "cP": 0, "cPl": 0, "cPp": 0.5, "pJ": 0, "pP": 0},
    {"cJ": -4481.79, "cJl": -500, "cJp": 0.42, "cP": 0, "cPl": 0, "cPp": 0.5, "pJ": 0, "pP": 0}
]

json_payload = json.dumps(payload_data)

connected = False

def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        print("✅ Successfully connected to HiveMQ Cloud!")
        connected = True
    else:
        print(f"❌ Connection failed with reason code: {rc}")

def on_publish(client, userdata, mid, reason_code=None, properties=None):
    print(f"📥 Broker acknowledged receipt (Message ID: {mid})")

def on_disconnect(client, userdata, flags, rc, properties=None):
    global connected
    print(f"⚠️ Disconnected from broker. Reason: {rc}")
    connected = False

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

client.on_connect = on_connect
client.on_publish = on_publish
client.on_disconnect = on_disconnect

client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

client.username_pw_set(USERNAME, PASSWORD)

print("Connecting to broker...")
client.connect(BROKER, PORT, keepalive=60)

client.loop_start()

try:
    print("🚀 Starting periodic publishing loop... (Press Ctrl+C to stop)")
    while True:
        if connected:
            result = client.publish(TOPIC, json_payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"📤 Payload cleanly sent to topic: {TOPIC} (Local ID: {result.mid})")
            else:
                print(f"❌ Failed to publish packet locally, internal error: {result.rc}")
        else:
            print("⏳ Waiting for connection to establish...")
        
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Stopping loop gracefully...")

finally:
    client.loop_stop()
    client.disconnect()
    print("👋 Cleaned up and exited.")