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

let token = getCookie("access_token");

console.log("Dashboard token:", token);
// protect dashboard
if (!token) {
  window.location.href = "index.html";
}

const API_URL = "http://127.0.0.1:8000";

// Refresh token function
async function refreshAccessToken() {
  const refreshToken = getCookie("refresh_token");
  
  console.log("🔄 Attempting to refresh token...");
  console.log("Refresh token:", refreshToken ? "exists" : "missing");
  
  if (!refreshToken) {
    console.log("❌ No refresh token available");
    logout();
    return null;
  }

  try {
    console.log("📡 Calling /refresh endpoint...");
    const res = await axios.post(`${API_URL}/refresh`, {
      refresh_token: refreshToken
    });

    const newAccessToken = res.data.access_token;
    setCookie("access_token", newAccessToken, 15); // 15 minutes
    token = newAccessToken; // update the global token variable
    console.log("✅ Token refreshed successfully!");
    console.log("New access token:", newAccessToken.substring(0, 20) + "...");
    return newAccessToken;
  } catch (error) {
    console.error("❌ Token refresh failed:", error.response?.data || error.message);
    logout();
    return null;
  }
}

// Axios interceptor to handle 401 errors and refresh token
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // If 401 and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log("⚠️ 401 Error detected - Token expired!");
      originalRequest._retry = true;

      const newToken = await refreshAccessToken();
      
      if (newToken) {
        console.log("🔁 Retrying original request with new token...");
        // Update the authorization header with new token
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return axios(originalRequest);
      }
    }

    return Promise.reject(error);
  }
);

loadUsers();

//fetch users
function loadUsers() {
  axios.get(`${API_URL}/dashboard`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
  .then(res => {
    console.log("Dashboard data:", res.data);

    const tbody = document.querySelector("#userTable tbody");
    tbody.innerHTML = ""; // clear old rows

    res.data.forEach(user => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${user.id}</td>

        <td>
          <span id="email-text-${user.id}">${user.email}</span>
          <input id="email-input-${user.id}" value="${user.email}" style="display:none" />
        </td>

        <td>
          <span id="username-text-${user.id}">${user.username}</span>
          <input id="username-input-${user.id}" value="${user.username}" style="display:none" />
        </td>

        <td>
          <button id="edit-btn-${user.id}" onclick="editUser(${user.id})">Edit</button>
          <button id="save-btn-${user.id}" onclick="saveUser(${user.id})" style="display:none">Save</button>
        </td>
      `;

      tbody.appendChild(row);
    });
  })
  .catch(err => {
    console.error("Dashboard error:", err);
    alert("Unauthorized or session expired");
    logout();
  });
}

// enable edit mode
function editUser(userId) {
  toggleEdit(userId, true);
}

// save updated data
function saveUser(userId) {
  const email = document.getElementById(`email-input-${userId}`).value;
  const username = document.getElementById(`username-input-${userId}`).value;

  axios.put(`${API_URL}/users/${userId}`,
    { email, username },
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    }
  )
  .then(() => {
    console.log("User update successful");
    alert("User updated successfully");
    loadUsers(); // refresh from DB
  })
  .catch(err => {
    console.error("Update error:", err);
    alert("Failed to update user");
  });
}

// toggle edit mode
function toggleEdit(userId, isEdit) {
  document.getElementById(`email-text-${userId}`).style.display = isEdit ? "none" : "inline";
  document.getElementById(`username-text-${userId}`).style.display = isEdit ? "none" : "inline";

  document.getElementById(`email-input-${userId}`).style.display = isEdit ? "inline" : "none";
  document.getElementById(`username-input-${userId}`).style.display = isEdit ? "inline" : "none";

  document.getElementById(`edit-btn-${userId}`).style.display = isEdit ? "none" : "inline";
  document.getElementById(`save-btn-${userId}`).style.display = isEdit ? "inline" : "none";
}

// logout
function logout() {
  deleteCookie("access_token");
  deleteCookie("refresh_token");
  window.location.href = "index.html";
}


// Test function to manually trigger refresh token
async function testRefreshToken() {
  const output = document.getElementById("testOutput");
  output.innerHTML = "<h3>🧪 Testing Refresh Token...</h3>";
  
  console.log("=== MANUAL REFRESH TOKEN TEST ===");
  
  // Show current tokens
  const currentAccess = getCookie("access_token");
  const currentRefresh = getCookie("refresh_token");
  
  output.innerHTML += `<p><strong>Current Access Token:</strong> ${currentAccess ? currentAccess.substring(0, 30) + "..." : "None"}</p>`;
  output.innerHTML += `<p><strong>Current Refresh Token:</strong> ${currentRefresh ? currentRefresh.substring(0, 30) + "..." : "None"}</p>`;
  
  // Call refresh
  output.innerHTML += "<p>🔄 Calling refresh endpoint...</p>";
  const newToken = await refreshAccessToken();
  
  if (newToken) {
    output.innerHTML += `<p style="color: green;"><strong>✅ SUCCESS!</strong></p>`;
    output.innerHTML += `<p><strong>New Access Token:</strong> ${newToken.substring(0, 30)}...</p>`;
    output.innerHTML += "<p>Check console for detailed logs</p>";
  } else {
    output.innerHTML += `<p style="color: red;"><strong>❌ FAILED!</strong> Check console for errors</p>`;
  }
}

