const state = {
  data: window.BEAHERO_INITIAL_STATE,
  pending: false,
};

const elements = {
  eyebrow: document.getElementById("eyebrow"),
  roomTitle: document.getElementById("room-title"),
  roomDescription: document.getElementById("room-description"),
  roomHint: document.getElementById("room-hint"),
  mapHeading: document.getElementById("map-heading"),
  mapText: document.getElementById("map-text"),
  mapLegend: document.getElementById("map-legend"),
  statusHeading: document.getElementById("status-heading"),
  statsList: document.getElementById("stats-list"),
  winNote: document.getElementById("win-note"),
  actionsHeading: document.getElementById("actions-heading"),
  actionsList: document.getElementById("actions-list"),
  logHeading: document.getElementById("log-heading"),
  logList: document.getElementById("log-list"),
  restartButton: document.getElementById("restart-button"),
  langButtons: document.querySelectorAll("[data-lang]"),
  statusNote: document.getElementById("status-note"),
};

function setPending(pending) {
  state.pending = pending;
  elements.restartButton.disabled = pending;
  elements.statusNote.textContent = pending ? state.data.ui.status_updating : "";
  for (const button of elements.actionsList.querySelectorAll("button")) {
    button.disabled = pending;
  }
  for (const button of elements.langButtons) {
    button.disabled = pending;
  }
}

function renderStats(stats) {
  elements.statsList.innerHTML = "";
  for (const item of stats) {
    const li = document.createElement("li");
    const label = document.createElement("span");
    const value = document.createElement("strong");
    label.textContent = item.label;
    value.textContent = item.value;
    li.append(label, value);
    elements.statsList.appendChild(li);
  }
}

function renderActions(actions) {
  elements.actionsList.innerHTML = "";
  for (const item of actions) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = item.label;
    button.disabled = state.pending;
    button.addEventListener("click", () => runAction(item.key));
    elements.actionsList.appendChild(button);
  }
}

function renderLog(log) {
  elements.logList.innerHTML = "";
  for (const line of log) {
    const li = document.createElement("li");
    li.textContent = line;
    elements.logList.appendChild(li);
  }
}

function render(nextState) {
  state.data = nextState;
  document.documentElement.lang = nextState.ui.lang;
  document.title = nextState.ui.page_title;
  elements.eyebrow.textContent = nextState.ui.eyebrow;
  elements.roomTitle.textContent = nextState.room.title;
  elements.roomDescription.textContent = nextState.room.description;
  elements.roomHint.textContent = nextState.room.action_text;
  elements.mapHeading.textContent = nextState.ui.map_heading;
  elements.mapText.innerHTML = nextState.map_html;
  elements.mapLegend.textContent = nextState.ui.map_legend;
  elements.statusHeading.textContent = nextState.ui.status_heading;
  elements.actionsHeading.textContent = nextState.won ? nextState.ui.aftermath_heading : nextState.ui.actions_heading;
  elements.logHeading.textContent = nextState.ui.log_heading;
  elements.restartButton.textContent = nextState.ui.restart;
  renderStats(nextState.stats);
  renderActions(nextState.actions);
  renderLog(nextState.log);

  if (nextState.won) {
    elements.winNote.hidden = false;
    elements.winNote.textContent = nextState.ui.win_note;
  } else {
    elements.winNote.hidden = true;
    elements.winNote.textContent = "";
  }

  for (const button of elements.langButtons) {
    button.textContent = nextState.ui[`lang_${button.dataset.lang}`];
    button.classList.toggle("active", button.dataset.lang === nextState.ui.lang);
  }
}

async function postJSON(url, payload = {}) {
  setPending(true);
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    render(await response.json());
  } catch (error) {
    console.error(error);
    elements.statusNote.textContent = state.data.ui.status_failed;
  } finally {
    setPending(false);
  }
}

function runAction(action) {
  void postJSON("/api/action", { action });
}

elements.restartButton.addEventListener("click", () => {
  void postJSON("/api/restart");
});

for (const button of elements.langButtons) {
  button.addEventListener("click", () => {
    void postJSON("/api/lang", { lang: button.dataset.lang });
  });
}

render(state.data);
