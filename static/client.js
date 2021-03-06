$(function () {
  var ws_scheme = "";
  if(window.location.protocol == "https:"){
    ws_scheme = "wss://";
  }else{
    ws_scheme = "ws://";
  }
  var ws = new WebSocket(ws_scheme+location.host);
  $('form').submit(function(){
    var $this = $(this);
    
    // ws.send("bot ping");
    ws.send($('#m').val());
    $('#m').val('');
    return false;
  });
  
  // ws.onopen = function() {
  //   console.log('sent message: %s', $('#m').val());
  // };
  
  ws.onmessage = function(msg){
    var returnObject = JSON.parse(msg.data);
    console.log(msg.data);
    $('#messages').append($('<li>')).append($('<span id="clientId">').text(returnObject.id)).append($('<span id="clientMessage">').text(returnObject.data));
  };
  ws.onerror = function(err){
    console.log("err", err);
  };
  ws.onclose = function close() {
    console.log('disconnected');
  };
});