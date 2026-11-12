// --- STATE MANAGEMENT & DOM SELECTIONS ---
let currentUser = null;

// DOM Selections
const loginSection = document.getElementById("login-section");
const loginForm = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");

// Student View Selections
const studentDashboard = document.getElementById("student-dashboard");
const studentAvatar = document.getElementById("student-avatar");
const studentNavName = document.getElementById("student-nav-name");
const studentWelcomeName = document.getElementById("student-welcome-name");
const studentHeroDate = document.getElementById("student-hero-date");
const studentStatBuses = document.getElementById("student-stat-buses");
const studentStatStops = document.getElementById("student-stat-stops");
const studentStatNotices = document.getElementById("student-stat-notices");
const studentRouteInfo = document.getElementById("student-route-info");
const studentBusList = document.getElementById("student-bus-list");
const studentStopList = document.getElementById("student-stop-list");
const studentNoticeList = document.getElementById("student-notice-list");
const studentLogoutBtn = document.getElementById("student-logout-btn");
const studentAlertsCard = document.getElementById("student-alerts-card");
const studentNoticesSection = document.getElementById("student-notices-section");

// Admin View Selections
const adminDashboard = document.getElementById("admin-dashboard");
const adminHeroDate = document.getElementById("admin-hero-date");
const adminStatBuses = document.getElementById("admin-stat-buses");
const adminStatStops = document.getElementById("admin-stat-stops");
const adminStatNotices = document.getElementById("admin-stat-notices");
const adminNoticeList = document.getElementById("admin-notice-list");
const adminBusList = document.getElementById("admin-bus-list");
const addNoticeForm = document.getElementById("add-notice-form");
const noticeText = document.getElementById("notice-text");
const noticeTargetRoute = document.getElementById("notice-target-route");
const addBusForm = document.getElementById("add-bus-form");
const adminLogoutBtn = document.getElementById("admin-logout-btn");

// Driver View Selections
const driverDashboard = document.getElementById("driver-dashboard");
const driverAvatar = document.getElementById("driver-avatar");
const driverNavName = document.getElementById("driver-nav-name");
const driverWelcomeName = document.getElementById("driver-welcome-name");
const driverHeroDate = document.getElementById("driver-hero-date");
const driverStatBus = document.getElementById("driver-stat-bus");
const driverStatRoute = document.getElementById("driver-stat-route");
const driverCoordinates = document.getElementById("driver-coordinates");
const updateGpsBtn = document.getElementById("update-gps-btn");
const driverLogoutBtn = document.getElementById("driver-logout-btn");

// Registration View Selections
const signinView = document.getElementById("signin-view");
const registerView = document.getElementById("register-view");
const showRegisterBtn = document.getElementById("show-register-btn");
const showLoginBtn = document.getElementById("show-login-btn");
const registerForm = document.getElementById("register-form");
const regRouteSelect = document.getElementById("reg-route");

// Role Selection View
const roleSelectionView = document.getElementById("role-selection-view");
const selectStudentBtn = document.getElementById("select-student-btn");
const selectAdminBtn = document.getElementById("select-admin-btn");
const backToRolesBtn = document.getElementById("back-to-roles-btn");
const signinTitle = document.getElementById("signin-title");
const signinSub = document.getElementById("signin-sub");
const authSwitchContainer = document.getElementById("auth-switch-container");

let currentLoginRole = 'student';

// Student Search Selections
const studentSearchInput = document.getElementById("student-search-input");
const studentSearchBtn = document.getElementById("student-search-btn");
const searchResultsContainer = document.getElementById("search-results");

// Admin Audit Log Selection
const adminAuditLogs = document.getElementById("admin-audit-logs");

// Base API URL
const API_BASE = window.location.protocol.startsWith("file") ? "http://127.0.0.1:5000" : ""; // Point to local backend if file-loaded, else use same origin

