function ScalePost(PostId) {
    return window.location.href=`/read/${PostId}`;
}

function DeletePost(PostId) {
    fetch(`/delete/${PostId}`, {method: ['POST']})
    .then(r => r.json())
    .then(res => {
        if (res.ok) {
            document.getElementById(`post-${PostId}`).remove();
        }
    })
}

function PostForm() {
    let shareform = document.getElementById('addContainer');
    shareform.innerHTML = 
    `<div id="postform" style='text-align: center;'>
    <input id="Tinput" class="input" type="text" placeholder="Enter title...">
    <textarea id="Cinput" class="input" placeholder="Enter text..."></textarea></br>
    <button onclick="SharePost()">Submit</button>
    <button id="shrenck">-</button>
    </div>`
    document.getElementById('shrenck').addEventListener('click', () => {
        shareform.innerHTML = `<button onclick="PostForm()">+</button>`
    }) 
}

function SharePost() {
    let Cinput = document.getElementById('Cinput').value;
    let Tinput = document.getElementById('Tinput').value;
    if (Cinput && Tinput) {
    fetch('/share', {method:['POST'], headers:{'Content-Type': 'application/json'}, body: JSON.stringify({'title': Tinput, 'txt': Cinput})})
    .then(r => r.json())
    .then(res => {
        if (res.ok) {
            return window.location.href='/admin';
        }
    })
    }
}

function SubmitUpdate(PostId) {
    let Uptitle = document.getElementById('Uptitle').value;
    let Uptxt = document.getElementById('Uptxt').value;
    if (Uptitle && Uptxt) {
    fetch('/Update', {
        method:'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({'Uptxt': Uptxt, 'Uptitle': Uptitle, 'PostId': PostId})
    })
    .then(res => res.json())
    .then(response => {
        if (response.ok) {
            return window.location.href='/admin';
        }
    })}

}

function UpdateForm(PostId) {
    return window.location.href=`/UpdateForm/${PostId}`;
}

function SubmitLoginInfo() {
    let Euser = document.getElementById('Euser').value;
    let Epassword = document.getElementById('Epassword').value;

    fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'user': Euser, 'password': Epassword })
    })
    .then(res => res.text())
    .then(data => {
        console.log("Server replied:", data); 
        if (data === '1') {
            window.location.href = '/admin';  
        } else {
            alert('Login failed');
        }
    })
    .catch(err => console.error("Fetch error:", err));
}

function DeletePopUp(PostId) {
let popup = document.getElementById(`popup`);
let openBtn = document.getElementById(`open-popup`);
let yesBtn = document.getElementById("YesBtn");
let noBtn = document.getElementById("NoBtn");
popup.style.display = "flex";


noBtn.addEventListener("click", () => {
  popup.style.display = "none";
});

yesBtn.onclick= () => {
    DeletePost(PostId)
    popup.style.display = "none";

}
}

