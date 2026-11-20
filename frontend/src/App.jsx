import { useCallback, useEffect, useMemo, useState } from "react";
import { api, clearSession, getSavedUser, getToken, saveSession } from "./api";
import "./App.css";

const STATUSES = ["pending", "in_progress", "completed"];
const PRIORITIES = ["low", "medium", "high"];

function nice(value = "") {
  return String(value).replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase());
}
function dateOnly(value) {
  if (!value) return "—";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleDateString();
}
function errorText(e) { return e?.message || "Something went wrong"; }

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault(); setBusy(true); setError("");
    try {
      const result = await api("/auth/login", { method: "POST", body: { email, password } });
      const token = result.access_token;
      if (!token) throw new Error("Login response did not contain an access token.");
      const user = await api("/auth/me", { headers: { Authorization: `Bearer ${token}` } });
      saveSession(token, user);
      onLogin(user);
    } catch (err) { setError(errorText(err)); }
    finally { setBusy(false); }
  }

  return <main className="login-wrap">
    <section className="login-card">
      <div className="brand-mark">ET</div>
      <p className="eyebrow">WORKSPACE PORTAL</p>
      <h1>Welcome back</h1>
      <p className="muted">Sign in to manage tasks and track team progress.</p>
      <form onSubmit={submit} className="stack">
        <label>Email address<input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="name@company.com" /></label>
        <label>Password<input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength="8" placeholder="Enter your password" /></label>
        {error && <div className="alert error">{error}</div>}
        <button className="primary full" disabled={busy}>{busy ? "Signing in..." : "Sign in"}</button>
      </form>
      <p className="login-foot">Employee Task Management System</p>
    </section>
  </main>;
}

