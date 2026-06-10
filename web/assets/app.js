const state = {
  summary: null,
  packageIndex: null,
  path: [],
  docs: [],
  currentLevel: "ALL",
  currentNode: null,
  progress: loadProgress(),
};

const els = {
  sidebar: document.querySelector("#sidebar"),
  mobileMenuButton: document.querySelector("#mobileMenuButton"),
  mobileBackdrop: document.querySelector("#mobileBackdrop"),
  statusGrid: document.querySelector("#statusGrid"),
  dashboardPanel: document.querySelector("#dashboardPanel"),
  coursesPanel: document.querySelector("#coursesPanel"),
  packagePanel: document.querySelector("#packagePanel"),
  sourcesPanel: document.querySelector("#sourcesPanel"),
  progressPanel: document.querySelector("#progressPanel"),
  lessonPanel: document.querySelector("#lessonPanel"),
  levelFilters: document.querySelector("#levelFilters"),
  lessonList: document.querySelector("#lessonList"),
  searchInput: document.querySelector("#searchInput"),
  activeMeta: document.querySelector("#activeMeta"),
  activeTitle: document.querySelector("#activeTitle"),
  overviewBand: document.querySelector("#overviewBand"),
  sectionTabs: document.querySelector("#sectionTabs"),
  contentView: document.querySelector("#contentView"),
  toggleComplete: document.querySelector("#toggleComplete"),
  resetProgress: document.querySelector("#resetProgress"),
};