// --- HELPER: SHOW CORRECT DASHBOARD ---
function showDashboard(role) {
  loginSection.style.display = "none";
  studentDashboard.style.display = "none";
  adminDashboard.style.display = "none";
  driverDashboard.style.display = "none";

  if (role === "admin") {
    adminDashboard.style.display = "flex";
    loadAdminPortal();
  } else if (role === "student") {
    studentDashboard.style.display = "flex";
    loadStudentPortal();
  } else if (role === "driver") {
    driverDashboard.style.display = "flex";
    loadDriverPortal();
  } else {
    loginSection.style.display = "flex";
  }
}

// --- STUDENT PORTAL LOGIC ---
async function loadStudentPortal() {
  studentHeroDate.textContent = new Date().toLocaleDateString("en-IN", {
    weekday: "long", day: "numeric", month: "long", year: "numeric"
  });

  try {
    // Load routes cache for notice route name resolution
    await loadNoticeRoutes();

    const res = await fetch(`${API_BASE}/api/student/dashboard`);
    const data = await res.json();
    if (data.error) {
      alert(data.error);
      return;
    }

    const student = data.student;
    const route = data.route;
    const buses = data.buses;
    const stops = data.stops;
    const notices = data.notices;

    // Update profile info
    const initials = student.name.split(" ").map(n => n[0]).join("");
    studentAvatar.textContent = initials;
    studentNavName.textContent = student.name;
    studentWelcomeName.textContent = student.name.split(" ")[0];

    // Update stats
    studentStatBuses.textContent = buses.length;
    studentStatStops.textContent = stops.length;
    studentStatNotices.textContent = notices.length;

    // Route Name
    studentRouteInfo.textContent = `${route.route_name} (${route.start_point} to ${route.end_point})`;

    // Render Buses
    studentBusList.innerHTML = "";
    if (buses.length === 0) {
      studentBusList.innerHTML = `<li style="text-align: center; color: var(--text-muted); width: 100%;">No buses currently active on this route.</li>`;
    } else {
      buses.forEach(bus => {
        const li = document.createElement("li");
        li.style.cursor = "pointer";
        li.title = "Click to get real-time location";
        li.onclick = () => trackBus(bus.bus_id, bus.bus_number);
        const phoneBlock = bus.driver_phone
          ? `<div style="font-size:0.75rem;color:var(--text-muted);margin-top:3px;display:flex;align-items:center;gap:4px;">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
              ${bus.driver_phone}
            </div>`
          : "";
        li.innerHTML = `
          <div class="bus-number">${bus.bus_number}</div>
          <div class="bus-driver">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            ${bus.driver || "No driver assigned"}${phoneBlock}
          </div>
          <div class="bus-times">
            <strong>${bus.departure || "08:00"}</strong> <span>depart</span>
            <span class="arrow-transit">→</span>
            <strong>${bus.arrival || "08:30"}</strong> <span>arrive</span>
          </div>`;
        studentBusList.appendChild(li);
      });
    }

    // Render Stops Timeline
    studentStopList.innerHTML = "";
    if (stops.length === 0) {
      studentStopList.innerHTML = `<li style="color: var(--text-muted);">No stops defined for this route.</li>`;
    } else {
      stops.forEach((stop, index) => {
        const isTerminal = index === 0 || index === stops.length - 1;
        const label = index === 0 ? "Origin" : "Destination";
        const li = document.createElement("li");
        li.innerHTML = `
          <div class="stop-dot-wrap">
            <div class="stop-dot ${isTerminal ? 'terminal' : ''}"></div>
            ${index < stops.length - 1 ? '<div class="stop-line"></div>' : ''}
          </div>
          <div class="stop-text-wrap">
            <div class="stop-name ${isTerminal ? 'terminal' : ''}">${stop}</div>
            ${isTerminal ? `<span class="stop-badge">${label}</span>` : ''}
          </div>`;
        studentStopList.appendChild(li);
      });
    }

    // Render Notices with route badge
    studentNoticeList.innerHTML = "";
    if (notices.length === 0) {
      studentNoticeList.innerHTML = `
        <li style="background: rgba(255,255,255,0.02); border-color: var(--border-light); justify-content: center; width: 100%;">
          <p style="color: var(--text-muted); text-align: center; margin: 0;">No active bulletins or transit alerts.</p>
        </li>`;
    } else {
      notices.forEach(notice => {
        const routeName = getRouteName(notice.target_route_id);
        const routeBadge = notice.target_route_id 
          ? `<span style="display:inline-block; font-size:0.65rem; background:rgba(139,92,246,0.2); color:#a78bfa; padding:1px 6px; border-radius:12px; margin-left:6px;">🎯 ${routeName}</span>`
          : `<span style="display:inline-block; font-size:0.65rem; background:rgba(148,163,184,0.2); color:#94a3b8; padding:1px 6px; border-radius:12px; margin-left:6px;">🌐 All Routes</span>`;
        const li = document.createElement("li");
        li.innerHTML = `
          <div class="notice-icon">⚠️</div>
          <p>${notice.text} ${routeBadge}</p>`;
        studentNoticeList.appendChild(li);
      });
    }

  } catch (err) {
    console.error("Error loading student dashboard:", err);
  }
}

