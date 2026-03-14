const state = {
  datasets: [],
  selectedDataset: null,
  bundle: null,
  activeTab: "cases",
  selectedCaseId: null,
  selectedEdgeId: null,
};

const els = {
  datasetSelect: document.getElementById("datasetSelect"),
  datasetMeta: document.getElementById("datasetMeta"),
  familyFilter: document.getElementById("familyFilter"),
  caseSearch: document.getElementById("caseSearch"),
  caseStatusFilter: document.getElementById("caseStatusFilter"),
  edgeSearch: document.getElementById("edgeSearch"),
  edgeStatusFilter: document.getElementById("edgeStatusFilter"),
  casesList: document.getElementById("casesList"),
  caseDetail: document.getElementById("caseDetail"),
  caseCount: document.getElementById("caseCount"),
  edgesList: document.getElementById("edgesList"),
  edgeDetail: document.getElementById("edgeDetail"),
  edgeCount: document.getElementById("edgeCount"),
  metricCards: document.getElementById("metricCards"),
  evaluationTable: document.getElementById("evaluationTable"),
  worldModelTable: document.getElementById("worldModelTable"),
  divergenceSummary: document.getElementById("divergenceSummary"),
  globalNotes: document.getElementById("globalNotes"),
  saveGlobalNotes: document.getElementById("saveGlobalNotes"),
  resetCaseFilters: document.getElementById("resetCaseFilters"),
  resetEdgeFilters: document.getElementById("resetEdgeFilters"),
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function percent(value) {
  if (value == null || Number.isNaN(value)) return "—";
  return `${Math.round(value * 100)}%`;
}

function fixed(value, digits = 3) {
  if (value == null || Number.isNaN(value)) return "—";
  return Number(value).toFixed(digits);
}

function prettyReviewStatus(status) {
  return {
    unreviewed: "Not reviewed yet",
    accepted: "Looks correct",
    corrected: "Corrected",
    flagged: "Needs discussion",
  }[status] || status;
}

function prettyStance(stance) {
  return {
    recommended: "Recommended",
    excluded: "Not appropriate",
    relative_ci: "Possible with caution",
    uncertain: "Uncertain",
  }[stance] || stance;
}

function collectTreatmentOptions(item) {
  const values = new Set([...(item.expected_recommendations || []), ...(item.expected_excluded || [])]);
  (item.consensus || []).forEach((row) => values.add(row.treatment));
  (item.parsed_runs || []).forEach((run) => (run.stances || []).forEach((stance) => values.add(stance.treatment)));
  return Array.from(values).sort();
}

function consensusSelectionMap(item) {
  const selected = {
    recommended: [],
    excluded: [],
    relative_ci: [],
    uncertain: [],
  };
  (item.consensus || []).forEach((row) => {
    if (row.top_stance && selected[row.top_stance]) {
      selected[row.top_stance].push(row.treatment);
    }
  });
  return selected;
}

function summarySentence(item) {
  const groups = consensusSelectionMap(item);
  const parts = [];
  if (groups.recommended.length) parts.push(`Recommended: ${groups.recommended.join(", ")}`);
  if (groups.excluded.length) parts.push(`Not appropriate: ${groups.excluded.join(", ")}`);
  if (groups.relative_ci.length) parts.push(`Possible with caution: ${groups.relative_ci.join(", ")}`);
  if (groups.uncertain.length) parts.push(`Uncertain: ${groups.uncertain.join(", ")}`);
  return parts.length ? parts.join(" | ") : "No parser summary is available for this case.";
}

function parserState(item) {
  const validation = item.annotation?.parser_validation || {};
  const defaults = consensusSelectionMap(item);
  return {
    verdict: validation.verdict || "",
    recommended: validation.recommended || defaults.recommended,
    excluded: validation.excluded || defaults.excluded,
    relative_ci: validation.relative_ci || defaults.relative_ci,
    uncertain: validation.uncertain || defaults.uncertain,
  };
}

function renderChecklist(title, group, options, selected) {
  return `
    <div class="checklist-card">
      <h4>${title}</h4>
      ${
        options.length
          ? options
              .map(
                (option) => `
            <label class="check-item">
              <input type="checkbox" data-parser-group="${group}" value="${escapeHtml(option)}" ${
                  selected.includes(option) ? "checked" : ""
                } />
              <span>${escapeHtml(option)}</span>
            </label>
          `
              )
              .join("")
          : `<p class="helper-copy">No treatment options available for this case.</p>`
      }
    </div>
  `;
}

function checkedValues(group) {
  return Array.from(document.querySelectorAll(`[data-parser-group="${group}"]:checked`)).map((node) => node.value);
}

async function getJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function toast(message) {
  const node = document.createElement("div");
  node.className = "toast";
  node.textContent = message;
  document.body.appendChild(node);
  setTimeout(() => node.remove(), 2400);
}

function renderDatasetMeta(dataset) {
  if (!dataset) {
    els.datasetMeta.textContent = "";
    return;
  }
  els.datasetMeta.innerHTML = `
    <div>${dataset.models.join(", ")}</div>
    <div>${dataset.n_cases} patient cases · ${dataset.n_runs} parser outputs · ${dataset.n_edges} rule tests</div>
  `;
}

async function loadDatasets() {
  const payload = await getJson("/api/datasets");
  state.datasets = payload.datasets;
  els.datasetSelect.innerHTML = state.datasets
    .map((dataset) => `<option value="${escapeHtml(dataset.name)}">${escapeHtml(dataset.name)}</option>`)
    .join("");
  if (state.datasets.length) {
    state.selectedDataset = state.datasets[0].name;
    els.datasetSelect.value = state.selectedDataset;
    renderDatasetMeta(state.datasets[0]);
    resetCaseFilters();
    resetEdgeFilters();
    await loadBundle();
  }
}

function resetCaseFilters() {
  els.caseSearch.value = "";
  els.familyFilter.value = "";
  els.caseStatusFilter.value = "";
}

function resetEdgeFilters() {
  els.edgeSearch.value = "";
  els.edgeStatusFilter.value = "";
}

function renderFamilyFilter() {
  const families = state.bundle?.dataset?.families ?? [];
  els.familyFilter.innerHTML = `<option value="">All families</option>${families
    .map((family) => `<option value="${escapeHtml(family)}">${escapeHtml(family)}</option>`)
    .join("")}`;
}

async function loadBundle() {
  if (!state.selectedDataset) return;
  const previousCaseId = state.selectedCaseId;
  const previousEdgeId = state.selectedEdgeId;
  try {
    state.bundle = await getJson(`/api/datasets/${encodeURIComponent(state.selectedDataset)}/bundle`);
    state.selectedCaseId =
      state.bundle.cases.find((item) => item.item_id === previousCaseId)?.item_id ?? state.bundle.cases[0]?.item_id ?? null;
    state.selectedEdgeId =
      state.bundle.edges.find((item) => item.edge_id === previousEdgeId)?.edge_id ?? state.bundle.edges[0]?.edge_id ?? null;
    renderFamilyFilter();
    els.globalNotes.value = state.bundle.annotations?.global_notes ?? "";
    renderCaseList();
    renderEdgeList();
    renderEvaluation();
  } catch (error) {
    console.error(error);
    els.casesList.innerHTML = `<div class="empty-list">The dataset could not be loaded.<div class="subtle">${escapeHtml(
      error?.message || "Unknown error"
    )}</div></div>`;
    els.caseDetail.className = "detail-panel empty-state";
    els.caseDetail.textContent = `The dataset could not be loaded: ${error?.message || "Unknown error"}`;
    toast(`Failed to load selected dataset: ${error?.message || "Unknown error"}`);
  }
}

function getFilteredCases() {
  const family = els.familyFilter.value;
  const search = els.caseSearch.value.trim().toLowerCase();
  const status = els.caseStatusFilter.value;
  return (state.bundle?.cases ?? []).filter((item) => {
    if (family && item.family !== family) return false;
    if (status && item.review_status !== status) return false;
    if (!search) return true;
    const haystack = [item.item_id, item.family, item.question, item.type].join(" ").toLowerCase();
    return haystack.includes(search);
  });
}

function renderCaseList() {
  const cases = getFilteredCases();
  els.caseCount.textContent = `${cases.length} shown`;
  if (!cases.length) {
    els.casesList.innerHTML = `
      <div class="empty-list">
        <div>No cases match the current filters.</div>
        <button class="ghost-btn" type="button" data-reset-case-filters="true">Clear filters</button>
      </div>
    `;
    els.caseDetail.className = "detail-panel empty-state";
    els.caseDetail.textContent = "No case matches the current filters.";
    return;
  }
  els.casesList.innerHTML = cases
    .map(
      (item) => `
      <article class="list-item ${item.item_id === state.selectedCaseId ? "active" : ""}" data-case-id="${escapeHtml(item.item_id)}">
        <h3>${escapeHtml(item.item_id)}</h3>
        <div class="meta-row">
          <span class="badge accent">${escapeHtml(item.family)}</span>
          <span class="badge">${escapeHtml(item.type)}</span>
          <span class="badge">${escapeHtml(item.models.join(", "))}</span>
        </div>
        <p class="subtle">${escapeHtml(item.question || "")}</p>
        <div class="pill-row">
          <span class="pill">${item.parsed_runs.length} parsed runs</span>
          <span class="pill">${item.raw_runs.length} raw responses</span>
          <span class="pill">${escapeHtml(prettyReviewStatus(item.review_status))}</span>
        </div>
      </article>
    `
    )
    .join("");
  if (cases.length && !cases.some((item) => item.item_id === state.selectedCaseId)) {
    state.selectedCaseId = cases[0].item_id;
  }
  renderCaseDetail();
}

function consensusMarkup(consensus) {
  if (!consensus.length) return `<p class="subtle">No parsed stances available for this case.</p>`;
  return `
    <table class="stance-table">
      <thead>
        <tr><th>Treatment</th><th>Consensus</th><th>Distribution</th></tr>
      </thead>
      <tbody>
        ${consensus
          .map(
            (row) => `
          <tr>
            <td>${escapeHtml(row.treatment)}</td>
            <td><span class="stance-pill ${escapeHtml(row.top_stance)}">${escapeHtml(prettyStance(row.top_stance || "—"))}</span> ${percent(
              row.top_rate
            )}</td>
            <td>${Object.entries(row.counts)
              .map(([stance, count]) => `${escapeHtml(stance)}: ${count}`)
              .join(" · ")}</td>
          </tr>
        `
          )
          .join("")}
      </tbody>
    </table>
  `;
}

function runMarkup(run) {
  const stances = run.stances || [];
  return `
    <article class="run-card">
      <div class="status-row">
        <span class="badge accent">${escapeHtml(run.model_name)}</span>
        <span class="badge">run ${escapeHtml(run.run_idx)}</span>
        <span class="badge">conditionality ${run.conditionality ? "yes" : "no"}</span>
        <span class="badge">uncertainty ${run.uncertainty ? "yes" : "no"}</span>
      </div>
      <table class="stance-table">
        <thead>
          <tr><th>Treatment</th><th>Stance</th><th>Evidence</th></tr>
        </thead>
        <tbody>
          ${stances
            .map(
              (stance) => `
            <tr>
              <td>${escapeHtml(stance.treatment)}</td>
              <td><span class="stance-pill ${escapeHtml(stance.stance)}">${escapeHtml(prettyStance(stance.stance))}</span></td>
              <td>${escapeHtml(stance.evidence || "")}</td>
            </tr>
          `
            )
            .join("")}
        </tbody>
      </table>
    </article>
  `;
}

function rawMarkup(raw) {
  return `
    <article class="run-card">
      <div class="status-row">
        <span class="badge accent">${escapeHtml(raw.model_name)}</span>
        <span class="badge">run ${escapeHtml(raw.run_idx)}</span>
        <span class="badge">${escapeHtml(raw.item_type || "")}</span>
      </div>
      <details>
        <summary>Phase 1 response</summary>
        <p>${escapeHtml(raw.phase1_response || "")}</p>
      </details>
      <details>
        <summary>Phase 2 response</summary>
        <p>${escapeHtml(raw.phase2_response || "")}</p>
      </details>
    </article>
  `;
}

function renderCaseDetail() {
  const item = (state.bundle?.cases ?? []).find((entry) => entry.item_id === state.selectedCaseId);
  if (!item) {
    els.caseDetail.className = "detail-panel empty-state";
    els.caseDetail.textContent = "Select a case to review automatic parsing and clinician corrections.";
    return;
  }
  const annotation = item.annotation || {};
  const currentStatus = annotation.status || "unreviewed";
  const parserValidation = parserState(item);
  const treatmentOptions = collectTreatmentOptions(item);
  const consensusDefaults = consensusSelectionMap(item);
  els.caseDetail.className = "detail-panel";
  els.caseDetail.innerHTML = `
    <div class="detail-grid">
      <section class="card-block">
        <div class="panel-heading">
          <div>
            <h2>${escapeHtml(item.item_id)}</h2>
            <p class="subtle">${escapeHtml(item.question || "")}</p>
          </div>
          <div class="pill-row">
            <span class="badge accent">${escapeHtml(item.family)}</span>
            <span class="badge">${escapeHtml(item.type)}</span>
            <span class="badge">${escapeHtml(item.models.join(", "))}</span>
          </div>
        </div>
        <p>${escapeHtml(item.clinical_text || "")}</p>
      </section>

      <section class="card-block">
        <div class="panel-heading">
          <h3>Expected Clinical Direction</h3>
        </div>
        <p class="helper-copy">These are the treatment options that the study expects to stay appropriate or become inappropriate for this case.</p>
        <div class="chip-row">
          ${item.expected_recommendations.map((value) => `<span class="badge accent">${escapeHtml(value)}</span>`).join("")}
          ${item.expected_excluded.map((value) => `<span class="badge warn">${escapeHtml(value)}</span>`).join("")}
        </div>
        ${
          item.edge_justification.length
            ? `<div class="pill-row" style="margin-top:12px;">${item.edge_justification
                .map((value) => `<span class="pill">${escapeHtml(value)}</span>`)
                .join("")}</div>`
            : ""
        }
      </section>

      <section class="card-block">
        <div class="panel-heading">
          <h3>What The System Understood</h3>
        </div>
        <p class="helper-copy">This summary combines the parser output across all runs for this case.</p>
        ${consensusMarkup(item.consensus)}
      </section>

      <section class="card-block quick-review-card">
        <div class="panel-heading">
          <h3>Quick Validation</h3>
          <span class="pill">${escapeHtml(prettyReviewStatus(currentStatus))}</span>
        </div>
        <p class="helper-copy">This is the shortest possible workflow: confirm the parser if the summary is clinically acceptable, or open the correction box only when it needs adjustment.</p>
        <div class="snapshot-card">
          <strong>Current parser summary</strong>
          <p>${escapeHtml(summarySentence(item))}</p>
        </div>
        <div class="quick-actions">
          <button class="action-btn" data-quick-case="confirm" data-case-id="${escapeHtml(item.item_id)}">Confirm Parser Summary</button>
          <button class="ghost-btn" data-toggle-correction="true">Correct This Case</button>
          <button class="ghost-btn" data-quick-case="flag" data-case-id="${escapeHtml(item.item_id)}">Mark For Discussion</button>
        </div>
        <details class="correction-panel" ${currentStatus === "corrected" || currentStatus === "flagged" ? "open" : ""}>
          <summary>Open correction box</summary>
          <div class="review-form">
            <p class="helper-copy">Only adjust the final treatment labels. Free-text notes are optional.</p>
            <div class="checklist-grid">
              ${renderChecklist("Recommended", "recommended", treatmentOptions, parserValidation.recommended || consensusDefaults.recommended)}
              ${renderChecklist("Not appropriate", "excluded", treatmentOptions, parserValidation.excluded || consensusDefaults.excluded)}
              ${renderChecklist("Possible with caution", "relative_ci", treatmentOptions, parserValidation.relative_ci || consensusDefaults.relative_ci)}
              ${renderChecklist("Uncertain", "uncertain", treatmentOptions, parserValidation.uncertain || consensusDefaults.uncertain)}
            </div>
            <textarea id="caseNotes" class="notes-area compact" placeholder="Optional short note">${escapeHtml(annotation.notes || "")}</textarea>
            <div class="panel-heading">
              <select id="parserVerdict" class="field compact-select">
                <option value="correct">Correct</option>
                <option value="partly-correct" ${parserValidation.verdict === "partly-correct" ? "selected" : ""}>Partly correct</option>
                <option value="incorrect" ${parserValidation.verdict === "incorrect" ? "selected" : ""}>Incorrect</option>
              </select>
              <button class="action-btn" data-save-case="${escapeHtml(item.item_id)}">Save Correction</button>
            </div>
          </div>
        </details>
      </section>

      <section class="card-block compact-block">
        <div class="panel-heading">
          <h3>Run-By-Run Parser Output</h3>
        </div>
        <details>
          <summary>Show detailed parser output</summary>
          <p class="helper-copy">Open only if the quick summary looks wrong or unclear.</p>
          ${item.parsed_runs.map(runMarkup).join("") || `<p class="subtle">No parsed runs for this item.</p>`}
        </details>
      </section>

      <section class="card-block compact-block">
        <div class="panel-heading">
          <h3>Original Model Responses</h3>
        </div>
        <details>
          <summary>Show original model responses</summary>
          <p class="helper-copy">Use only when you need to verify the parser against the source text.</p>
          ${item.raw_runs.map(rawMarkup).join("") || `<p class="subtle">No raw responses were found for this dataset.</p>`}
        </details>
      </section>
    </div>
  `;
}

function getFilteredEdges() {
  const search = els.edgeSearch.value.trim().toLowerCase();
  const status = els.edgeStatusFilter.value;
  return (state.bundle?.edges ?? []).filter((edge) => {
    if (status && edge.review_status !== status) return false;
    if (!search) return true;
    const haystack = [edge.edge_id, edge.related_items.join(" "), edge.models.join(" ")].join(" ").toLowerCase();
    return haystack.includes(search);
  });
}

function renderEdgeList() {
  const edges = getFilteredEdges();
  els.edgeCount.textContent = `${edges.length} shown`;
  if (!edges.length) {
    els.edgesList.innerHTML = `
      <div class="empty-list">
        <div>No edges match the current filters.</div>
        <button class="ghost-btn" type="button" data-reset-edge-filters="true">Clear filters</button>
      </div>
    `;
    els.edgeDetail.className = "detail-panel empty-state";
    els.edgeDetail.textContent = "No edge matches the current filters.";
    return;
  }
  els.edgesList.innerHTML = edges
    .map(
      (edge) => `
      <article class="list-item ${edge.edge_id === state.selectedEdgeId ? "active" : ""}" data-edge-id="${escapeHtml(edge.edge_id)}">
        <h3>${escapeHtml(edge.edge_id)}</h3>
        <div class="pill-row">
          <span class="pill">${percent(edge.significant_rate)} significant</span>
          <span class="pill">JSD ${fixed(edge.mean_jsd)}</span>
          <span class="pill">${edge.n_tests} tests</span>
          <span class="pill">${escapeHtml(prettyReviewStatus(edge.review_status))}</span>
        </div>
        <p class="subtle">${escapeHtml(edge.related_items.slice(0, 4).join(", "))}</p>
      </article>
    `
    )
    .join("");
  if (edges.length && !edges.some((item) => item.edge_id === state.selectedEdgeId)) {
    state.selectedEdgeId = edges[0].edge_id;
  }
  renderEdgeDetail();
}

function renderEdgeDetail() {
  const edge = (state.bundle?.edges ?? []).find((entry) => entry.edge_id === state.selectedEdgeId);
  if (!edge) {
    els.edgeDetail.className = "detail-panel empty-state";
    els.edgeDetail.textContent = "Select an edge to inspect related perturbations and graph evidence.";
    return;
  }
  const annotation = edge.annotation || {};
  const currentStatus = annotation.status || "unreviewed";
  els.edgeDetail.className = "detail-panel";
  els.edgeDetail.innerHTML = `
    <div class="detail-grid">
      <section class="card-block">
        <div class="panel-heading">
          <div>
            <h2>${escapeHtml(edge.edge_id)}</h2>
            <p class="subtle">${edge.models.map(escapeHtml).join(", ")}</p>
          </div>
          <div class="pill-row">
            <span class="pill">${percent(edge.significant_rate)} significant</span>
            <span class="pill">mean JSD ${fixed(edge.mean_jsd)}</span>
          </div>
        </div>
        <div class="chip-row">
          ${edge.related_items.map((itemId) => `<span class="badge accent">${escapeHtml(itemId)}</span>`).join("")}
        </div>
      </section>

      <section class="card-block review-form">
        <div class="panel-heading">
          <h3>Graph Adjudication</h3>
          <button class="action-btn" data-save-edge="${escapeHtml(edge.edge_id)}">Save Edge Review</button>
        </div>
        <div class="status-row">
          ${["unreviewed", "accepted", "corrected", "flagged"]
            .map(
              (status) => `
            <button class="status-chip ${currentStatus === status ? "active" : ""}" data-edge-status="${escapeHtml(status)}" data-edge-id="${escapeHtml(
                edge.edge_id
              )}" data-status="${escapeHtml(status)}">${escapeHtml(prettyReviewStatus(status))}</button>
          `
            )
            .join("")}
        </div>
        <textarea id="edgeNotes" class="notes-area" placeholder="Clinician note on whether this edge should contribute to KG1/KG2">${escapeHtml(
          annotation.notes || ""
        )}</textarea>
        <textarea id="edgeCorrections" class="notes-area" placeholder="Optional corrected edge interpretation">${escapeHtml(
          annotation.corrections || ""
        )}</textarea>
      </section>

      <section class="card-block">
        <div class="panel-heading">
          <h3>Enhanced Detection Summary</h3>
        </div>
        <table class="metric-table">
          <thead><tr><th>Model</th><th>Detected</th><th>Soft</th><th>Direction</th><th>Rate</th><th>JSD</th></tr></thead>
          <tbody>
            ${Object.entries(edge.enhanced)
              .map(
                ([model, value]) => `
              <tr>
                <td>${escapeHtml(model)}</td>
                <td>${String(value.detected)}</td>
                <td>${String(value.soft_detected)}</td>
                <td>${String(value.direction_correct)}</td>
                <td>${percent(value.detection_rate)}</td>
                <td>${fixed(value.mean_jsd)}</td>
              </tr>
            `
              )
              .join("") || `<tr><td colspan="6">No enhanced edge summary available.</td></tr>`}
          </tbody>
        </table>
      </section>

      <section class="card-block">
        <div class="panel-heading">
          <h3>Supporting Edge Tests</h3>
        </div>
        <table class="metric-table">
          <thead><tr><th>Perturbation</th><th>Model</th><th>Treatment</th><th>Significant</th><th>base→pert</th><th>JSD</th></tr></thead>
          <tbody>
            ${edge.tests
              .map(
                (test) => `
              <tr>
                <td>${escapeHtml(test.pert_id)}</td>
                <td>${escapeHtml(test.model)}</td>
                <td>${escapeHtml(test.treatment)}</td>
                <td>${String(Boolean(test.significant))}</td>
                <td>${percent(test.base_rec_rate)} → ${percent(test.pert_rec_rate)}</td>
                <td>${fixed(test.jsd)}</td>
              </tr>
            `
              )
              .join("")}
          </tbody>
        </table>
      </section>
    </div>
  `;
}

