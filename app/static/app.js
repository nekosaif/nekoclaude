/* Global HTMX error visibility: surface any 4xx/5xx as a toast. */
document.addEventListener("htmx:responseError", e => {
  const xhr = e.detail.xhr;
  const text = (xhr.responseText || "").trim();
  const msg = text.length > 0 ? text.slice(0, 400) : `HTTP ${xhr.status}`;
  showToast(`Request failed: ${msg}`, "error");
});
document.addEventListener("htmx:sendError", () => {
  showToast("Network error: server unreachable", "error");
});
document.addEventListener("htmx:swapError", e => {
  showToast(`Swap error: ${e.detail.error || "unknown"}`, "error");
});

function showToast(message, kind = "info") {
  const host = document.getElementById("global-error");
  if (!host) return;
  const div = document.createElement("div");
  const bg = kind === "error"
    ? "bg-rose-900/80 border-rose-700 text-rose-100"
    : "bg-emerald-900/80 border-emerald-700 text-emerald-100";
  div.className = `${bg} border rounded p-2 text-xs shadow-lg cursor-pointer`;
  div.textContent = message;
  div.addEventListener("click", () => div.remove());
  host.appendChild(div);
  setTimeout(() => div.remove(), 6000);
}

/* Alpine app state: target selection + helpers to add ops to the cart. */

function ncApp() {
  return {
    selectedTargets: [],

    init() {
      // restore selection from localStorage
      try {
        const saved = JSON.parse(localStorage.getItem("nc.selectedTargets") || "[]");
        if (Array.isArray(saved)) this.selectedTargets = saved;
      } catch {}
      this.$watch("selectedTargets", v => {
        localStorage.setItem("nc.selectedTargets", JSON.stringify(v));
        this._refreshInstalled();
        this._refreshHistory();
      });
      // first render
      this._refreshInstalled();
      this._refreshHistory();
    },

    toggleTarget(id) {
      const i = this.selectedTargets.indexOf(id);
      if (i >= 0) this.selectedTargets.splice(i, 1);
      else this.selectedTargets.push(id);
    },

    isSelected(id) {
      return this.selectedTargets.includes(id);
    },

    _firstSelected() {
      return this.selectedTargets[0] || null;
    },

    _refreshInstalled() {
      const tid = this._firstSelected();
      const panel = document.getElementById("installed-panel");
      if (!panel) return;
      if (!tid) {
        panel.innerHTML = '<p class="text-xs text-slate-500">Select a target on the left.</p>';
        return;
      }
      htmx.ajax("GET", `/installed/${tid}`, { target: "#installed-panel", swap: "innerHTML" });
    },

    _refreshHistory() {
      const tid = this._firstSelected();
      const panel = document.getElementById("history-panel");
      if (!panel) return;
      if (!tid) {
        panel.innerHTML = '<p class="text-xs text-slate-500">Select a target on the left.</p>';
        return;
      }
      htmx.ajax("GET", `/history/${tid}`, { target: "#history-panel", swap: "innerHTML" });
    },

    // Send a staged op via fetch. Catalog buttons call these.
    async stage(kind, payload) {
      if (!this.selectedTargets.length) {
        alert("Select at least one target first.");
        return;
      }
      const fd = new FormData();
      fd.append("kind", kind);
      fd.append("payload", JSON.stringify(payload || {}));
      for (const t of this.selectedTargets) fd.append("target_ids", t);
      const res = await fetch("/stage/add", { method: "POST", body: fd });
      if (!res.ok) {
        const text = await res.text();
        alert("stage failed: " + text);
        return;
      }
      htmx.trigger("body", "cart:refresh");
    },
  };
}