// --- BUS TRACKING INTERACTION FOR STUDENT ---
async function trackBus(busId, busNumber) {
  try {
    const res = await fetch(`${API_BASE}/api/track/${busId}`);
    const data = await res.json();
    if (data.error) {
      alert(`Tracking error: ${data.error}`);
    } else {
      alert(`🚌 GPS TRACKING [${busNumber}]\nLatitude: ${data.latitude}\nLongitude: ${data.longitude}\nStatus: Simulating active connection.`);
    }
  } catch (err) {
    console.error(err);
  }
}

// --- DRIVER PORTAL LOGIC ---
let activeBusId = null;
let currentLat = 22.719600;
let currentLng = 75.857700;

async function loadDriverPortal() {
  driverHeroDate.textContent = new Date().toLocaleDateString("en-IN", {
    weekday: "long", day: "numeric", month: "long", year: "numeric"
  });

  try {
    const res = await fetch(`${API_BASE}/api/driver/dashboard`);
    const data = await res.json();
    if (data.error) {
      alert(data.error);
      return;
    }

    const driver = data.driver;
    const bus = data.bus;
    const route = data.route;

    // Set header
    driverNavName.textContent = driver.name;
    driverWelcomeName.textContent = driver.name.split(" ")[0];

    if (bus) {
      activeBusId = bus.bus_id;
      currentLat = parseFloat(bus.latitude) || 22.719600;
      currentLng = parseFloat(bus.longitude) || 75.857700;
      driverStatBus.textContent = bus.bus_number;
      driverStatRoute.textContent = `${route.route_name || "Route 1"} Corridor`;
      driverCoordinates.textContent = `Latitude: ${currentLat.toFixed(6)}, Longitude: ${currentLng.toFixed(6)}`;
    } else {
      driverStatBus.textContent = "Unassigned";
      driverStatRoute.textContent = "N/A";
      driverCoordinates.textContent = "Coordinates unavailable — No bus assigned";
      updateGpsBtn.disabled = true;
    }
  } catch (err) {
    console.error(err);
  }
}

