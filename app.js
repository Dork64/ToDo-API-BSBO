const AUTH_BASE = "http://127.0.0.1:8000/api/v3/auth";
const TASK_BASE = "http://127.0.0.1:8000/api/v3/tasks";

let token = "";
let who = "";

let editingTask = null;

const $ = (id) => document.getElementById(id);

function show(el, on, display = "block") {
  el.style.display = on ? display : "none";
}

function setErr(el, msg) {
  el.textContent = msg || "";
  el.style.display = msg ? "block" : "none";
}

function humanErr(err) {
  if (!err) return "Неизвестная ошибка.";
  if (typeof err === "string") return err;
  if (Array.isArray(err.detail)) {
    return err.detail.map((e) =>
      String(e.msg || e)
        .replace("String should have at least 3 characters", "Поле должно быть не менее 3 символов")
        .replace("String should have at least 6 characters", "Пароль минимум 6 символов")
        .replace("value is not a valid email address", "Неверный формат email")
    ).join("\n");
  }
  if (typeof err.detail === "string") return err.detail;
  return JSON.stringify(err);
}

async function api(url, opts = {}) {
  const res = await fetch(url, opts);
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch {}
  if (!res.ok) throw (data || { detail: `HTTP ${res.status}` });
  return data;
}

function authHeaders() { return { Authorization: "Bearer " + token }; }

function formatDate(dt) {
  if (!dt) return "нет";
  const d = new Date(dt);
  if (isNaN(d.getTime())) return "нет";
  const pad = (n) => String(n).padStart(2, "0");
  return `${pad(d.getDate())}.${pad(d.getMonth()+1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

// чтобы подставлять дедлайн в input type=datetime-local
function toDatetimeLocal(value) {
  if (!value) return "";
  const d = new Date(value);
  if (isNaN(d.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/* Views */
function openRegister() {
  show($("registerView"), true);
  show($("loginView"), false);
  show($("mainView"), false);
  setErr($("regErr"), "");
  setErr($("loginErr"), "");
}
function openLogin() {
  show($("registerView"), false);
  show($("loginView"), true);
  show($("mainView"), false);
  setErr($("regErr"), "");
  setErr($("loginErr"), "");
}
function openMain(email) {
  show($("registerView"), false);
  show($("loginView"), false);
  show($("mainView"), true);
  who = email;
  $("whoName").textContent = who;
  show($("whoPill"), true);
  show($("logoutBtn"), true);
}

/* Auth buttons */
$("toLogin").onclick = openLogin;
$("toRegister").onclick = openRegister;

$("regBtn").onclick = async () => {
  setErr($("regErr"), "");
  const nickname = $("regNick").value.trim();
  const email = $("regEmail").value.trim();
  const password = $("regPass").value;

  try {
    await api(`${AUTH_BASE}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nickname, email, password })
    });
    $("loginEmail").value = email;
    openLogin();
  } catch (e) {
    setErr($("regErr"), humanErr(e));
  }
};

$("loginBtn").onclick = async () => {
  setErr($("loginErr"), "");
  const username = $("loginEmail").value.trim();
  const password = $("loginPass").value;

  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  try {
    const data = await api(`${AUTH_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData
    });
    token = data.access_token;
    openMain(username);
    await loadTasks();
  } catch (e) {
    setErr($("loginErr"), humanErr(e));
  }
};

$("logoutBtn").onclick = () => {
  token="";
  who="";
  show($("whoPill"), false);
  show($("logoutBtn"), false);
  openLogin();
};

/* Filters */
$("applyBtn").onclick = loadTasks;
$("clearBtn").onclick = () => {
  $("q").value = "";
  $("quadrant").value = "";
  $("status").value = "";
  loadTasks();
};

/* Modal create */
const overlay = $("createOverlay");

function openCreate() {
  setErr($("mErr"), "");
  $("mTitle").value = "";
  $("mDesc").value = "";
  $("mDeadline").value = "";
  $("mImportant").value = "false";

  show(overlay, true, "flex");
  $("mTitle").focus();
}

function closeCreate() {
  show(overlay, false);
}

$("openCreateBtn").onclick = openCreate;
$("closeCreateBtn").onclick = closeCreate;
$("cancelCreateBtn").onclick = closeCreate;

overlay.addEventListener("click", (e) => {
  if (e.target === overlay) closeCreate();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeCreate();
});

$("createBtn").onclick = async () => {
  setErr($("mErr"), "");
  const title = $("mTitle").value.trim();
  const description = $("mDesc").value.trim();
  const is_important = $("mImportant").value === "true";
  const deadline_at = $("mDeadline").value || null;

  if (!title) return setErr($("mErr"), "Название обязательно.");

  try {
    $("createBtn").disabled = true;

    await api(`${TASK_BASE}/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({
        title,
        description: description || null,
        is_important,
        deadline_at
      })
    });

    closeCreate();
    await loadTasks();
  } catch (e) {
    setErr($("mErr"), humanErr(e));
  } finally {
    $("createBtn").disabled = false;
  }
};

/* ===== EDIT MODAL (ДОБАВЛЕНО) ===== */
const editOverlay = $("editOverlay");