function App() {
  const [user, setUser] = useState(getSavedUser());
  const [page, setPage] = useState("dashboard");
  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [employees, setEmployees] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [overview, setOverview] = useState({});
  const [performance, setPerformance] = useState([]);
  const [weekly, setWeekly] = useState({ updates: [] });
  const [progressFor, setProgressFor] = useState(null);
  const [progressRows, setProgressRows] = useState([]);
  const [progressValue, setProgressValue] = useState(0);
  const [progressText, setProgressText] = useState("");
  const [employeeForm, setEmployeeForm] = useState(null);
  const [taskForm, setTaskForm] = useState(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const isAdmin = user?.role === "admin";

  const loadData = useCallback(async () => {
    if (!user) return;
    try {
      if (isAdmin) {
        const results = await Promise.allSettled([
          api("/employees"),
          api("/tasks/with-employees"),
          api("/reports/overview"),
          api("/reports/employee-performance"),
          api("/reports/weekly-progress?days=7"),
        ]);
        setError("");
        if (results[0].status === "fulfilled") setEmployees(Array.isArray(results[0].value) ? results[0].value : []);
        if (results[1].status === "fulfilled") setTasks(Array.isArray(results[1].value) ? results[1].value : []);
        if (results[2].status === "fulfilled") setOverview(results[2].value || {});
        if (results[3].status === "fulfilled") setPerformance(Array.isArray(results[3].value) ? results[3].value : []);
        if (results[4].status === "fulfilled") setWeekly(results[4].value || { updates: [] });
        const failed = results.find(r => r.status === "rejected");
        if (failed) setError(errorText(failed.reason));
      } else {
        const data = await api("/tasks");
        setError("");
        setTasks(Array.isArray(data) ? data : []);
      }
    } catch (e) { setError(errorText(e)); }
    finally { setLoading(false); }
  }, [user, isAdmin]);

  useEffect(() => {
    const timer = setTimeout(() => {
      void loadData();
    }, 0);

    return () => clearTimeout(timer);
  }, [loadData]);

  async function refresh() { setLoading(true); await loadData(); }
  function logout() { clearSession(); setUser(null); setPage("dashboard"); }

  async function openProgress(task) {
    setProgressFor(task); setProgressText(""); setProgressValue(0); setProgressRows([]);
    try { const rows = await api(`/tasks/${task.task_id ?? task.id}/progress`); setProgressRows(Array.isArray(rows) ? rows : []); }
    catch (e) { setError(errorText(e)); }
  }

  async function submitProgress(e) {
    e.preventDefault();
    try {
      await api(`/tasks/${progressFor.task_id ?? progressFor.id}/progress`, {
        method: "POST",
        body: { progress_percentage: Number(progressValue), update_text: progressText }
      });
      setNotice("Progress update submitted."); setProgressText("");
      await refresh(); await openProgress(progressFor);
    } catch (e) { setError(errorText(e)); }
  }

  async function saveEmployee(e) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const body = Object.fromEntries(form.entries());
    if (!body.department) body.department = null;
    try {
      if (employeeForm?.id) {
        delete body.password;
        await api(`/employees/${employeeForm.id}`, { method: "PUT", body });
        setNotice("Employee updated.");
      } else {
        body.role = body.role || "employee";
        await api("/employees", { method: "POST", body });
        setNotice("Employee created.");
      }
      setEmployeeForm(null); await refresh();
    } catch (e) { setError(errorText(e)); }
  }

  async function deactivateEmployee(employee) {
    if (!confirm(`Deactivate ${employee.name}?`)) return;
    try { await api(`/employees/${employee.id}`, { method: "DELETE" }); setNotice("Employee deactivated."); await refresh(); }
    catch (e) { setError(errorText(e)); }
  }

  async function saveTask(e) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const body = Object.fromEntries(form.entries());
    body.assigned_to = Number(body.assigned_to);
    body.due_date = body.due_date ? new Date(body.due_date).toISOString() : null;
    if (!body.description) body.description = null;
    try {
      if (taskForm?.id) {
        await api(`/tasks/${taskForm.id}`, { method: "PUT", body });
        setNotice("Task updated.");
      } else {
        await api("/tasks", { method: "POST", body });
        setNotice("Task created.");
      }
      setTaskForm(null); await refresh();
    } catch (e) { setError(errorText(e)); }
  }

  async function changeStatus(taskId, status) {
    try { await api(`/tasks/${taskId}/status?status=${encodeURIComponent(status)}`, { method: "PUT" }); setNotice("Task status updated."); await refresh(); }
    catch (e) { setError(errorText(e)); }
  }

  async function deleteTask(task) {
    if (!confirm(`Delete "${task.title}" and its progress history?`)) return;
    try { await api(`/tasks/${task.task_id ?? task.id}`, { method: "DELETE" }); setNotice("Task deleted."); await refresh(); }
    catch (e) { setError(errorText(e)); }
  }

  const filteredTasks = useMemo(() => tasks.filter(t => {
    const q = search.toLowerCase();
    const matches = `${t.title || ""} ${t.employee_name || ""} ${t.description || ""}`.toLowerCase().includes(q);
    return matches && (statusFilter === "all" || t.status === statusFilter);
  }), [tasks, search, statusFilter]);

  if (!getToken() || !user) return <Login onLogin={setUser} />;

  const nav = isAdmin
    ? [["dashboard","Overview"],["tasks","Tasks"],["employees","Employees"],["reports","Reports"]]
    : [["dashboard","My tasks"]];

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="sidebar-brand"><span className="brand-mark small">ET</span><div><strong>TaskFlow</strong><small>WORKSPACE</small></div></div>
      <div className="nav-label">MENU</div>
      {nav.map(([key,label]) => <button key={key} className={`nav-item ${page===key?"active":""}`} onClick={() => {setPage(key);setNotice("");setError("");}}>
        <span className="nav-dot" />{label}
      </button>)}
      <div className="sidebar-bottom">
        <div className="profile-mini"><div className="avatar">{user.name?.slice(0,1) || "U"}</div><div><strong>{user.name}</strong><small>{nice(user.role)}</small></div></div>
        <button className="logout" onClick={logout}>↪ Sign out</button>
      </div>
    </aside>

    <main className="main-area">
      <header className="topbar">
        <div><p className="eyebrow">EMPLOYEE TASK MANAGEMENT</p><h1>{page==="dashboard" ? (isAdmin?"Overview":"My tasks") : nice(page)}</h1></div>
        <div className="top-actions"><span className="role-chip">{nice(user.role)}</span><button className="icon-btn" onClick={refresh} title="Refresh">↻</button><div className="avatar">{user.name?.slice(0,1) || "U"}</div></div>
      </header>
      {notice && <div className="alert success">{notice}<button onClick={() => setNotice("")}>×</button></div>}
      {error && <div className="alert error">{error}<button onClick={() => setError("")}>×</button></div>}
      {loading && <div className="loading-line">Refreshing workspace…</div>}

      {page === "dashboard" && isAdmin && <AdminOverview overview={overview} tasks={tasks} onTasks={() => setPage("tasks")} />}
      {page === "dashboard" && !isAdmin && <TaskList tasks={filteredTasks} isAdmin={false} onProgress={openProgress} />}
      {page === "tasks" && isAdmin && <section className="content-card">
        <div className="section-head"><div><h2>Task management</h2><p>Assign work, monitor status and manage deadlines.</p></div><button className="primary" onClick={() => setTaskForm({})}>+ Create task</button></div>
        <Filters search={search} setSearch={setSearch} status={statusFilter} setStatus={setStatusFilter} />
        <TaskList tasks={filteredTasks} isAdmin onEdit={t => setTaskForm({...t, id:t.task_id ?? t.id})} onDelete={deleteTask} onStatus={changeStatus} />
      </section>}
      {page === "employees" && isAdmin && <section className="content-card">
        <div className="section-head"><div><h2>Employees</h2><p>Manage employee accounts and access.</p></div><button className="primary" onClick={() => setEmployeeForm({})}>+ Add employee</button></div>
        <div className="table-wrap"><table><thead><tr><th>Employee</th><th>Department</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>{employees.map(emp => <tr key={emp.id}><td><strong>{emp.name}</strong><small className="table-sub">{emp.email}</small></td><td>{emp.department || "—"}</td><td>{nice(emp.role)}</td><td><span className={`status ${emp.is_active===false?"inactive":"completed"}`}>{emp.is_active===false?"Inactive":"Active"}</span></td><td className="actions"><button className="text-btn" onClick={() => setEmployeeForm(emp)}>Edit</button>{emp.is_active!==false && emp.id!==user.id && <button className="text-btn danger-text" onClick={() => deactivateEmployee(emp)}>Deactivate</button>}</td></tr>)}</tbody>
        </table>{!employees.length && <Empty text="No employees found." />}</div>
      </section>}
      {page === "reports" && isAdmin && <Reports overview={overview} performance={performance} weekly={weekly} />}
    </main>

    {employeeForm && <Modal title={employeeForm.id?"Edit employee":"Add employee"} onClose={() => setEmployeeForm(null)}>
      <form className="stack" onSubmit={saveEmployee}>
        <label>Full name<input name="name" required minLength="2" defaultValue={employeeForm.name||""}/></label>
        <label>Email<input name="email" type="email" required defaultValue={employeeForm.email||""}/></label>
        {!employeeForm.id && <label>Temporary password<input name="password" type="password" required minLength="8"/></label>}
        <label>Department<input name="department" defaultValue={employeeForm.department||""}/></label>
        <label>Role<select name="role" defaultValue={employeeForm.role||"employee"}><option value="employee">Employee</option><option value="admin">Admin</option></select></label>
        {employeeForm.id && <label>Account status<select name="is_active" defaultValue={String(employeeForm.is_active!==false)}><option value="true">Active</option><option value="false">Inactive</option></select></label>}
        <div className="modal-actions"><button type="button" className="secondary" onClick={() => setEmployeeForm(null)}>Cancel</button><button className="primary">Save employee</button></div>
      </form>
    </Modal>}

    {taskForm && <Modal title={taskForm.id?"Edit task":"Create task"} onClose={() => setTaskForm(null)}>
      <form className="stack" onSubmit={saveTask}>
        <label>Task title<input name="title" required minLength="3" defaultValue={taskForm.title||""}/></label>
        <label>Description<textarea name="description" rows="3" defaultValue={taskForm.description||""}/></label>
        <label>Assign to<select name="assigned_to" required defaultValue={taskForm.assigned_to||""}><option value="" disabled>Select employee</option>{employees.filter(e=>e.is_active!==false && e.role!=="admin").map(e=><option key={e.id} value={e.id}>{e.name} — {e.department||"No department"}</option>)}</select></label>
        <div className="form-grid"><label>Priority<select name="priority" defaultValue={taskForm.priority||"medium"}>{PRIORITIES.map(p=><option key={p} value={p}>{nice(p)}</option>)}</select></label><label>Status<select name="status" defaultValue={taskForm.status||"pending"}>{STATUSES.map(s=><option key={s} value={s}>{nice(s)}</option>)}</select></label></div>
        <label>Due date<input name="due_date" type="datetime-local" defaultValue={taskForm.due_date?new Date(taskForm.due_date).toISOString().slice(0,16):""}/></label>
        <div className="modal-actions"><button type="button" className="secondary" onClick={() => setTaskForm(null)}>Cancel</button><button className="primary">Save task</button></div>
      </form>
    </Modal>}

    {progressFor && <Modal title={`Progress · ${progressFor.title}`} onClose={() => setProgressFor(null)}>
      <form className="stack" onSubmit={submitProgress}>
        <label>Progress percentage <strong>{progressValue}%</strong><input type="range" min="0" max="100" value={progressValue} onChange={e=>setProgressValue(e.target.value)}/></label>
        <label>Update description<textarea rows="3" required minLength="1" maxLength="2000" value={progressText} onChange={e=>setProgressText(e.target.value)} placeholder="Describe the work completed or current progress…"/></label>
        <div className="modal-actions"><button type="button" className="secondary" onClick={() => setProgressFor(null)}>Close</button><button className="primary">Submit update</button></div>
      </form>
      <div className="history"><h3>Progress history</h3>{progressRows.length?progressRows.slice().reverse().map(row=><div className="history-row" key={row.id}><div><strong>{row.progress_percentage}% complete</strong><small>{dateOnly(row.created_at)}</small></div><p>{row.update_text}</p></div>):<p className="muted">No progress updates yet.</p>}</div>
    </Modal>}
  </div>;
}

