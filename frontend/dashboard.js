const token = localStorage.getItem("authorization");

console.log("Dashboard token:", token);
// protect dashboard
if (!token) {
  window.location.href = "index.html";
}

const API_URL = "http://127.0.0.1:8000";

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
  localStorage.removeItem("token");
  window.location.href = "index.html"; 
  
}