async function boot() {
  const [summary, path, docs, packageIndex] = await Promise.all([
    fetchJson("data/summary.json"),
    fetchJson("data/learning-path.json"),
    fetchJson("data/source-documents.json"),
    fetchJson("data/lms-package/package-index.json"),
  ]);
  state.summary = summary;
  state.packageIndex = packageIndex;
  state.path = path;
  state.docs = docs;
  renderShell();
  window.addEventListener("hashchange", handleRouteChange);
  handleRouteChange({ replace: true, scroll: false });
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Failed to load ${url}`);
  return response.json();
}

function renderShell() {
  renderStats();
  renderDashboard();
  renderCourses();
  renderPackage();
  renderSources();
  renderProgress();
  renderFilters();
  renderList();
  els.searchInput.addEventListener("input", renderList);
  els.toggleComplete.addEventListener("click", toggleCurrentComplete);
  els.resetProgress.addEventListener("click", resetProgress);
  els.mobileMenuButton.addEventListener("click", toggleMobileMenu);
  els.mobileBackdrop.addEventListener("click", closeMobileMenu);
  document.querySelectorAll("[data-route]").forEach((button) => {
    button.addEventListener("click", () => {
      navigateToPage(button.dataset.route);
      closeMobileMenu();
    });
  });
}

function renderStats() {
  const completed = Object.keys(state.progress.completed).length;
  els.statusGrid.innerHTML = [
    stat("Nodes", state.summary.indexed_nodes),
    stat("Done", completed),
    stat("Sources", state.summary.source_documents),
    stat("Extracted", state.summary.content_blocks),
  ].join("");
}

function stat(label, value) {
  return `<div class="stat"><strong>${escapeHtml(String(value))}</strong><span>${escapeHtml(label)}</span></div>`;
}

function renderDashboard() {
  const completed = Object.keys(state.progress.completed).length;
  const nextNode = state.path.find((node) => !state.progress.completed[node.id]) || state.path[0];
  const extracted = state.path.filter((node) => node.content_ref).length;
  const sourceBacked = state.path.filter((node) => !node.content_ref && node.source_document).length;
  const levels = ["FOUNDATIONS", "N5", "N4", "N3", "N2", "N1", "SUPPLEMENTS"].filter((level) => state.summary.levels[level] || level === "FOUNDATIONS");
  els.dashboardPanel.innerHTML = `
    <div class="dashboard-heading">
      <div>
        <p class="eyebrow">Zero-budget static LMS</p>
        <h2>Find the right Japanese study area fast</h2>
      </div>
      <button class="primary-button" type="button" data-action="continue" data-id="${escapeHtml(nextNode.id)}">Continue ${escapeHtml(nextNode.id)}</button>
    </div>

    <div class="feature-grid" id="featureMap">
      ${featureCard("Learning Path", `${state.summary.indexed_nodes} indexed items`, "Browse Foundations through N1 in order.", "path")}
      ${featureCard("Lesson Reader", `${extracted} extracted lessons`, "Open lessons with objectives, vocabulary, and source content.", "current")}
      ${featureCard("LMS Package", `${state.packageIndex.artifacts.length} export files`, "Open course structure, Anki TSV, mock specs, workbook specs, and manifest.", "package")}
      ${featureCard("Progress", `${completed} completed locally`, "Completion is saved in this browser with no account required.", "progress")}
    </div>

    <div class="level-map" id="levelMap">
      ${levels.map((level) => levelButton(level)).join("")}
    </div>

    <div class="package-map" id="packageMap">
      <div>
        <strong>LMS package exports</strong>
        <span>${state.packageIndex.rule}</span>
      </div>
      <div class="package-links">
        ${state.packageIndex.artifacts.map((artifact) => packageLink(artifact)).join("")}
      </div>
    </div>

    <div class="dashboard-foot">
      <button class="ghost-button" type="button" data-action="showExtracted">Show extracted lessons</button>
      <button class="ghost-button" type="button" data-action="showSourceBacked">Show source-backed nodes</button>
      <button class="ghost-button" type="button" data-action="sources">Show source library</button>
      <span>${sourceBacked} nodes currently open their source document directly.</span>
    </div>
  `;
  els.dashboardPanel.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", () => handleDashboardAction(button.dataset.action, button.dataset.id));
  });
  els.dashboardPanel.querySelectorAll("[data-level]").forEach((button) => {
    button.addEventListener("click", () => {
      state.currentLevel = button.dataset.level;
      els.searchInput.value = "";
      renderFilters();
      renderList();
      revealCatalog();
    });
  });
}

function renderCourses() {
  const levels = Object.keys(state.summary.levels);
  els.coursesPanel.innerHTML = `
    <div class="page-heading">
      <p class="eyebrow">Structured learning paths</p>
      <h2>Courses, modules, and gates</h2>
      <p>Use MAIN for JLPT pass study. OPTIONAL and SUPPLEMENTS are enrichment for real-world fluency.</p>
    </div>
    <div class="course-grid">
      ${levels.map((level) => courseCard(level)).join("")}
    </div>
  `;
  els.coursesPanel.querySelectorAll("[data-level]").forEach((button) => {
    button.addEventListener("click", () => {
      state.currentLevel = button.dataset.level;
      els.searchInput.value = "";
      renderFilters();
      renderList();
      navigateToPage("courses");
      revealCatalog();
    });
  });
}

function courseCard(level) {
  const info = state.summary.levels[level];
  const modules = Object.entries(info.modules || {})
    .map(([module, count]) => `<span>${escapeHtml(module)} <strong>${escapeHtml(String(count))}</strong></span>`)
    .join("");
  return `
    <article class="course-card">
      <div>
        <p class="eyebrow">${escapeHtml(level)}</p>
        <h3>${escapeHtml(courseName(level))}</h3>
      </div>
      <div class="course-metrics">
        <span>${escapeHtml(String(info.lesson_count))} SCOs</span>
        <span>${escapeHtml(String(info.main))} MAIN</span>
        <span>${escapeHtml(String(info.optional))} OPTIONAL</span>
      </div>
      <div class="module-strip">${modules}</div>
      <button class="ghost-button" type="button" data-level="${escapeHtml(level)}">Browse ${escapeHtml(level)}</button>
    </article>
  `;
}

function courseName(level) {
  if (level === "FOUNDATIONS") return "Before N5";
  if (level === "SUPPLEMENTS") return "Supplement Library";
  return `JLPT ${level}`;
}

function renderPackage() {
  els.packagePanel.innerHTML = `
    <div class="page-heading">
      <p class="eyebrow">Build prompt outputs</p>
      <h2>LMS package exports</h2>
      <p>${escapeHtml(state.packageIndex.rule)}</p>
    </div>
    <div class="artifact-grid">
      ${state.packageIndex.artifacts.map((artifact) => packageLink(artifact)).join("")}
    </div>
    <div class="scope-grid">
      ${Object.entries(state.packageIndex.counts).map(([key, value]) => stat(key.replaceAll("_", " "), value)).join("")}
    </div>
  `;
}

function renderSources() {
  els.sourcesPanel.innerHTML = `
    <div class="page-heading">
      <p class="eyebrow">Source library</p>
      <h2>Original handoff documents</h2>
      <p>These files remain the preserved source text for source-backed lesson nodes.</p>
    </div>
    <div class="source-grid">
      ${state.docs.map((doc) => sourceCard(doc)).join("")}
    </div>
  `;
  els.sourcesPanel.querySelectorAll("[data-source]").forEach((button) => {
    button.addEventListener("click", () => {
      els.searchInput.value = button.dataset.source;
      state.currentLevel = "ALL";
      renderFilters();
      renderList();
      revealCatalog();
    });
  });
}

function sourceCard(doc) {
  return `
    <article class="source-card">
      <strong>${escapeHtml(doc.filename)}</strong>
      <span>${escapeHtml(doc.title)}</span>
      <small>${escapeHtml(String(doc.char_count))} chars</small>
      <button class="ghost-button" type="button" data-source="${escapeHtml(doc.filename)}">Find lessons</button>
    </article>
  `;
}

function renderProgress() {
  const completed = Object.keys(state.progress.completed);
  const percent = state.path.length ? Math.round((completed.length / state.path.length) * 100) : 0;
  const recent = completed.slice(-8).reverse();
  els.progressPanel.innerHTML = `
    <div class="page-heading">
      <p class="eyebrow">Local browser progress</p>
      <h2>${percent}% complete on this device</h2>
      <p>No account or server is required. Progress is saved locally in this browser.</p>
    </div>
    <div class="progress-meter"><span style="width: ${percent}%"></span></div>
    <div class="scope-grid">
      ${stat("completed", completed.length)}
      ${stat("remaining", Math.max(state.path.length - completed.length, 0))}
      ${stat("total nodes", state.path.length)}
      ${stat("storage", "localStorage")}
    </div>
    <div class="recent-list">
      <h3>Recently completed</h3>
      ${recent.length ? recent.map((id) => `<button type="button" data-lesson="${escapeHtml(id)}">${escapeHtml(id)}</button>`).join("") : "<p>No completed lessons yet.</p>"}
    </div>
  `;
  els.progressPanel.querySelectorAll("[data-lesson]").forEach((button) => {
    button.addEventListener("click", () => navigateToNode(button.dataset.lesson));
  });
}

function featureCard(title, metric, body, action) {
  return `
    <button class="feature-card" type="button" data-action="${escapeHtml(action)}">
      <strong>${escapeHtml(title)}</strong>
      <span>${escapeHtml(metric)}</span>
      <small>${escapeHtml(body)}</small>
    </button>
  `;
}

function levelButton(level) {
  const levelInfo = state.summary.levels[level];
  const count = levelInfo?.lesson_count || state.path.filter((node) => node.level === level).length;
  const optional = levelInfo?.optional ? ` + ${levelInfo.optional} optional` : "";
  const first = state.path.find((node) => node.level === level);
  return `
    <button class="level-card" type="button" data-level="${escapeHtml(level)}" data-first="${escapeHtml(first?.id || "")}">
      <span>${escapeHtml(level)}</span>
      <strong>${escapeHtml(String(count))}</strong>
      <small>${first ? `Starts at ${escapeHtml(first.id)}${escapeHtml(optional)}` : "Coming soon"}</small>
    </button>
  `;
}

function packageLink(artifact) {
  return `
    <a class="package-link" href="${escapeHtml(artifact.path)}" target="_blank" rel="noopener">
      <strong>Task ${escapeHtml(String(artifact.task))}</strong>
      <span>${escapeHtml(artifact.name)}</span>
      <small>${escapeHtml(artifact.format)}</small>
    </a>
  `;
}

function handleDashboardAction(action, nodeId) {
  if (action === "continue" && nodeId) {
    navigateToNode(nodeId);
    return;
  }
  if (action === "path") {
    navigateToPage("courses");
    return;
  }
  if (action === "current") {
    if (state.currentNode) navigateToNode(state.currentNode.id);
    return;
  }
  if (action === "sources") {
    navigateToPage("sources");
    return;
  }
  if (action === "package") {
    navigateToPage("package");
    return;
  }
  if (action === "progress") {
    navigateToPage("progress");
    return;
  }
  if (action === "showExtracted") {
    els.searchInput.value = "lesson extract";
    renderList();
    revealCatalog();
    return;
  }
  if (action === "showSourceBacked") {
    els.searchInput.value = "source doc";
    renderList();
    revealCatalog();
  }
}

function renderFilters() {
  const levels = ["ALL", ...Object.keys(state.summary.levels)];
  els.levelFilters.innerHTML = levels
    .map((level) => `<button class="filter-button ${level === state.currentLevel ? "active" : ""}" data-level="${level}">${level}</button>`)
    .join("");
  els.levelFilters.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      state.currentLevel = button.dataset.level;
      renderFilters();
      renderList();
    });
  });
}

function renderList() {
  const query = els.searchInput.value.trim().toLowerCase();
  const filtered = state.path.filter((node) => {
    const levelMatch = state.currentLevel === "ALL" || node.level === state.currentLevel;
    const contentType = node.content_ref ? "lesson extract" : "source doc";
    const queryMatch = !query || `${node.id} ${node.title} ${node.skill || ""} ${node.source_document || ""} ${contentType}`.toLowerCase().includes(query);
    return levelMatch && queryMatch;
  });
  els.lessonList.innerHTML = filtered
    .slice(0, 500)
    .map((node) => {
      const done = Boolean(state.progress.completed[node.id]);
      const active = state.currentNode?.id === node.id;
      return `
        <button class="lesson-button ${done ? "done" : ""} ${active ? "active" : ""}" data-id="${node.id}">
          <strong>${escapeHtml(node.id)} · ${escapeHtml(node.title)}</strong>
          <span>${escapeHtml(node.level)} / ${escapeHtml(node.module)} · ${escapeHtml(node.track)}${node.content_ref ? " · lesson extract" : " · source doc"}</span>
        </button>
      `;
    })
    .join("");
  els.lessonList.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => navigateToNode(button.dataset.id));
  });
}

function toggleMobileMenu() {
  const isOpen = document.body.classList.toggle("mobile-menu-open");
  els.mobileBackdrop.hidden = !isOpen;
  els.mobileMenuButton.setAttribute("aria-expanded", String(isOpen));
}

function closeMobileMenu() {
  document.body.classList.remove("mobile-menu-open");
  els.mobileBackdrop.hidden = true;
  els.mobileMenuButton.setAttribute("aria-expanded", "false");
}

function revealCatalog() {
  if (window.matchMedia("(max-width: 920px)").matches) {
    closeMobileMenu();
    return;
  }
  els.sidebar.scrollIntoView({ behavior: "smooth", block: "start" });
}

function handleRouteChange(options = {}) {
  const route = parseRoute();
  if (route.redirect) {
    history.replaceState(null, "", route.redirect);
    handleRouteChange(options);
    return;
  }
  showView(route.page);
  if (route.page === "lesson") {
    const node = state.path.find((item) => item.id === route.nodeId) || state.path.find((item) => item.id === "F01") || state.path[0];
    selectNode(node, { ...options, sectionId: route.sectionId });
  } else {
    updatePageTitle(route.page);
  }
}

function parseRoute() {
  const raw = decodeURIComponent(window.location.hash.replace(/^#\/?/, ""));
  if (!raw) return { page: "dashboard" };
  const parts = raw.split("/");
  const knownPages = new Set(["dashboard", "courses", "package", "sources", "progress"]);
  if (knownPages.has(parts[0])) return { page: parts[0] };
  if (parts[0] === "lesson") return { page: "lesson", nodeId: parts[1], sectionId: parts[2] };
  if (state.path.some((node) => node.id === parts[0])) {
    const section = parts[1] ? `/${encodeURIComponent(parts[1])}` : "";
    return { redirect: `#/lesson/${encodeURIComponent(parts[0])}${section}` };
  }
  return { redirect: "#/dashboard" };
}