function AdminOverview({overview, tasks, onTasks}) {
  const cards = [
    ["Total employees", overview.total_employees ?? 0, "People in workspace"],
    ["Total tasks", overview.total_tasks ?? tasks.length, "Assigned work items"],
    ["In progress", overview.in_progress_tasks ?? 0, "Currently underway"],
    ["Completed", overview.completed_tasks ?? 0, "Successfully finished"],
  ];
  return <div className="dashboard-content">
    <div className="welcome-banner"><div><p className="eyebrow">TEAM WORKSPACE</p><h2>Good to see you</h2><p>Here’s what’s happening across your team today.</p></div><div className="banner-symbol">↗</div></div>
    <div className="stats-grid">{cards.map(([label,value,sub])=><div className="stat-card" key={label}><span>{label}</span><strong>{value}</strong><small>{sub}</small></div>)}</div>
    <div className="content-card"><div className="section-head"><div><h2>Recent tasks</h2><p>Latest work across the team.</p></div><button className="text-btn" onClick={onTasks}>View all tasks →</button></div><TaskList tasks={tasks.slice(0,5)} isAdmin={false} compact /></div>
  </div>;
}

function Filters({search,setSearch,status,setStatus}) {
  return <div className="filters"><input placeholder="Search tasks or employees…" value={search} onChange={e=>setSearch(e.target.value)}/><select value={status} onChange={e=>setStatus(e.target.value)}><option value="all">All statuses</option>{STATUSES.map(s=><option key={s} value={s}>{nice(s)}</option>)}</select></div>;
}

