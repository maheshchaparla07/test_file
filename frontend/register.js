document.getElementById("registerForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const username = document.getElementById("username").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const confirm = document.getElementById("confirmPassword").value;

  // Clear errors
  document.querySelectorAll("small").forEach(s => s.innerText = "");

  // Validations


  if (username.length < 1) {
    document.getElementById("userError").innerText = "Username min 1 char";
    return;
  }
  if (!email.includes("@")) {
    document.getElementById("emailError").innerText = "Invalid email";
    return;
  }
  if (password.length < 1) {
    document.getElementById("passError").innerText = "Password min 1 char";
    return;
  }
  if (password !== confirm) {
    document.getElementById("confirmError").innerText = "Passwords do not match";
    return;
  }

  try {
    const res = await axios.post("http://127.0.0.1:8000/create-user", {
      username,
      email,
      password
    });

    document.getElementById("responseBox").innerText =
      JSON.stringify(res.data, null, 2);

    

    localStorage.setItem("token", res.data.access_token);
    localStorage.getItem("access_token")


    console.log("Registration token:", res.data.access_token);

    alert(`my registration token is ${res.data.access_token}`);


    window.location.href = "index.html";
  } catch (err) {
      console.log("error", err);
    
    document.getElementById("responseBox").innerText =
      err.response?.data?.detail || "Registration failed";
  }
});

function goToLogin() {
  window.location.href = "index.html";
}
