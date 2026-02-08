// Cookie utility functions
function setCookie(name, value, minutes) {
  const expires = new Date(Date.now() + minutes * 60000).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Strict`;
}

function getCookie(name) {
  const value = document.cookie
    .split("; ")
    .find(row => row.startsWith(name + "="))
    ?.split("=")[1];
  return value || null;
}

function deleteCookie(name) {
  document.cookie = `${name}=; Max-Age=0; path=/`;
}

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

    // Store tokens in cookies
    setCookie("access_token", res.data.access_token, 15);   // 15 minutes
    setCookie("refresh_token", res.data.refresh_token, 10080); // 7 days

    console.log("JWT stored in cookies");

    alert("Login successful!");

    // Redirect after storing token
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
