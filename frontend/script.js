document.getElementById("loginForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
    const res = await axios.post(
      "http://127.0.0.1:8000/login",
      new URLSearchParams({
        username: username,
        password: password
      })
    );

    // ✅ STORE JWT HERE (this is the correct place)
    const token = res.data.access_token;
    localStorage.setItem("authorization", token);
    localStorage.setItem("refresh_token", res.data.refresh_token);

    console.log("JWT stored:", token);

    alert("Login successful!");

    // ✅ Redirect after storing token
    window.location.href = "dashboard.html";

  } catch (error) {
    console.error("Login failed:", error);

    alert(
      error.response?.data?.detail || "Invalid username or password"
    );
  }
});

function goToRegister() {
  window.location.href = "register.html";
}