function navigateToNode(nodeId, sectionId = "") {
  const hash = sectionId ? `#/lesson/${encodeURIComponent(nodeId)}/${encodeURIComponent(sectionId)}` : `#/lesson/${encodeURIComponent(nodeId)}`;
  if (window.location.hash === hash) {
    selectNode(state.path.find((node) => node.id === nodeId), { sectionId });
    closeMobileMenu();
    return;
  }
  window.location.hash = hash;
  closeMobileMenu();
}

function navigateToPage(page) {
  const hash = `#/${page}`;
  if (window.location.hash === hash) {
    handleRouteChange();
    return;
  }
  window.location.hash = hash;
}

function showView(page) {
  const visible = {
    dashboard: els.dashboardPanel,
    courses: els.coursesPanel,
    package: els.packagePanel,
    sources: els.sourcesPanel,
    progress: els.progressPanel,
    lesson: els.lessonPanel,
  };
  Object.values(visible).forEach((panel) => {
    panel.hidden = true;
  });
  (visible[page] || els.dashboardPanel).hidden = false;
  document.querySelectorAll("[data-route]").forEach((button) => {
    button.classList.toggle("active", button.dataset.route === page);
  });
}

function updatePageTitle(page) {
  const titles = {
    dashboard: "Dashboard | Nihongo LMS",
    courses: "Courses | Nihongo LMS",
    package: "LMS Package | Nihongo LMS",
    sources: "Source Library | Nihongo LMS",
    progress: "Progress | Nihongo LMS",
  };
  document.title = titles[page] || "Nihongo LMS";
}