// Update GPS coordinates for simulated movement
if (updateGpsBtn) {
  updateGpsBtn.addEventListener("click", async () => {
    if (!activeBusId) return;

    // Simulate minor motion (jitter coordinates slightly)
    currentLat += (Math.random() - 0.5) * 0.0004;
    currentLng += (Math.random() - 0.5) * 0.0004;

    try {
      const res = await fetch(`${API_BASE}/api/track/${activeBusId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ latitude: currentLat, longitude: currentLng })
      });
      const data = await res.json();
      if (data.success) {
        driverCoordinates.textContent = `Latitude: ${currentLat.toFixed(6)}, Longitude: ${currentLng.toFixed(6)}`;
        // Flash live badge visually to confirm update
        const liveBadge = document.querySelector(".driver-live-badge");
        if (liveBadge) {
          liveBadge.style.background = "rgba(16, 185, 129, 0.2)";
          setTimeout(() => { liveBadge.style.background = ""; }, 500);
        }
      } else {
        alert(data.error || "Failed to update GPS.");
      }
    } catch (err) {
      console.error(err);
    }
  });
}

// Routes cache for displaying route names in notice lists
let routesCache = [];

// Load routes for the notice target dropdown and cache for display
async function loadNoticeRoutes() {
  try {
    const res = await fetch(`${API_BASE}/api/routes`);
    const routes = await res.json();
    routesCache = routes;
    
    // Populate the dropdown if it exists
    if (noticeTargetRoute) {
      noticeTargetRoute.innerHTML = '<option value="">All Routes (General Notice)</option>';
      routes.forEach(route => {
        const opt = document.createElement("option");
        opt.value = route.route_id;
        opt.textContent = `${route.route_name} (${route.start_point} → ${route.end_point})`;
        noticeTargetRoute.appendChild(opt);
      });
    }
  } catch (err) {
    console.error("Failed to load routes for notices:", err);
  }
}

// Helper to get route name from route_id
function getRouteName(routeId) {
  if (!routeId) return "All Routes";
  const route = routesCache.find(r => r.route_id === routeId);
  return route ? `${route.route_name}` : `Route #${routeId}`;
}

// --- ADMIN PORTAL LOGIC ---
async function loadAdminPortal() {
  adminHeroDate.textContent = new Date().toLocaleDateString("en-IN", {
    weekday: "long", day: "numeric", month: "long", year: "numeric"
  });

  try {
    // 0. Load routes for dropdown and cache
    await loadNoticeRoutes();

    // 1. Fetch notices
    const resNotices = await fetch(`${API_BASE}/api/notices`);
    const notices = await resNotices.json();

    // 2. Fetch buses
    const resBuses = await fetch(`${API_BASE}/api/buses`);
    const buses = await resBuses.json();

    // 3. Fetch routes for stats
    const resRoutes = await fetch(`${API_BASE}/api/routes`);
    const routes = await resRoutes.json();

    // Update Stats - show route count instead of bus count, total stops across all routes
    adminStatNotices.textContent = notices.length;
    adminStatBuses.textContent = routes.length;
    // Calculate total stops: sum of stops across all 5 routes
    const totalStops = routesCache.reduce((sum, r) => sum + (r.stop_count || 0), 0);
    adminStatStops.textContent = totalStops || 117; // fallback to known total

    // Render Notices with route info
    adminNoticeList.innerHTML = "";
    if (notices.length === 0) {
      adminNoticeList.innerHTML = `<li style="justify-content: center; color: var(--text-muted); font-size: 0.85rem;">No active broadcasts</li>`;
    } else {
      notices.forEach(notice => {
        const routeName = getRouteName(notice.target_route_id);
        const routeBadge = notice.target_route_id 
          ? `<span class="notice-route-badge" style="display:inline-block; font-size:0.7rem; background:rgba(139,92,246,0.2); color:#a78bfa; padding:2px 8px; border-radius:20px; margin-top:4px;">🎯 ${routeName}</span>`
          : `<span class="notice-route-badge" style="display:inline-block; font-size:0.7rem; background:rgba(148,163,184,0.2); color:#94a3b8; padding:2px 8px; border-radius:20px; margin-top:4px;">🌐 All Routes</span>`;
        const li = document.createElement("li");
        li.innerHTML = `
          <div class="item-content">
            ${notice.message}
            ${routeBadge}
          </div>
          <button class="delete-btn" onclick="deleteNotice(${notice.notice_id})" title="Delete Announcement">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
          </button>`;
        adminNoticeList.appendChild(li);
      });
    }

    // Render Buses
    adminBusList.innerHTML = "";
    if (buses.length === 0) {
      adminBusList.innerHTML = `<li style="justify-content: center; color: var(--text-muted); font-size: 0.85rem;">No registered vehicles</li>`;
    } else {
      buses.forEach(bus => {
        const li = document.createElement("li");
        const phoneBlock = bus.driver_phone
          ? `<div style="font-size:0.75rem;color:var(--text-muted);margin-top:3px;display:flex;align-items:center;gap:4px;">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
              ${bus.driver_phone}
            </div>`
          : "";
        li.innerHTML = `
          <div class="item-content">
            <strong>${bus.bus_number}</strong> — Driver: ${bus.driver_name || "None"}${phoneBlock} (Cap: ${bus.capacity})
          </div>
          <button class="delete-btn" onclick="deleteBus(${bus.bus_id})" title="Deregister Bus">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
          </button>`;
        adminBusList.appendChild(li);
      });
    }
  } catch (err) {
    console.error("Error loading admin portal data:", err);
  }

}

// Notice Broadcast Handler
if (addNoticeForm) {
  addNoticeForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = noticeText.value.trim();
    if (!text) return;

    // Get selected target route (empty string means all routes)
    const targetRouteId = noticeTargetRoute ? noticeTargetRoute.value : "";

    try {
      const res = await fetch(`${API_BASE}/api/notices`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: text,
          target_route_id: targetRouteId || null
        })
      });
      const data = await res.json();
      if (data.success) {
        noticeText.value = "";
        if (noticeTargetRoute) noticeTargetRoute.value = "";
        loadAdminPortal();
      } else {
        alert(data.error || "Failed to publish notice.");
      }
    } catch (err) {
      console.error(err);
    }
  });
}

