const socket=io();

const USER=prompt("Enter username");
socket.emit("join",USER);

function enc(m){return btoa(m)}
function dec(m){return atob(m)}

function typing(){
 socket.emit("typing",USER+" typing...");
}

socket.on("typing",t=>{
 document.getElementById("typing").innerText=t;
});

socket.on("online",u=>{
 document.getElementById("online").innerText=
 "Online: "+u.join(", ");
});

async function send(){

 let file=null;
 let f=document.getElementById("file");

 if(f.files.length){
   let form=new FormData();
   form.append("file",f.files[0]);
   let r=await fetch("/upload",{method:"POST",body:form});
   file=(await r.json()).file;
 }

 socket.emit("message",{
   user:USER,
   msg:enc(document.getElementById("msg").value),
   file:file
 });
}

socket.on("message",d=>{
 let div=document.createElement("div");

 let file="";
 if(d.file)
   file=`<a href="/uploads/${d.file}" target="_blank">📎</a>`;

 div.innerHTML=`<b>${d.user}</b>: ${dec(d.msg)} ✔✔ (${d.time}) ${file}`;
 document.getElementById("messages").appendChild(div);
});