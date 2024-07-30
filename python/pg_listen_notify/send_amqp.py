import pika
import os

credentials=pika.PlainCredentials(os.getenv('USERNAME'),os.getenv('PASSWORD'))
#credentials=pika.PlainCredentials('pai','dunder3000')
connection=pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))
channel=connection.channel() 
channel.queue_declare(queue='hello')
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()
