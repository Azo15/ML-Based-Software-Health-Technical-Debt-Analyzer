"use strict";
const $ = (id) => document.getElementById(id);
const states = {
  queued: "Sırada",
  running: "Analiz sürüyor",
  succeeded: "Tamamlandı",
  failed: "Tamamlanamadı",
};
const stages = {
  validating: "Proje kontrol ediliyor",
  mining: "Git geçmişi inceleniyor",
  historical_metrics: "Geçmiş ölçümler hesaplanıyor",
  training: "Model değerlendiriliyor",
  current_files: "Mevcut dosyalar inceleniyor",
  completed: "Analiz tamamlandı",
};
const reasons = {
  environment_directory: "Sanal ortam dosyası",
  excluded_by_filter: "Seçtiğin filtreyle hariç tutuldu",
  outside_repository: "Proje dışında",
  missing_file: "Dosya bulunamadı",
  unreadable_file: "Dosya okunamadı",
  empty_file: "Boş dosya",
  invalid_python: "Python sözdizimi geçersiz",
};
const errors = {
  empty_history:
    "Bu Git deposunda henüz commit yok. Önce ilk commit’i oluşturup yeniden dene.",
  missing_repository: "Proje klasörü bulunamadı. Tam klasör yolunu kontrol et.",
  git_error: "Bu klasör bir Git deposu değil veya Git tarafından okunamıyor.",
  repository_root_required: "Git deposunun ana klasörünü seç.",
  history_failed: "Projenin Git geçmişi okunamadı.",
  interrupted:
    "Uygulama kapandığı için analiz yarıda kaldı. Yeniden başlatabilirsin.",
  internal_error:
    "Analiz sırasında beklenmeyen bir hata oluştu. Yeniden deneyebilirsin.",
};
let currentId = null,
  viewVersion = 0,
  pollTimer = null,
  files = [];