async function selectNode(node, options = {}) {
  if (!node) return;
  state.currentNode = node;
  document.title = `${node.id} | ${node.title}`;
  els.activeMeta.textContent = `${node.level} · ${node.module} · ${node.track}`;
  els.activeTitle.textContent = `${node.id} — ${node.title}`;
  renderOverview(node);
  renderList();
  els.contentView.innerHTML = "<p>Loading content...</p>";
  els.sectionTabs.innerHTML = "";
  if (node.content_ref) {
    const lesson = await fetchJson(node.content_ref);
    els.contentView.innerHTML = renderLesson(lesson);
  } else if (node.source_document) {
    const source = await fetchJson(`data/source-docs/${safeFilename(node.source_document)}.json`);
    els.contentView.innerHTML = renderSourceFallback(node, source);
  } else {
    els.contentView.innerHTML = renderNoContent(node);
  }
  buildSectionTabs(node, options.sectionId);
  els.toggleComplete.textContent = state.progress.completed[node.id] ? "Mark Incomplete" : "Mark Complete";
  if (options.replace && !window.location.hash) {
    history.replaceState(null, "", `#/${encodeURIComponent(node.id)}`);
  }
  focusSelectedLesson();
  if (options.sectionId) {
    scrollToSection(options.sectionId);
  } else if (options.scroll !== false) {
    scrollMainIntoView();
  }
}

