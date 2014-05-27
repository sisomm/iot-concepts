//Demonstrates IoT concepts using MQTT, Arduino and Python on RaspI.
//(c) Simen Sommerfeldt, @sisomm, simen.sommerfeldt@gmail.com Licensed as CC-BY-SA

var mqtt = require('sc-mqtt');  

var client = mqtt.client('tcp://192.168.1.16:1883'); // local host is default. Otherwise use host, user/pwd

client.connect();

client.publish('/minecraft/status','Reset',0,false);

var lastSeen=new Date(); // to remember the last seen time so that we don't spam the Arduino

var players=server.onlinePlayers;
var lastLoc=  new org.bukkit.Location(players[0].world, 0, 0, 0); // Empty locaiton
																  // Now we must have one player online
var nearby=false;												  // The player isin front of the skull

//Subscribe to changes in the state of the Arduino
client.subscribe('/arduino/1/status');

var player; // To remember who pulled the switch

//This event handler reports if the player breaks a block. The position is not correct.
events.on('block.BlockBreakEvent', function (event){
		var loc=event.player.location;
		var locString=loc.x+','+loc.y+','+loc.z;
		client.publish('/minecraft/world/block/'+locString+'/status','BROKEN',0,false);
});

//Make skull follow the player if closer than 10 blocks
events.on('player.PlayerMoveEvent', function (event) { 
	var loc=event.player.location;

	// The position of the skull & The origin for the face tracker 	
	var fromX=-250;
	var fromY=70.5;   // Actually 71, but we want the skull to look straight forward
	var fromZ=211;
	
	var now=new Date();
	var timeDiff=(now-lastSeen)/1000;

	// Need this to remember where he was. Should only happen once
	if(lastLoc.x==0){
		console.info('no last location');
		lastLoc=loc;
		return;
	}
	
	if(timeDiff<0.1) { // We don´t want more than 10 updates/sec
		return;
	}

	// The distance from the skull to the player
	var dX=loc.x-fromX;
	var dY=loc.y-fromY;
	var dZ=loc.z-fromZ;
	var distance=Math.sqrt(dY*dY+dX*dX+dZ*dZ);

	var sonarPos='250,72,211';	// For MQTT topic. Change to where you put your skull/sonar

	// Find out how much he moved since the last time
	var movedX=lastLoc.x-loc.x;8
	var movedY=lastLoc.y-loc.y;
	var movedZ=lastLoc.z-loc.z;
	var moved=Math.sqrt(movedX*movedX+movedY*movedY+movedZ*movedZ);

	if(moved<0.1) {	// Don't bother if the player hasn't moved
		return;
	}
	
	// The sonar only works in front of the skull and at distance shorter than 20
	// I have disabled the sonar since I currently don't use it and it floods the messaqe queue
	//if (distance<21 && loc.z<fromZ) client.publish('/minecraft/world/sonar/'+sonarPos,'Ping: '+Math.floor(distance),2,false);	

	//Find out if the skull has company 
	if (distance>13){
		if(nearby){
			client.publish('/minecraft/world/skull/'+sonarPos,'IS_ALONE',0,false);
		}	
		nearby=false;
		return;
	} else {
		if (!nearby){
			client.publish('/minecraft/world/skull/'+sonarPos,'HAS_COMPANY',0,false);			
			nearby=true
		}
	}
	
	//The magic facetracker only works in front of the skull
	if(loc.z<fromZ){
		var horHyp=Math.sqrt(dX*dX+dZ*dZ);
		var verHyp=Math.sqrt(dY*dY+dZ*dZ);
		var sinX=dX/horHyp;
		var sinY=dY/verHyp;
		client.publish('/minecraft/world/facetracker/'+sonarPos,sinX+', '+sinY,0,false);	
	}
	
	lastSeen=now;
	lastLoc=loc;

})



// Detect if a the player pulled one of the switches in front of the skull
events.on('player.PlayerInteractEvent', function (event) { 
	var block = event.getClickedBlock(); // Which block?
	var type = block.getType();			 // What type is it?
 	player = event.player; 				 // Note who shall be alerted

	if(type==org.bukkit.Material.LEVER) {
		var loc = block.location;	
		
		var locString=loc.x+','+loc.y+','+loc.z;
		
		// Is the lever up or down?
		var state=(block.data==4)?"1":"0";

		// Only publish if it is one of the right blocks. You must change to your position
		if(locString=="-249,71,210" || locString=="-251,71,210"){

			var statusTopic='/minecraft/world/lever/'+locString+'/status';
			var payload=state;

			client.publish(statusTopic,  // which topic
			payload,					 // the status
			0,						  	 // QoS 
			false); 				     // broker should retain message
		}

	}
})


//Handle messages
client.onMessageArrived(function(topic, message){
	var bytes = message.payload;	
	var javaString = new java.lang.String(bytes);	// Using the Java libraries, we can convert from binary
	players[0].sendMessage('Message: '+javaString);	

});

		