function text(id, value) {
  $(id).textContent = value;
}
function projectName(path) {
  return path.replace(/\\/g, "/").replace(/\/$/, "").split("/").pop() || path;
}
async function api(url, options) {
  let response;
  try {
    response = await fetch(url, options);
  } catch {
    throw new Error(
      "Uygulamaya ulaşılamıyor. Yerel servisin çalıştığını kontrol edip yeniden dene.",
    );
  }
  const body = await response.json();
  if (!response.ok)
    throw new Error(
      response.status === 429
        ? "Analiz kuyruğu dolu. Bir analiz tamamlanınca yeniden dene."
        : response.status === 422
          ? "Analiz seçeneklerini kontrol et."
          : typeof body.detail === "string"
            ? body.detail
            : "İşlem tamamlanamadı.",
    );
  return body;
}
function showError(error) {
  text("form-error", error.message);
  $("form-error").hidden = false;
}
function renderHistory(jobs) {
  $("history").replaceChildren();
  if (!jobs.length) {
    const p = document.createElement("p");
    p.className = "muted";
    p.textContent = "Henüz analiz yok.";
    $("history").append(p);
  }
  for (const job of jobs) {
    const button = document.createElement("button");
    button.className = job.id === currentId ? "active" : "";
    const name = document.createElement("strong");
    name.textContent = projectName(job.payload.repo_path || "Proje");
    const detail = document.createElement("small");
    detail.textContent = `${states[job.state] || job.state} · ${new Date(job.created).toLocaleDateString("tr-TR")}`;
    button.append(name, detail);
    button.addEventListener("click", () => selectJob(job.id));
    $("history").append(button);
  }
}
async function refreshHistory() {
  const jobs = await api("/api/scans");
  renderHistory(jobs);
  return jobs;
}
async function selectJob(id) {
  currentId = id;
  const version = ++viewVersion;
  clearTimeout(pollTimer);
  history.replaceState(null, "", `#scan=${encodeURIComponent(id)}`);
  $("results").hidden = true;
  $("welcome").hidden = true;
  $("job-panel").hidden = false;
  $("form-error").hidden = true;
  text("job-title", "Analiz yükleniyor…");
  text("job-state", "Yükleniyor");
  text("job-description", "");
  $("job-progress").hidden = false;
  $("job-progress").removeAttribute("value");
  async function poll() {
    try {
      const job = await api(`/api/scans/${encodeURIComponent(id)}`);
      if (version !== viewVersion) return;
      text("job-title", projectName(job.payload.repo_path));
      text("job-state", states[job.state]);
      const p = job.progress;
      text(
        "job-description",
        job.state === "failed"
          ? errors[job.error?.code] ||
              job.error?.message ||
              "Analiz tamamlanamadı."
          : job.state === "queued"
            ? "Sıradaki analiz bekleniyor."
            : (stages[p?.stage] || "Analiz hazırlanıyor…") +
              (p?.total ? ` · ${p.completed} / ${p.total}` : ""),
      );
      $("job-progress").hidden = ["failed", "succeeded"].includes(job.state);
      if (p?.total) {
        $("job-progress").max = p.total;
        $("job-progress").value = p.completed;
      } else $("job-progress").removeAttribute("value");
      if (job.state === "succeeded") {
        const report = await api(`/api/scans/${id}/report`);
        if (version !== viewVersion) return;
        renderReport(report, job);
        await refreshHistory();
      } else if (job.state === "failed") await refreshHistory();
      else pollTimer = setTimeout(poll, 1200);
    } catch (error) {
      if (version === viewVersion) {
        showError(error);
        $("job-progress").hidden = true;
      }
    }
  }
  await poll();
}
function renderReport(report, job) {
  files = report.files || [];
  $("results").hidden = false;
  $("search").value = "";
  text("project-name", projectName(report.repository || job.payload.repo_path));
  const status = {
    complete: "Analiz tamamlandı",
    partial: "Bazı dosyalar incelenemedi",
    empty: "İncelenecek dosya bulunamadı",
  };
  text(
    "scan-info",
    `${status[report.status] || "Analiz tamamlandı"} · ${new Date(job.created).toLocaleString("tr-TR")}`,
  );
  text("file-count", files.length);
  text(
    "finding-count",
    files.reduce(
      (n, file) => n + file.result.maintainability_findings.length,
      0,
    ),
  );
  text("skip-count", report.skipped_files?.length || 0);
  text(
    "model-notice",
    report.evaluation_details?.status === "evaluated"
      ? "Risk sıralaması deneyseldir; hata olasılığı veya teknik borç süresi değildir. Bakım bulguları ayrı kurallarla değerlendirilir."
      : "Bu analizde risk modeli için yeterli ve çeşitli veri bulunamadı. Bakım bulgularını ve dosya ölçümlerini inceleyebilirsin.",
  );
  $("json-download").href = `/api/scans/${job.id}/report?format=json`;
  $("csv-download").href = `/api/scans/${job.id}/report?format=csv`;
  $("skipped-list").replaceChildren();
  for (const item of report.skipped_files || []) {
    const li = document.createElement("li");
    li.textContent = `${item.path} — ${reasons[item.reason] || item.reason}`;
    $("skipped-list").append(li);
  }
  if (!report.skipped_files?.length) {
    const li = document.createElement("li");
    li.textContent = "Atlanan dosya yok.";
    $("skipped-list").append(li);
  }
  text("evaluation", report.model_evaluation || "Değerlendirme bulunmuyor.");
  renderFiles();
}
function renderFiles() {
  const query = $("search").value.toLocaleLowerCase("tr-TR");
  const selected = files.filter((file) =>
    file.path.toLocaleLowerCase("tr-TR").includes(query),
  );
  $("file-rows").replaceChildren();
  $("empty-files").hidden = selected.length > 0;
  for (const file of selected) {
    const row = document.createElement("tr"),
      cell = document.createElement("td"),
      button = document.createElement("button");
    button.className = "file-button";
    button.textContent = file.path;
    button.addEventListener("click", () => openFile(file));
    cell.append(button);
    row.append(cell);
    const values = [
      file.result.risk_score == null
        ? "Hesaplanamadı"
        : Number(file.result.risk_score).toFixed(3),
      file.metrics.loc,
      file.metrics.cyclomatic_complexity_max,
      file.result.maintainability_findings.length,
    ];
    for (const value of values) {
      const td = document.createElement("td");
      td.textContent = value;
      row.append(td);
    }
    $("file-rows").append(row);
  }
}
function openFile(file) {
  text("detail-path", file.path);
  text(
    "detail-metrics",
    `${file.metrics.loc} kod satırı · En yüksek karmaşıklık: ${file.metrics.cyclomatic_complexity_max} · Fonksiyon sayısı: ${file.metrics.num_functions ?? "—"}`,
  );
  $("detail-findings").replaceChildren();
  const translations = {
    complex_function: [
      "Karmaşık fonksiyon",
      "Dallanma sayısı yüksek. Fonksiyonu testlerle birlikte daha küçük, anlamlı adımlara ayırmayı değerlendir.",
    ],
    large_file: [
      "Büyük dosya",
      "Dosyanın farklı sorumluluklarını daha küçük modüllere ayırmayı değerlendir.",
    ],
    dense_expressions: [
      "Yoğun ifadeler",
      "Karmaşık ifadeleri sadeleştir; ara sonuçlara anlamlı isimler ver.",
    ],
  };
  for (const finding of file.result.maintainability_findings) {
    const box = document.createElement("div");
    box.className = "finding";
    const title = document.createElement("strong"),
      p = document.createElement("p");
    title.textContent = translations[finding.rule]?.[0] || finding.rule;
    p.textContent = translations[finding.rule]?.[1] || finding.suggestion;
    box.append(title, p);
    const evidence = document.createElement("p");
    evidence.textContent = finding.reason;
    box.append(evidence);
    $("detail-findings").append(box);
  }
  if (!file.result.maintainability_findings.length) {
    const p = document.createElement("p");
    p.textContent = "Bu dosyada mevcut kurallara göre bakım bulgusu yok.";
    $("detail-findings").append(p);
  }
  $("file-dialog").showModal();
}
$("close-dialog").addEventListener("click", () => $("file-dialog").close());
$("search").addEventListener("input", renderFiles);
$("refresh").addEventListener("click", async () => {
  try {
    await refreshHistory();
    if (currentId) await selectJob(currentId);
  } catch (e) {
    showError(e);
  }
});
$("scan-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("form-error").hidden = true;
  $("start").disabled = true;
  try {
    const repo = $("repo").value.trim();
    if (!repo) throw new Error("Lütfen proje klasörünün tam yolunu gir.");
    const data = await api("/api/scans", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        repo_path: repo,
        max_commits: Number($("commits").value),
        observation_commits: Number($("window").value),
        excludes: $("excludes")
          .value.split(",")
          .map((x) => x.trim())
          .filter(Boolean),
      }),
    });
    await selectJob(data.id);
    await refreshHistory();
  } catch (error) {
    showError(error);
  } finally {
    $("start").disabled = false;
  }
});
(async () => {
  try {
    const jobs = await refreshHistory();
    if (jobs.length) $("repo").value = jobs[0].payload.repo_path;
    const match = location.hash.match(/^#scan=([a-f0-9]{32})$/);
    if (match) await selectJob(match[1]);
  } catch (error) {
    showError(error);
  }
})();
