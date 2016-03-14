# source https://gist.github.com/claws/8794715
# This gist demonstrates a simple method to create a WebSockets proxy for a MQTT broker.
# I use this method to provide a WebSockets interface for the Mosquitto MQTT broker.
# This lets my browser based MQTT applications to access my MQTT broker.
# I consider this approach simpler than the common alternative which is to run lighttpd
# with the mod_websocket addon which can be complex to setup.
#
# Dependencies are Python, Twisted and Autobahn.
# This example sets up a WebSockets server listening on localhost:9000. Messages received from
# WebSocket clients are forwarded to the MQTT broker using the endpointforward plugin provided
# by Autobahn.
#
# This example assumes that the MQTT broker is running on the localhost:1883.
# This example assumes that the WebSocket client is running the paho or mosquitto Javascript
# library, both of which use the `mqttv3.1` binary subprotocol.

twistd -n endpointforward --endpoint "autobahn:tcp\:9000:url=ws\://localhost\:9000:subprotocol=mqttv3.1" --dest_endpoint="tcp:127.0.0.1:1883"
