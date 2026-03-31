const socket = io();

function encrypt(message){
    return btoa(message);
}

function decrypt(message){
    return atob(message);
}

function sendMessage(){

    const input = document.getElementById("msg");
    if(!input.value) return;

    socket.send(encrypt(input.value));

    input.value="";
}

socket.on("message", function(data){

    const chat = document.getElementById("chat");

    const div = document.createElement("div");
    div.className="message";

    div.innerHTML =
        decrypt(data.msg) +
        `<small> (${data.time})</small>`;

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
});