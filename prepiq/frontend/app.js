// ---------- State ----------
let currentUser = null;
let codeEditor = null;
let activeQuestion = null;
let questionsCache = [];

// ---------- View switching ----------
function showView(name) {
  document.querySelectorAll(".view").forEach((v) => v.classList.add("hidden"));
  document.getElementById(`view-${name}`).classList.remove("hidden");
  document.querySelectorAll("#navbar nav button").forEach((b) => b.classList.remove("active"));
  const navBtn = document.querySelector(`#navbar nav button[data-view="${name}"]`);
  if (navBtn) navBtn.classList.add("active");

  if (name === "dashboard") loadDashboard();
  if (name === "questions") loadQuestions();
  if (name === "leaderboard") loadLeaderboard();
  if (name === "contests") loadContests();
}

document.querySelectorAll("#navbar nav button").forEach((btn) => {
  btn.addEventListener("click", () => showView(btn.dataset.view));
});

// ---------- Auth ----------
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`${btn.dataset.tab}Form`).classList.add("active");
  });
});

document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;
  const errBox = document.getElementById("authError");
  errBox.textContent = "";
  try {
    const tokens = await Api.post("/auth/login", { email, password });
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
    await afterLogin();
  } catch (err) {
    errBox.textContent = err.message;
  }
});

document.getElementById("registerForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("registerName").value;
  const email = document.getElementById("registerEmail").value;
  const password = document.getElementById("registerPassword").value;
  const errBox = document.getElementById("authError");
  errBox.textContent = "";
  try {
    await Api.post("/auth/register", { name, email, password });
    // auto-login right after registering
    const tokens = await Api.post("/auth/login", { email, password });
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
    await afterLogin();
  } catch (err) {
    errBox.textContent = err.message;
  }
});

document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  currentUser = null;
  document.getElementById("navbar").classList.add("hidden");
  showView("auth"); // will be hidden anyway; auth view has no nav entry
  document.getElementById("view-auth").classList.remove("hidden");
});

async function afterLogin() {
  currentUser = await Api.get("/auth/me");
  document.getElementById("userName").textContent = `${currentUser.name} (${currentUser.role})`;
  document.getElementById("navbar").classList.remove("hidden");
  document.getElementById("view-auth").classList.add("hidden");
  if (currentUser.role === "admin") {
    document.getElementById("adminContestForm").classList.remove("hidden");
  }
  showView("dashboard");
}

// ---------- Dashboard ----------
async function loadDashboard() {
  const recBox = document.getElementById("recommendedBox");
  const masteredBox = document.getElementById("masteredBox");
  const unlockedBox = document.getElementById("unlockedBox");
  const orderBox = document.getElementById("topicOrderBox");

  try {
    const rec = await Api.get("/recommend/next-question");
    if (rec.question) {
      recBox.innerHTML = `
        <strong>${rec.question.title}</strong>
        <div class="tag">${rec.question.difficulty}</div>
        <div class="tag">${rec.question.topic}</div>
        <p style="margin-top:8px;color:#8a8fa3;font-size:0.85rem;">
          Suggested because: ${rec.reasoning.why_this_topic || "recommended for your level"}
        </p>`;
    } else {
      recBox.textContent = rec.reasoning.message || "No recommendation yet — solve a few questions first.";
    }
  } catch (err) {
    recBox.textContent = `Error: ${err.message}`;
  }

  try {
    const next = await Api.get("/topics/next-unlocked");
    masteredBox.innerHTML = next.mastered.length
      ? next.mastered.map((t) => `<span class="tag">${t}</span>`).join("")
      : `<span style="color:#6b7086">None yet — keep solving!</span>`;
    unlockedBox.innerHTML = next.unlocked_next.length
      ? next.unlocked_next.map((t) => `<span class="tag">${t}</span>`).join("")
      : `<span style="color:#6b7086">Nothing new unlocked</span>`;
  } catch (err) {
    masteredBox.textContent = `Error: ${err.message}`;
  }

  try {
    const order = await Api.get("/topics/order");
    orderBox.innerHTML = order.order.map((t, i) => `<span class="tag">${i + 1}. ${t}</span>`).join("");
  } catch (err) {
    orderBox.textContent = `Error: ${err.message}`;
  }
}

