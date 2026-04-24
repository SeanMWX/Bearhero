const state = {
  data: window.BEAHERO_INITIAL_STATE,
  pending: false,
};

const elements = {
  roomTitle: document.getElementById("room-title"),
  roomDescription: document.getElementById("room-description"),
  roomHint: document.getElementById("room-hint"),
  mapText: document.getElementById("map-text"),
  statsList: document.getElementById("stats-list"),
  winNote: document.getElementById("win-note"),
  actionsHeading: document.getElementById("actions-heading"),
  actionsList: document.getElementById("actions-list"),
  logList: document.getElementById("log-list"),
  restartButton: document.getElementById("restart-button"),
  statusNote: document.getElementById("status-note"),
};

function setPending(pending) {
  state.pending = pending;
  elements.restartButton.disabled = pending;
  elements.statusNote.textContent = pending ? "Updating..." : "";
  for (const button of elements.actionsList.querySelectorAll("button")) {
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
  elements.roomTitle.textContent = nextState.room.title;
  elements.roomDescription.textContent = nextState.room.description;
  elements.roomHint.textContent = nextState.room.action_text;
  elements.mapText.textContent = nextState.map_text;
  elements.actionsHeading.textContent = nextState.won ? "Aftermath" : "Actions";
  renderStats(nextState.stats);
  renderActions(nextState.actions);
  renderLog(nextState.log);

  if (nextState.won) {
    elements.winNote.hidden = false;
    elements.winNote.textContent = "You brought something back from the dark. That is enough for day one.";
  } else {
    elements.winNote.hidden = true;
    elements.winNote.textContent = "";
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
    elements.statusNote.textContent = "Request failed. Try again.";
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

render(state.data);