// Bus Registration Handler
if (addBusForm) {
  addBusForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const num = document.getElementById("bus-number").value.trim();
    const driver = document.getElementById("bus-driver").value.trim();
    const dep = document.getElementById("bus-departure").value;
    const arr = document.getElementById("bus-arrival").value;

    if (!num || !driver) return;

    try {
      const res = await fetch(`${API_BASE}/api/buses`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bus_number: num,
          driver_name: driver,
          capacity: 52
        })
      });
      const data = await res.json();
      if (data.success) {
        addBusForm.reset();
        loadAdminPortal();
      } else {
        alert(data.error || "Failed to register bus.");
      }
    } catch (err) {
      console.error(err);
    }
  });
}

// Admin deletion actions (Window scoped for onclick events)
window.deleteNotice = async function (id) {
  if (!confirm("Are you sure you want to delete this notice?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/notices/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      loadAdminPortal();
    } else {
      alert(data.error || "Failed to delete notice.");
    }
  } catch (err) {
    console.error(err);
  }
};

window.deleteBus = async function (id) {
  if (!confirm("Are you sure you want to deregister this bus?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/buses/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      loadAdminPortal();
    } else {
      alert(data.error || "Failed to delete bus.");
    }
  } catch (err) {
    console.error(err);
  }
};