function renderEvaluation() {
  const metrics = state.bundle?.metrics ?? {};
  const world = state.bundle?.world_model_metrics ?? {};
  const graphComparison = state.bundle?.graph_comparison ?? {};
  const divergences = state.bundle?.divergences ?? [];
  const models = Object.keys(metrics);

  els.metricCards.innerHTML = models
    .map((model) => {
      const value = metrics[model];
      return `
        <article class="metric-tile">
          <span class="tiny">${escapeHtml(model)}</span>
          <strong>${percent(value.rec_accuracy)}</strong>
          <div class="subtle">Recommendation agreement</div>
          <div class="tiny" style="margin-top:10px;">Exclusion ${percent(value.exc_accuracy)} · Stability ${percent(value.null_spec)}</div>
        </article>
      `;
    })
    .join("");

  els.evaluationTable.innerHTML = `
    <table class="metric-table">
      <thead>
        <tr><th>Model</th><th>Recommended treatments</th><th>Excluded treatments</th><th>Precision</th><th>Context handling</th><th>Rule-link F1</th></tr>
      </thead>
      <tbody>
        ${models
          .map(
            (model) => `
          <tr>
            <td>${escapeHtml(model)}</td>
            <td>${percent(metrics[model].rec_accuracy)}</td>
            <td>${percent(metrics[model].exc_accuracy)}</td>
            <td>${percent(metrics[model].rec_precision)}</td>
            <td>${percent(metrics[model].cond_rate)}</td>
            <td>${fixed(graphComparison[model]?.f1, 2)}</td>
          </tr>
        `
          )
          .join("")}
      </tbody>
    </table>
  `;

  const worldModels = Object.keys(world);
  els.worldModelTable.innerHTML = worldModels.length
    ? `
      <table class="metric-table">
        <thead>
          <tr><th>Model</th><th>WMS</th><th>Coverage</th><th>Fidelity</th><th>Stability</th><th>Penalty</th></tr>
        </thead>
        <tbody>
          ${worldModels
            .map(
              (model) => `
            <tr>
              <td>${escapeHtml(model)}</td>
              <td>${fixed(world[model].wms, 3)}</td>
              <td>${fixed(world[model].coverage_score, 3)}</td>
              <td>${fixed(world[model].fidelity_score, 3)}</td>
              <td>${fixed(world[model].stability_score, 3)}</td>
              <td>${fixed(world[model].rigidity_penalty, 3)}</td>
            </tr>
          `
            )
            .join("")}
        </tbody>
      </table>
    `
    : `<p class="subtle">World-model metrics are not available for this dataset.</p>`;

  const divergenceCounts = divergences.reduce((acc, row) => {
    acc[row.divergence_type] = (acc[row.divergence_type] || 0) + 1;
    return acc;
  }, {});
  els.divergenceSummary.innerHTML = Object.keys(divergenceCounts).length
    ? `
      <div class="chip-row">
        ${Object.entries(divergenceCounts)
          .map(([key, value]) => `<span class="badge warn">${escapeHtml(key.replaceAll("_", " "))}: ${value}</span>`)
          .join("")}
      </div>
    `
    : `<p class="subtle">No divergence summary available.</p>`;
}