function renderOverview(node) {
  const doc = state.docs.find((item) => item.filename === node.source_document);
  els.overviewBand.innerHTML = [
    overview("Track", node.track),
    overview("Skill", node.skill || "mixed"),
    overview("Time", node.estimated_minutes ? `${node.estimated_minutes} min` : "not set"),
    overview("Source", doc ? doc.filename : node.source_document || "index only"),
  ].join("");
}

function overview(label, value) {
  return `<div class="overview-item"><span>${escapeHtml(label)}</span><strong>${escapeHtml(String(value))}</strong></div>`;
}

function renderLesson(lesson) {
  return `
    <div class="pill">${escapeHtml(lesson.source_document)}</div>
    ${lesson.objectives?.length ? `<h2>Learning Objectives</h2><ul>${lesson.objectives.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
    ${lesson.vocabulary?.length ? `<h2>Vocabulary Extract</h2>${renderTable(lesson.vocabulary.slice(0, 80))}` : ""}
    ${lesson.checklist?.length ? `<h2>Progress Checklist</h2><ul>${lesson.checklist.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
    <h2>Lesson Source</h2>
    ${renderMarkdown(lesson.markdown)}
  `;
}

function renderSourceFallback(node, source) {
  return `
    <div class="pill">Bundled source document</div>
    <p>This node is indexed from the curriculum map. Its content lives in the bundled source document below.</p>
    <h2>${escapeHtml(source.filename)}</h2>
    ${renderMarkdown(source.markdown)}
  `;
}

function renderNoContent(node) {
  return `
    <h2>${escapeHtml(node.id)}</h2>
    <p>This node exists in the learning path index, but no source document was matched by the parser yet.</p>
  `;
}

function buildSectionTabs(node, activeSectionId = "") {
  const headings = Array.from(els.contentView.querySelectorAll("h2, h3")).slice(0, 10);
  headings.forEach((heading, index) => {
    const id = heading.id || `${node.id.toLowerCase()}-section-${index + 1}`;
    heading.id = id;
  });
  if (!headings.length) {
    els.sectionTabs.innerHTML = "";
    return;
  }
  els.sectionTabs.innerHTML = headings
    .map((heading) => {
      const active = heading.id === activeSectionId ? " active" : "";
      return `<button class="section-tab${active}" data-section="${escapeHtml(heading.id)}" type="button">${escapeHtml(heading.textContent.trim())}</button>`;
    })
    .join("");
  els.sectionTabs.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => navigateToNode(node.id, button.dataset.section));
  });
}