function openEdit(task) {
  editingTask = task;
  setErr($("eErr"), "");

  $("eTitle").value = task.title || "";
  $("eDesc").value = task.description || "";
  $("eDeadline").value = toDatetimeLocal(task.deadline_at);
  $("eImportant").value = task.is_important ? "true" : "false";

  show(editOverlay, true, "flex");
  $("eTitle").focus();
}

function closeEdit() {
  show(editOverlay, false);
  editingTask = null;
}

$("closeEditBtn").onclick = closeEdit;
$("cancelEditBtn").onclick = closeEdit;

editOverlay.addEventListener("click", (e) => {
  if (e.target === editOverlay) closeEdit();
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeEdit();
});

$("saveEditBtn").onclick = async () => {
  if (!editingTask) return;

  setErr($("eErr"), "");
  const title = $("eTitle").value.trim();
  const description = $("eDesc").value.trim();
  const is_important = $("eImportant").value === "true";
  const deadline_at = $("eDeadline").value || null;

  if (!title) return setErr($("eErr"), "Название обязательно.");

  try {
    $("saveEditBtn").disabled = true;

    // PUT /tasks/{id}
    await api(`${TASK_BASE}/${editingTask.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({
        title,
        description: description || null,
        is_important,
        deadline_at
      })
    });

    closeEdit();
    await loadTasks();
  } catch (e) {
    setErr($("eErr"), humanErr(e));
  } finally {
    $("saveEditBtn").disabled = false;
  }
};
/* ===== /EDIT MODAL ===== */

/* Tasks load/render */
async function loadTasks() {
  const q = $("q").value.trim();
  const quadrant = $("quadrant").value;
  const status = $("status").value;

  let url = TASK_BASE;
  if (q) url = `${TASK_BASE}/search?q=${encodeURIComponent(q)}`;
  else if (quadrant) url = `${TASK_BASE}/quadrant/${quadrant}`;
  else if (status) url = `${TASK_BASE}/status/${status}`;

  try {
    const tasks = await api(url, { headers: { ...authHeaders() } });
    const sorted = (Array.isArray(tasks) ? tasks : []).sort((a, b) => {
    // 1. Важные выше
    if (a.is_important !== b.is_important) {
        return b.is_important - a.is_important;
    }

    // 2. С дедлайном выше без дедлайна
    if (a.deadline_at && !b.deadline_at) return -1;
    if (!a.deadline_at && b.deadline_at) return 1;

    // 3. По дате дедлайна (раньше → выше)
    if (a.deadline_at && b.deadline_at) {
        return new Date(a.deadline_at) - new Date(b.deadline_at);
    }

    return 0;
    });

    renderTasks(sorted);
  } catch (e) {
    renderTasks([]);
    alert("Ошибка загрузки: " + humanErr(e));
  }
}

function renderTasks(tasks) {
  const list = $("list");
  list.innerHTML = "";

  if (!tasks.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "Ничего не найдено.";
    list.appendChild(empty);
    return;
  }

  for (const t of tasks) {
    const card = document.createElement("div");
    card.className = "card" + (t.completed ? " done" : "");

    const top = document.createElement("div");
    top.className = "titleline";

    const left = document.createElement("div");
    const name = document.createElement("p");
    name.className = "name";
    name.textContent = t.title || "(без названия)";
    left.appendChild(name);

    const chips = document.createElement("div");
    chips.className = "chips";

    const qChip = document.createElement("span");
    qChip.className = "chip";
    qChip.textContent = t.quadrant || "—";
    chips.appendChild(qChip);

    const stChip = document.createElement("span");
    stChip.className = "chip";
    stChip.textContent = t.status_message || (t.completed ? "выполнено" : "в процессе");
    chips.appendChild(stChip);

    if (t.is_important) {
      const imp = document.createElement("span");
      imp.className = "chip imp";
      imp.textContent = "важная";
      chips.appendChild(imp);
    }

    top.appendChild(left);
    top.appendChild(chips);

    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = `Дедлайн: ${formatDate(t.deadline_at)}`;

    const desc = document.createElement("div");
    desc.className = "desc";
    desc.textContent = t.description || "";

    const actions = document.createElement("div");
    actions.className = "actions";

    const doneBtn = document.createElement("button");
    doneBtn.textContent = t.completed ? "✅ выполнено" : "✔ выполнить";
    doneBtn.disabled = !!t.completed;
    doneBtn.onclick = async () => {
      await api(`${TASK_BASE}/${t.id}/complete`, {
        method: "PATCH",
        headers: { ...authHeaders() },
      });
      loadTasks();
    };

    // --- EDIT BUTTON (ДОБАВЛЕНО) ---
    const editBtn = document.createElement("button");
    editBtn.textContent = "✏ редактировать";
    editBtn.onclick = () => openEdit(t);
    // --- /EDIT BUTTON ---

    const delBtn = document.createElement("button");
    delBtn.className = "danger";
    delBtn.textContent = "🗑 удалить";
    delBtn.onclick = async () => {
      if (!confirm("Удалить задачу?")) return;
      await api(`${TASK_BASE}/${t.id}`, {
        method: "DELETE",
        headers: { ...authHeaders() },
      });
      loadTasks();
    };

    actions.appendChild(doneBtn);
    actions.appendChild(editBtn);
    actions.appendChild(delBtn);

    card.appendChild(top);
    card.appendChild(meta);
    if (t.description) card.appendChild(desc);
    card.appendChild(actions);

    list.appendChild(card);
  }
}

/* Start */
openRegister();