function TaskList({tasks,isAdmin,onProgress,onEdit,onDelete,onStatus,compact=false}) {
  if (!tasks.length) return <Empty text="No tasks to display." />;
  return <div className="task-list">{tasks.map(task=>{
    const id=task.task_id ?? task.id;
    return <article className="task-row" key={id}>
      <div className="task-main"><div className="task-title-line"><h3>{task.title}</h3><span className={`status ${task.status||"pending"}`}>{nice(task.status||"pending")}</span></div>
        {task.description && <p>{task.description}</p>}
        <div className="task-meta"><span>Assigned to: <strong>{task.employee_name || task.assignee_name || "You"}</strong></span><span>Priority: <strong className={`priority ${task.priority||"medium"}`}>{nice(task.priority||"medium")}</strong></span>{task.due_date && <span>Due: {dateOnly(task.due_date)}</span>}</div>
      </div>
      {!compact && <div className="task-actions">
        {isAdmin && <><select aria-label="Task status" value={task.status||"pending"} onChange={e=>onStatus(id,e.target.value)}>{STATUSES.map(s=><option key={s} value={s}>{nice(s)}</option>)}</select><button className="text-btn" onClick={()=>onEdit(task)}>Edit</button><button className="text-btn danger-text" onClick={()=>onDelete(task)}>Delete</button></>}
        {!isAdmin && <button className="primary small-btn" onClick={()=>onProgress(task)}>Update progress</button>}
      </div>}
    </article>;
  })}</div>;
}