function focusSelectedLesson() {
  const active = els.lessonList.querySelector(".lesson-button.active");
  if (active) active.scrollIntoView({ block: "nearest" });
}

function scrollMainIntoView() {
  document.querySelector(".main-panel").scrollIntoView({ behavior: "smooth", block: "start" });
}

function scrollToSection(sectionId) {
  requestAnimationFrame(() => {
    const section = document.getElementById(sectionId);
    if (!section) {
      scrollMainIntoView();
      return;
    }
    section.scrollIntoView({ behavior: "smooth", block: "start" });
    els.sectionTabs.querySelectorAll(".section-tab").forEach((tab) => {
      tab.classList.toggle("active", tab.dataset.section === sectionId);
    });
  });
}

function renderTable(rows) {
  if (!rows.length) return "";
  const headers = Object.keys(rows[0]);
  return `
    <table>
      <thead><tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr></thead>
      <tbody>${rows.map((row) => `<tr>${headers.map((header) => `<td>${escapeHtml(row[header] || "")}</td>`).join("")}</tr>`).join("")}</tbody>
    </table>
  `;
}

function renderMarkdown(markdown) {
  const lines = markdown.split(/\r?\n/);
  const html = [];
  let inList = false;
  let table = [];
  const flushList = () => {
    if (inList) {
      html.push("</ul>");
      inList = false;
    }
  };
  const flushTable = () => {
    if (table.length >= 2) {
      const headers = table[0].slice(1, -1).split("|").map((cell) => cell.trim());
      const rows = table.slice(2).map((row) => row.slice(1, -1).split("|").map((cell) => cell.trim()));
      html.push(`<table><thead><tr>${headers.map((h) => `<th>${escapeHtml(h)}</th>`).join("")}</tr></thead><tbody>`);
      rows.forEach((row) => html.push(`<tr>${row.map((cell) => `<td>${inline(cell)}</td>`).join("")}</tr>`));
      html.push("</tbody></table>");
    }
    table = [];
  };

  for (const line of lines) {
    if (line.trim().startsWith("|")) {
      flushList();
      table.push(line.trim());
      continue;
    }
    flushTable();
    if (!line.trim()) {
      flushList();
      continue;
    }
    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      flushList();
      const level = Math.min(heading[1].length + 1, 4);
      html.push(`<h${level}>${inline(heading[2])}</h${level}>`);
      continue;
    }
    if (/^[-*]\s+/.test(line.trim())) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${inline(line.trim().replace(/^[-*]\s+/, ""))}</li>`);
      continue;
    }
    flushList();
    html.push(`<p>${inline(line)}</p>`);
  }
  flushList();
  flushTable();
  return html.join("");
}

function inline(value) {
  return escapeHtml(value)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>");
}

function toggleCurrentComplete() {
  if (!state.currentNode) return;
  if (state.progress.completed[state.currentNode.id]) {
    delete state.progress.completed[state.currentNode.id];
  } else {
    state.progress.completed[state.currentNode.id] = new Date().toISOString();
  }
  saveProgress();
  renderStats();
  renderDashboard();
  renderProgress();
  renderList();
  els.toggleComplete.textContent = state.progress.completed[state.currentNode.id] ? "Mark Incomplete" : "Mark Complete";
}

function resetProgress() {
  if (!confirm("Reset all local progress on this device?")) return;
  state.progress = { completed: {} };
  saveProgress();
  renderStats();
  renderDashboard();
  renderProgress();
  renderList();
  if (state.currentNode) els.toggleComplete.textContent = "Mark Complete";
}

function loadProgress() {
  try {
    return JSON.parse(localStorage.getItem("nihongo-daigaku-progress")) || { completed: {} };
  } catch {
    return { completed: {} };
  }
}

function saveProgress() {
  localStorage.setItem("nihongo-daigaku-progress", JSON.stringify(state.progress));
}

function safeFilename(filename) {
  return filename.replace(/[^A-Za-z0-9_.-]+/g, "_");
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[char]);
}

boot().catch((error) => {
  els.contentView.innerHTML = `<h2>Could not load LMS data</h2><pre>${escapeHtml(error.stack || String(error))}</pre>`;
});
