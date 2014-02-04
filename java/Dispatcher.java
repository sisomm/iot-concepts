import org.eclipse.paho.client.mqttv3.*;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import gnu.io.CommPortIdentifier;
import gnu.io.SerialPort;
import gnu.io.SerialPortEvent;
import java.io.IOException;
import gnu.io.SerialPortEventListener;
import java.util.Enumeration;
import java.util.concurrent.*;

public class Dispatcher implements MqttCallback
{
 public BufferedReader input;
 public OutputStream output;
 public MqttClient client;
 public SerialClass obj;

 BlockingQueue commandQueue = new ArrayBlockingQueue(1024);
 BlockingQueue responseQueue= new ArrayBlockingQueue(1024);

  private class serialSender implements Runnable {
        @Override
        public void run() {
            try {
                while(!Thread.currentThread().isInterrupted()) {
                    // will block until there is work to do.
                    String command = (String) commandQueue.take();
                    obj.writeData(command);
                    String response = (String) responseQueue.take();
                    System.out.println("Response: "+response);
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

 public synchronized void writeData(String data) {
    System.out.println("Sent: " + data);
    try {
        output.write(data.getBytes());
    } catch (Exception e) {
       System.out.println("could not write to port");
    }
 }

  public void PahoMqttSubscribe() {}

  public void messageArrived(String topic, MqttMessage message) throws Exception
  {
    String payload=new String (message.getPayload());
    System.out.println (topic + " " + new String (message.getPayload()));
    commandQueue.put(payload);
  }

  public void connectionLost (Throwable cause) {}
  public void deliveryComplete(IMqttDeliveryToken token) {}

  public static void main (String[] args) {
   new Dispatcher().doWork();
  }

  public void doWork() {
    try {
      obj = new SerialClass();
      obj.initialize();
      obj.setQueue(responseQueue);
      input = SerialClass.input;
      output = SerialClass.output;

      Thread sender= new Thread(new serialSender());
      sender.setDaemon(true); // don't hold the VM open for this thread
      sender.start();

      client = new MqttClient("tcp://192.168.1.36:1883", MqttClient.generateClientId());
      client.connect();
      client.setCallback(this);

      client.subscribe("/arduino/1/incoming");

      // We'll now idle here sleeping, but your app can be busy
      // working here instead
      while (true) {
      try { Thread.sleep (1000); } catch (InterruptedException e) {}
      }
    }
    catch (MqttException e) { e.printStackTrace (); }
  }
}