async function saveAnnotation(kind, id, payload) {
  await getJson(`/api/datasets/${encodeURIComponent(state.selectedDataset)}/annotations`, {
    method: "POST",
    body: JSON.stringify({ kind, id, payload }),
  });
  toast("Saved");
  await loadBundle();
}

async function saveGlobalNotes() {
  await getJson(`/api/datasets/${encodeURIComponent(state.selectedDataset)}/annotations`, {
    method: "POST",
    body: JSON.stringify({ kind: "global", notes: els.globalNotes.value }),
  });
  toast("Global notes saved");
  await loadBundle();
}

function bindEvents() {
  els.datasetSelect.addEventListener("change", async (event) => {
    state.selectedDataset = event.target.value;
    const dataset = state.datasets.find((entry) => entry.name === state.selectedDataset);
    renderDatasetMeta(dataset);
    resetCaseFilters();
    resetEdgeFilters();
    await loadBundle();
  });

  document.querySelectorAll(".nav-tab").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".nav-tab").forEach((tab) => tab.classList.remove("active"));
      button.classList.add("active");
      state.activeTab = button.dataset.tab;
      document.querySelectorAll(".tab-pane").forEach((pane) => pane.classList.remove("active"));
      document.querySelectorAll(".filters").forEach((pane) => pane.classList.remove("active"));
      document.getElementById(`${button.dataset.tab}Tab`).classList.add("active");
      if (button.dataset.tab === "cases") document.getElementById("casesFilters").classList.add("active");
      if (button.dataset.tab === "edges") document.getElementById("edgesFilters").classList.add("active");
    });
  });

  [els.familyFilter, els.caseSearch, els.caseStatusFilter].forEach((el) => el.addEventListener("input", renderCaseList));
  [els.edgeSearch, els.edgeStatusFilter].forEach((el) => el.addEventListener("input", renderEdgeList));

  els.casesList.addEventListener("click", (event) => {
    if (event.target.closest("[data-reset-case-filters]")) {
      resetCaseFilters();
      renderCaseList();
      return;
    }
    const card = event.target.closest("[data-case-id]");
    if (!card) return;
    state.selectedCaseId = card.dataset.caseId;
    renderCaseList();
  });

  els.edgesList.addEventListener("click", (event) => {
    if (event.target.closest("[data-reset-edge-filters]")) {
      resetEdgeFilters();
      renderEdgeList();
      return;
    }
    const card = event.target.closest("[data-edge-id]");
    if (!card) return;
    state.selectedEdgeId = card.dataset.edgeId;
    renderEdgeList();
  });

  els.caseDetail.addEventListener("click", async (event) => {
    const quickButton = event.target.closest("[data-quick-case]");
    if (quickButton) {
      const item = (state.bundle?.cases ?? []).find((entry) => entry.item_id === quickButton.dataset.caseId);
      if (!item) return;
      const defaults = consensusSelectionMap(item);
      if (quickButton.dataset.quickCase === "confirm") {
        await saveAnnotation("cases", quickButton.dataset.caseId, {
          status: "accepted",
          notes: item.annotation?.notes || "",
          corrections: "",
          parser_validation: {
            verdict: "correct",
            recommended: defaults.recommended,
            excluded: defaults.excluded,
            relative_ci: defaults.relative_ci,
            uncertain: defaults.uncertain,
          },
        });
        return;
      }
      if (quickButton.dataset.quickCase === "flag") {
        await saveAnnotation("cases", quickButton.dataset.caseId, {
          status: "flagged",
          notes: item.annotation?.notes || "",
          corrections: "",
          parser_validation: {
            verdict: "incorrect",
            recommended: checkedValues("recommended"),
            excluded: checkedValues("excluded"),
            relative_ci: checkedValues("relative_ci"),
            uncertain: checkedValues("uncertain"),
          },
        });
        return;
      }
    }

    const correctionToggle = event.target.closest("[data-toggle-correction]");
    if (correctionToggle) {
      const details = els.caseDetail.querySelector(".correction-panel");
      if (details) details.open = true;
      return;
    }

    const statusButton = event.target.closest("[data-case-status]");
    if (statusButton) {
      document.querySelectorAll("[data-case-status]").forEach((button) => button.classList.remove("active"));
      statusButton.classList.add("active");
      return;
    }

    const saveButton = event.target.closest("[data-save-case]");
    if (saveButton) {
      await saveAnnotation("cases", saveButton.dataset.saveCase, {
        status: "corrected",
        notes: document.getElementById("caseNotes").value,
        corrections: "",
        parser_validation: {
          verdict: document.getElementById("parserVerdict").value,
          recommended: checkedValues("recommended"),
          excluded: checkedValues("excluded"),
          relative_ci: checkedValues("relative_ci"),
          uncertain: checkedValues("uncertain"),
        },
      });
    }
  });

  els.edgeDetail.addEventListener("click", async (event) => {
    const statusButton = event.target.closest("[data-edge-status]");
    if (statusButton) {
      document.querySelectorAll("[data-edge-status]").forEach((button) => button.classList.remove("active"));
      statusButton.classList.add("active");
      return;
    }

    const saveButton = event.target.closest("[data-save-edge]");
    if (saveButton) {
      const activeStatus = document.querySelector("[data-edge-status].active")?.dataset.edgeStatus || "unreviewed";
      await saveAnnotation("edges", saveButton.dataset.saveEdge, {
        status: activeStatus,
        notes: document.getElementById("edgeNotes").value,
        corrections: document.getElementById("edgeCorrections").value,
      });
    }
  });

  els.saveGlobalNotes.addEventListener("click", saveGlobalNotes);
  els.resetCaseFilters.addEventListener("click", () => {
    resetCaseFilters();
    renderCaseList();
  });
  els.resetEdgeFilters.addEventListener("click", () => {
    resetEdgeFilters();
    renderEdgeList();
  });
}

bindEvents();
loadDatasets().catch((error) => {
  console.error(error);
  toast("Failed to load datasets");
});