// ---------- Questions ----------
async function loadQuestions() {
  const difficulty = document.getElementById("difficultyFilter").value;
  const path = difficulty ? `/questions?difficulty=${difficulty}` : "/questions";
  try {
    questionsCache = await Api.get(path);
    renderQuestionList(questionsCache);
  } catch (err) {
    document.getElementById("questionList").textContent = `Error: ${err.message}`;
  }
}

function renderQuestionList(questions) {
  const list = document.getElementById("questionList");
  if (!questions.length) {
    list.innerHTML = `<p class="placeholder">No questions found.</p>`;
    return;
  }
  list.innerHTML = questions
    .map(
      (q) => `
      <div class="question-item" data-id="${q.id}">
        <div>${q.title}</div>
        <span class="diff diff-${q.difficulty}">${q.difficulty}</span>
        <span class="tag">${q.topic}</span>
      </div>`
    )
    .join("");

  list.querySelectorAll(".question-item").forEach((el) => {
    el.addEventListener("click", () => openQuestion(el.dataset.id));
  });
}

document.getElementById("difficultyFilter").addEventListener("change", loadQuestions);

let searchDebounce;
document.getElementById("searchBox").addEventListener("input", (e) => {
  clearTimeout(searchDebounce);
  const prefix = e.target.value.trim();
  const suggestBox = document.getElementById("searchSuggestions");
  if (!prefix) {
    suggestBox.classList.add("hidden");
    return;
  }
  searchDebounce = setTimeout(async () => {
    try {
      const res = await Api.get(`/search/autocomplete?prefix=${encodeURIComponent(prefix)}`);
      if (!res.matches.length) {
        suggestBox.classList.add("hidden");
        return;
      }
      suggestBox.innerHTML = res.matches.map((m) => `<div>${m}</div>`).join("");
      suggestBox.classList.remove("hidden");
      suggestBox.querySelectorAll("div").forEach((div) => {
        div.addEventListener("click", () => {
          const match = questionsCache.find((q) => q.title === div.textContent);
          suggestBox.classList.add("hidden");
          document.getElementById("searchBox").value = div.textContent;
          if (match) openQuestion(match.id);
        });
      });
    } catch (_) {
      suggestBox.classList.add("hidden");
    }
  }, 250);
});

async function openQuestion(id) {
  activeQuestion = await Api.get(`/questions/${id}`);
  document.querySelectorAll(".question-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.id === id);
  });

  const detail = document.getElementById("questionDetail");
  detail.innerHTML = `
    <h3>${activeQuestion.title}</h3>
    <span class="diff diff-${activeQuestion.difficulty}">${activeQuestion.difficulty}</span>
    <span class="tag">${activeQuestion.topic}</span>
    <p style="margin-top:12px;">${activeQuestion.description}</p>
    <textarea id="codeArea"># write your Python solution here
# read input with input(), print output with print()
</textarea>
    <button id="submitCodeBtn">Submit</button>
    <div id="submitResult"></div>
  `;

  codeEditor = CodeMirror.fromTextArea(document.getElementById("codeArea"), {
    mode: "python",
    theme: "dracula",
    lineNumbers: true,
    indentUnit: 4,
  });

  document.getElementById("submitCodeBtn").addEventListener("click", submitCode);
}