function Reports({overview,performance,weekly}) {
  return <div className="dashboard-content">
    <div className="stats-grid">{[["Progress updates",overview.total_progress_updates??0],["Active employees",overview.active_employees??0],["Pending tasks",overview.pending_tasks??0],["Completed tasks",overview.completed_tasks??0]].map(([k,v])=><div className="stat-card" key={k}><span>{k}</span><strong>{v}</strong></div>)}</div>
    <section className="content-card"><div className="section-head"><div><h2>Employee performance</h2><p>Task distribution by employee.</p></div></div>
      <div className="table-wrap"><table><thead><tr><th>Employee</th><th>Total</th><th>Pending</th><th>In progress</th><th>Completed</th></tr></thead><tbody>{performance.map(row=><tr key={row.employee_id}><td><strong>{row.employee_name}</strong></td><td>{row.total_tasks}</td><td>{row.pending_tasks}</td><td>{row.in_progress_tasks}</td><td>{row.completed_tasks}</td></tr>)}</tbody></table>{!performance.length&&<Empty text="No performance data available."/>}</div>
    </section>
    <section className="content-card"><div className="section-head"><div><h2>Recent progress updates</h2><p>Last {weekly.report_period_days||7} days · {weekly.total_updates||0} updates</p></div></div>
      {(weekly.updates||[]).map((u,i)=><div className="history-row" key={`${u.task_id}-${i}`}><div><strong>{u.employee_name} · {u.progress_percentage}%</strong><small>{u.task_title} · {dateOnly(u.created_at)}</small></div><p>{u.update_text}</p></div>)}{!(weekly.updates||[]).length&&<Empty text="No progress updates in this period."/>}
    </section>
  </div>;
}

function Modal({title,onClose,children}) {
  return <div className="modal-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)onClose();}}><section className="modal"><div className="modal-head"><h2>{title}</h2><button className="icon-btn" onClick={onClose}>×</button></div>{children}</section></div>;
}
function Empty({text}) { return <div className="empty-state">{text}</div>; }

export default App;
