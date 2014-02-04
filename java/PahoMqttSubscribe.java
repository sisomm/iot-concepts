import org.eclipse.paho.client.mqttv3.*;
// From http://www.eclipse.org/paho/talkingsmall/talking_small.html
public class PahoMqttSubscribe implements MqttCallback
{

  MqttClient client;

  public PahoMqttSubscribe() {}

  public void messageArrived(String topic, MqttMessage message) throws Exception
  {
    System.out.println (topic + " " + new String (message.getPayload()));
  }

  public void connectionLost (Throwable cause) {}
  public void deliveryComplete(IMqttDeliveryToken token) {}

  public static void main (String[] args) {
    new PahoMqttSubscribe().doDemo();
  }

  public void doDemo() {
    try {
      client = new MqttClient("tcp://192.168.1.36:1883", MqttClient.generateClientId());
      client.connect();
      client.setCallback(this);

      client.subscribe("/#");

      // We'll now idle here sleeping, but your app can be busy
      // working here instead
      while (true) {
      try { Thread.sleep (1000); } catch (InterruptedException e) {}
      }
    }
    catch (MqttException e) { e.printStackTrace (); }
  }
}