// --- AUTHENTICATION & LOGIN FORM SUBMISSION ---
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim().toLowerCase();
    const password = passwordInput.value;

    try {
      const res = await fetch(`${API_BASE}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, role: currentLoginRole })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        currentUser = data.user;
        showDashboard(currentUser.role);
      } else {
        alert(data.error || "Invalid login credentials.");
      }
    } catch (err) {
      console.error("Login request failed:", err);
      alert("Unable to connect to the transit server.");
    }
  });
}

// --- LOGOUT HANDLERS ---
async function handleLogout() {
  try {
    await fetch(`${API_BASE}/api/logout`, { method: "POST" });
    currentUser = null;
    studentDashboard.style.display = "none";
    adminDashboard.style.display = "none";
    driverDashboard.style.display = "none";
    loginForm.reset();
    // Reset to role selection view
    signinView.style.display = "none";
    registerView.style.display = "none";
    if (roleSelectionView) roleSelectionView.style.display = "block";
    // Clear search results
    if (searchResultsContainer) {
      searchResultsContainer.style.display = "none";
      searchResultsContainer.innerHTML = "";
    }
    if (studentSearchInput) studentSearchInput.value = "";
    loginSection.style.display = "flex";
    loginSection.classList.add("active-section");
  } catch (err) {
    console.error("Logout failed:", err);
  }
}

studentLogoutBtn.addEventListener("click", handleLogout);

// Scroll to notices section when clicking the stat card
if (studentAlertsCard && studentNoticesSection) {
  studentAlertsCard.addEventListener("click", () => {
    studentNoticesSection.scrollIntoView({ behavior: "smooth" });
  });
}
adminLogoutBtn.addEventListener("click", handleLogout);
driverLogoutBtn.addEventListener("click", handleLogout);

// --- SIGN IN / REGISTER TOGGLE ---
if (showRegisterBtn) {
  showRegisterBtn.addEventListener("click", (e) => {
    e.preventDefault();
    signinView.style.display = "none";
    if (roleSelectionView) roleSelectionView.style.display = "none";
    registerView.style.display = "block";

    const regTitle = document.getElementById("register-title");
    const regSub = document.getElementById("register-sub");
    const regRouteGroup = document.getElementById("reg-route-group");

    if (currentLoginRole === 'admin') {
      if (regTitle) regTitle.textContent = "Admin Registration";
      if (regSub) regSub.textContent = "Create your transit command center account";
      if (regRouteGroup) regRouteGroup.style.display = "none";
      if (regRouteSelect) regRouteSelect.removeAttribute("required");
    } else {
      if (regTitle) regTitle.textContent = "Register";
      if (regSub) regSub.textContent = "Create your student transit account";
      if (regRouteGroup) regRouteGroup.style.display = "block";
      if (regRouteSelect) regRouteSelect.setAttribute("required", "required");
      loadRoutesForDropdown();
    }
  });
}

// --- ROLE SELECTION TOGGLE ---
if (selectStudentBtn) {
  selectStudentBtn.addEventListener('click', () => {
    currentLoginRole = 'student';
    roleSelectionView.style.display = 'none';
    signinView.style.display = 'block';
    signinTitle.textContent = 'Student Sign In';
    signinSub.textContent = 'Access your customized transit center';
    authSwitchContainer.style.display = 'block';
    const switchText = document.getElementById("auth-switch-text");
    if (switchText) switchText.textContent = "New student?";
  });
}

if (selectAdminBtn) {
  selectAdminBtn.addEventListener('click', () => {
    currentLoginRole = 'admin';
    roleSelectionView.style.display = 'none';
    signinView.style.display = 'block';
    signinTitle.textContent = 'Admin Sign In';
    signinSub.textContent = 'Transit Command Center Access';
    authSwitchContainer.style.display = 'block';
    const switchText = document.getElementById("auth-switch-text");
    if (switchText) switchText.textContent = "New admin?";
  });
}

if (backToRolesBtn) {
  backToRolesBtn.addEventListener('click', (e) => {
    e.preventDefault();
    signinView.style.display = 'none';
    registerView.style.display = 'none';
    roleSelectionView.style.display = 'block';
  });
}

if (showLoginBtn) {
  showLoginBtn.addEventListener("click", (e) => {
    e.preventDefault();
    registerView.style.display = "none";
    signinView.style.display = "block";
  });
}

// --- LOAD ROUTES FOR REGISTRATION DROPDOWN ---
async function loadRoutesForDropdown() {
  try {
    const res = await fetch(`${API_BASE}/api/routes`);
    const routes = await res.json();
    regRouteSelect.innerHTML = '<option value="">-- Select a route --</option>';
    routes.forEach(route => {
      const opt = document.createElement("option");
      opt.value = route.route_id;
      opt.textContent = `${route.route_name} (${route.start_point} → ${route.end_point})`;
      regRouteSelect.appendChild(opt);
    });
  } catch (err) {
    console.error("Failed to load routes for dropdown:", err);
    regRouteSelect.innerHTML = '<option value="">Failed to load routes</option>';
  }
}

// --- REGISTRATION FORM SUBMISSION ---
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("reg-name").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    const route_id = regRouteSelect.value;
    const role = currentLoginRole;

    if (!name || !email || !password || (role === 'student' && !route_id)) {
      alert("Please fill in all fields.");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/api/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password, route_id: role === 'student' ? route_id : null, role })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        currentUser = data.user;
        showDashboard(currentUser.role);
      } else {
        alert(data.error || "Registration failed.");
      }
    } catch (err) {
      console.error("Registration request failed:", err);
      alert("Unable to connect to the server.");
    }
  });
}

// --- STUDENT SEARCH FUNCTIONALITY ---
if (studentSearchBtn) {
  studentSearchBtn.addEventListener("click", performSearch);
}
if (studentSearchInput) {
  studentSearchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") performSearch();
  });
}

async function performSearch() {
  const query = studentSearchInput.value.trim();
  if (!query) {
    searchResultsContainer.style.display = "none";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}`);
    const results = await res.json();

    searchResultsContainer.style.display = "block";

    if (results.error) {
      searchResultsContainer.innerHTML = `<div class="search-no-results">Error: ${results.error}</div>`;
      return;
    }

    if (results.length === 0) {
      searchResultsContainer.innerHTML = `<div class="search-no-results">No routes, stops, or buses found for "<strong>${query}</strong>".</div>`;
      return;
    }

    searchResultsContainer.innerHTML = results.map(item => {
      const route = item.route;
      const buses = item.buses;
      const stops = item.stops;

      const busChips = buses.length > 0
        ? buses.map(b => `
            <span class="result-bus-chip">
              🚌 ${b.bus_number}
              <span class="chip-driver">${b.driver || "No driver"}</span>
            </span>`).join("")
        : '<span style="color: var(--text-muted); font-size: 0.85rem;">No buses on this route</span>';

      const stopTags = stops.length > 0
        ? stops.map(s => `<span class="result-stop-tag">${s}</span>`).join("")
        : '<span style="color: var(--text-muted); font-size: 0.85rem;">No stops defined</span>';

      return `
        <div class="search-result-item">
          <h4>${route.route_name}</h4>
          <div class="result-route-detail">${route.start_point} → ${route.end_point}</div>
          <div class="result-buses-title">Active Buses</div>
          <div>${busChips}</div>
          <div class="result-stops-title">Route Stops</div>
          <div class="result-stops-list">${stopTags}</div>
        </div>`;
    }).join("");

  } catch (err) {
    console.error("Search failed:", err);
    searchResultsContainer.style.display = "block";
    searchResultsContainer.innerHTML = `<div class="search-no-results">Search failed. Please try again.</div>`;
  }
}