async function submitCode() {
  const resultBox = document.getElementById("submitResult");
  resultBox.innerHTML = `<p class="placeholder">Running...</p>`;
  try {
    const result = await Api.post("/questions/submit", {
      question_id: activeQuestion.id,
      code: codeEditor.getValue(),
    });
    const cls = result.verdict === "Accepted" ? "result-accepted" : "result-failed";
    resultBox.innerHTML = `
      <div class="result-box ${cls}">
        ${result.verdict} — ${result.passed_cases}/${result.total_cases} test cases passed
        (${result.runtime_ms ? result.runtime_ms.toFixed(1) + "ms" : "n/a"})
      </div>`;
  } catch (err) {
    resultBox.innerHTML = `<div class="result-box result-failed">Error: ${err.message}</div>`;
  }
}

// ---------- Leaderboard ----------
async function loadLeaderboard() {
  const body = document.getElementById("leaderboardBody");
  try {
    const rows = await Api.get("/leaderboard");
    body.innerHTML = rows.length
      ? rows.map((r) => `<tr><td>#${r.rank}</td><td>${r.user_name}</td><td>${r.score}</td></tr>`).join("")
      : `<tr><td colspan="3">No submissions yet.</td></tr>`;
  } catch (err) {
    body.innerHTML = `<tr><td colspan="3">Error: ${err.message}</td></tr>`;
  }
}

// ---------- Contests ----------
async function loadContests() {
  const list = document.getElementById("contestList");
  try {
    const contests = await Api.get("/contests");
    list.innerHTML = contests.length
      ? contests
          .map(
            (c) => `
        <div class="card contest-card">
          <div>
            <strong>${c.title}</strong>
            <div class="status-badge status-${c.status}">${c.status}</div>
          </div>
          <div>
            ${c.seconds_remaining !== null ? formatSeconds(c.seconds_remaining) : ""}
            <button data-join="${c.id}">Join</button>
            <button data-board="${c.id}">Leaderboard</button>
          </div>
        </div>`
          )
          .join("")
      : `<p class="placeholder">No contests yet.</p>`;

    list.querySelectorAll("[data-join]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        try {
          await Api.post(`/contests/${btn.dataset.join}/join`);
          alert("Joined contest!");
        } catch (err) {
          alert(err.message);
        }
      });
    });
    list.querySelectorAll("[data-board]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const rows = await Api.get(`/contests/${btn.dataset.board}/leaderboard`);
        alert(rows.map((r) => `#${r.rank} ${r.user_name} — ${r.score}`).join("\n") || "No entries yet.");
      });
    });
  } catch (err) {
    list.innerHTML = `Error: ${err.message}`;
  }
}

function formatSeconds(s) {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  return `${h}h ${m}m left`;
}

document.getElementById("createContestBtn").addEventListener("click", async () => {
  const title = document.getElementById("contestTitle").value;
  const ids = document
    .getElementById("contestQuestionIds")
    .value.split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  const start = document.getElementById("contestStart").value;
  const end = document.getElementById("contestEnd").value;
  try {
    await Api.post("/contests", {
      title,
      question_ids: ids,
      start_time: new Date(start).toISOString(),
      end_time: new Date(end).toISOString(),
    });
    loadContests();
  } catch (err) {
    alert(err.message);
  }
});

// ---------- Resume ----------
document.getElementById("uploadResumeBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("resumeFile");
  if (!fileInput.files.length) return alert("Choose a .txt file first");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const result = await Api.postForm("/resume/upload", formData);
    document.getElementById("resumeResult").classList.remove("hidden");
    document.getElementById("skillsBox").innerHTML =
      result.extracted_skills.map((s) => `<span class="tag">${s}</span>`).join("") || "None found";
    document.getElementById("topicsBox").innerHTML =
      result.matched_topics.map((t) => `<span class="tag">${t}</span>`).join("") || "None found";
  } catch (err) {
    alert(err.message);
  }
});

// ---------- Boot ----------
(async function init() {
  if (Api.getAccessToken()) {
    try {
      await afterLogin();
      return;
    } catch (_) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  }
  document.getElementById("view-auth").classList.remove("hidden");
})();
