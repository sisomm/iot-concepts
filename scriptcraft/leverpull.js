var mqtt = require('sc-mqtt');  

var client = mqtt.client('tcp://192.168.1.31:1883'); // local host is default. Otherwise use host, user/pwd
//var client = mqtt.client(); 
client.connect();

var lastSeen=new Date(); // to remember the last seen time so that we only move the skull every second
var isPresent = false;	 // is the player close to the skull?

var players=server.onlinePlayers;
var lastLoc=  new org.bukkit.Location(players[0].world, 0, 0, 0); // TODO find out how to get an empty locaiton
																  // Now we must have one player online
var nearby=false;												  // is in front of skull


//Subscribe to changes in the state of the Arduino
client.subscribe('/arduino/1/status');

//Subscribe to skull position
client.subscribe('/arduino/1/skull/x/status');
client.subscribe('/arduino/1/skull/y/status');

var player; // To remember who pulled the switch

// Here we tell Minecraft to give us control after certain events
events.on('player.PlayerInteractEvent', function (listener, event) { 
	var block = event.getClickedBlock(); // Which block?
	var type = block.getType();			 // What type is it?
 	player = event.player; 				 // Note who shall be alerted

	if(type==org.bukkit.Material.LEVER) {
		var loc = block.location;	
		
		var locString=loc.x+','+loc.y+','+loc.z;
		
		var statusTopic='/minecraft/'+loc.world.name+'/lever/'+locString+'/status';

		// Is the lever up or down?
		var state=(block.data==4)?"1":"0";

		// Now publish position and state
  		client.publish(statusTopic, // which topic
  		state,					  	// the status
  		2,						  	// QoS 1 ( send at least once )
  		false); 					// broker should retain message

		// Only send commands to LED if it is one of the right blocks
		if(locString=="-249,71,210" || locString=="-251,71,210"){

			//Left or right?
			var led=(loc.x==-249)?"0":"1";

			var commandTopic='/arduino/1/incoming';
			var command='LED, '+led+', '+state;

			client.publish(commandTopic, // which topic
			command,					 // the command
			2,						  	 // QoS 1 ( send at least once )
			false); 				     // broker should retain message
		}

	}
})


//Make skull follow the player if closer than 20 blocks
events.on('player.PlayerMoveEvent', function (listener, event) { 
	var loc=event.player.location;

	// The position of the block above and between the levers	
	var fromX=-250;
	var fromY=71;
	var fromZ=211;
	
	//The max horizontal range for the servos
	var servoXMin=13;
	var servoXMax=133;
	var servoXMid=73;
	
	var now=new Date();
	
	var timeDiff=(now-lastSeen)/1000;

	if(lastLoc.x==0){
		console.info('no last location');
		lastLoc=loc;
		return;
	}
	
	if(timeDiff<1) {
		return;
	}

	var dX=loc.x-fromX;
	var dY=loc.y-fromY;
	var dZ=loc.z-fromZ;
	var distance=Math.sqrt(dY*dY+dX*dX+dZ*dZ);
	if (distance>10){
		if(nearby){
			client.publish('/arduino/3/incoming','LEDS_OFF',2,false);
			client.publish('/raspberry/1/incoming','GOODBYE',2,false);
		}	
		nearby=false;
		return;
	} else {
		if (!nearby){
			client.publish('/arduino/3/incoming','LEDS_ON',2,false);
			client.publish('/raspberry/1/incoming','HELLO',2,false);
			nearby=true
		}
	}

	var movedX=lastLoc.x-loc.x;
	var movedY=lastLoc.y-loc.y;
	var movedZ=lastLoc.z-loc.z;
	var moved=Math.sqrt(movedX*movedX+movedY*movedY+movedZ*movedZ);

	if(moved<0.5) {
		return;
	}
		
	var horHyp=Math.sqrt(dX*dX+dZ*dZ);
	var verHyp=Math.sqrt(dY*dY+dZ*dZ);
	
	sinX=dX/horHyp;
	
	var servoXPos=Math.floor(servoXMid-sinX*60);

	//event.player.sendMessage('Mov: '+moved+', Tf: '+timeDiff+', sinX: '+sinX+', Servo: '+servoXPos);

	lastSeen=now;
	lastLoc=loc;
	
	var command='SERVO, 1, '+servoXPos;
	
	client.publish('/arduino/3/incoming',command,2,false);
	
})


//Handle messages
client.onMessageArrived(function(topic, message){
	var bytes = message.payload;	
	var javaString = new java.lang.String(bytes);	// Using the Java libraries, we can convert from binary
	
	
	players[0].sendMessage('Message: '+javaString);	

});