// --- ADMIN AUDIT LOGS LOADING ---
async function loadAuditLogs() {
  try {
    const res = await fetch(`${API_BASE}/api/admin/logs`);
    const logs = await res.json();

    if (logs.error || !Array.isArray(logs)) {
      adminAuditLogs.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted); padding: 20px;">Failed to load logs.</td></tr>`;
      return;
    }

    if (logs.length === 0) {
      adminAuditLogs.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted); padding: 20px;">No login history yet.</td></tr>`;
      return;
    }

    adminAuditLogs.innerHTML = logs.map(log => {
      let statusClass = "audit-status-fail";
      if (log.status === "Success") statusClass = "audit-status-success";
      else if (log.status.includes("Registered")) statusClass = "audit-status-register";

      const time = log.login_time ? new Date(log.login_time).toLocaleString("en-IN", {
        day: "numeric", month: "short", year: "numeric",
        hour: "2-digit", minute: "2-digit"
      }) : "N/A";

      return `
        <tr>
          <td>${log.email}</td>
          <td style="text-transform: capitalize;">${log.role}</td>
          <td class="${statusClass}">${log.status}</td>
          <td>${log.ip_address || "N/A"}</td>
          <td>${time}</td>
        </tr>`;
    }).join("");
  } catch (err) {
    console.error("Failed to load audit logs:", err);
  }
}

// --- APP INITIALIZATION & SESSION RESTORATION ---
async function restoreSession() {
  try {
    const res = await fetch(`${API_BASE}/api/session`);
    const data = await res.json();
    if (data.logged_in) {
      currentUser = data.user;
      showDashboard(currentUser.role);
    } else {
      showDashboard(null);
    }
  } catch (err) {
    console.error("Session restoration error:", err);
    showDashboard(null);
  }
}

// Start app
restoreSession();
