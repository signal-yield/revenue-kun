/*
 * Browser-side preview + generate UI for revenue-kun's Step 3 Web UI
 * (Issues #81, #82).
 *
 * Scope: file selection, calling the existing POST /api/preview and
 * POST /api/generate endpoints, and rendering their responses. This file
 * must not parse CSV/PDF, compute missing information, or perform any
 * NOI/valuation/Excel-formula calculation -- all of that stays in
 * src/revenue_kun/ and is reused by webui/preview.py and webui/generate.py
 * on the server. See Issue #78 for the approved architecture decision.
 *
 * v0.5.2 product boundary: this file does not collect an optional-income
 * selection, a use-type, an OER, expense amounts, or a cap rate -- none of
 * that is asked for in the Web UI. Recurring income (water/parking/other
 * income) is shown read-only; it is always auto-included in both
 * calculation sheets on the server.
 *
 * Stateless: the same browser-selected File used for preview is resent,
 * unmodified, to /api/generate -- nothing is kept server-side between the
 * two requests.
 */
(function () {
  "use strict";

  var fileInput = document.getElementById("file-input");
  var previewButton = document.getElementById("preview-button");
  var generateButton = document.getElementById("generate-button");
  var errorBox = document.getElementById("error-box");
  var resultsBox = document.getElementById("results-box");
  var summaryBox = document.getElementById("summary-box");
  var rowsTableBody = document.querySelector("#rows-table tbody");
  var missingList = document.getElementById("missing-list");
  var optionalIncomeBox = document.getElementById("optional-income-box");
  var gpiAnnualBox = document.getElementById("gpi-annual-box");

  var OPTIONAL_INCOME_LABELS = {
    water_income: "水道代収入",
    parking_income: "駐車場収入",
    other_income: "その他収入",
  };

  // The browser-selected File is retained here (not just inside the
  // change-event handler) so a future #82 generate action can resend the
  // same file to POST /api/generate without asking the user to re-select it.
  var selectedFile = null;
  var isSubmitting = false;

  function clearChildren(element) {
    while (element.firstChild) {
      element.removeChild(element.firstChild);
    }
  }

  function hide(element) {
    element.hidden = true;
  }

  function show(element) {
    element.hidden = false;
  }

  function resetResults() {
    // Clear only the dynamically populated areas -- resultsBox itself keeps
    // its static structure (headings, table header, generate button).
    clearChildren(summaryBox);
    clearChildren(rowsTableBody);
    clearChildren(missingList);
    clearChildren(optionalIncomeBox);
    clearChildren(gpiAnnualBox);
    hide(resultsBox);
    clearChildren(errorBox);
    hide(errorBox);
    generateButton.disabled = true;
  }

  function showError(message) {
    clearChildren(errorBox);
    var p = document.createElement("p");
    p.textContent = message;
    errorBox.appendChild(p);
    show(errorBox);
    generateButton.disabled = true;
  }

  function formatAmount(value) {
    if (value === null || value === undefined) {
      return "-";
    }
    var num = Number(value);
    if (Number.isNaN(num)) {
      return "-";
    }
    return num.toLocaleString("ja-JP");
  }

  function textOrDash(value) {
    if (value === null || value === undefined || value === "") {
      return "-";
    }
    return String(value);
  }

  function renderSummary(data) {
    clearChildren(summaryBox);
    var statusSummary = data.status_summary || {};
    var lines = [
      "入力形式: " + textOrDash(data.input_type),
      "区画数: " + textOrDash(data.unit_count),
      "稼働: " + textOrDash(statusSummary.occupied) +
        " / 空室: " + textOrDash(statusSummary.vacant) +
        " / 不明: " + textOrDash(statusSummary.unknown),
    ];
    lines.forEach(function (line) {
      var p = document.createElement("p");
      p.textContent = line;
      summaryBox.appendChild(p);
    });
  }

  function renderRows(rows) {
    clearChildren(rowsTableBody);
    (rows || []).forEach(function (row) {
      var tr = document.createElement("tr");
      var values = [
        textOrDash(row.room),
        textOrDash(row.status),
        formatAmount(row.rent),
        formatAmount(row.common_fee),
        formatAmount(row.water_income),
        formatAmount(row.parking_income),
        formatAmount(row.other_income),
      ];
      values.forEach(function (value) {
        var td = document.createElement("td");
        td.textContent = value;
        tr.appendChild(td);
      });
      rowsTableBody.appendChild(tr);
    });
  }

  function renderMissing(missingItems) {
    clearChildren(missingList);
    if (!missingItems || missingItems.length === 0) {
      var none = document.createElement("li");
      none.textContent = "欠損項目はありません。";
      missingList.appendChild(none);
      return;
    }
    missingItems.forEach(function (item) {
      var li = document.createElement("li");
      var severity = textOrDash(item.severity);
      li.className = "severity-" + severity;
      li.textContent = "[" + severity + "] " + textOrDash(item.field) + ": " + textOrDash(item.message);
      missingList.appendChild(li);
    });
  }

  // v0.5.2: read-only display only -- no checkboxes, no selection state.
  // Recurring income is always auto-included in both calculation sheets on
  // the server; this table exists purely to show the user what was
  // extracted and what it adds up to before they download the workbook.
  function renderOptionalIncome(optionalIncome) {
    clearChildren(optionalIncomeBox);
    optionalIncome = optionalIncome || {};

    var table = document.createElement("table");
    var thead = document.createElement("thead");
    var headRow = document.createElement("tr");
    ["項目", "抽出", "月額合計", "年額合計", "GPI算入"].forEach(function (label) {
      var th = document.createElement("th");
      th.textContent = label;
      headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    var tbody = document.createElement("tbody");
    Object.keys(OPTIONAL_INCOME_LABELS).forEach(function (key) {
      var entry = optionalIncome[key] || { present: false, monthly_total: 0, annual_total: 0 };
      var tr = document.createElement("tr");
      var values = [
        OPTIONAL_INCOME_LABELS[key],
        entry.present ? "あり" : "なし",
        formatAmount(entry.monthly_total) + " 円",
        formatAmount(entry.annual_total) + " 円",
        "算入されます",
      ];
      values.forEach(function (value) {
        var td = document.createElement("td");
        td.textContent = value;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    optionalIncomeBox.appendChild(table);
  }

  function renderGpiAnnual(gpiAnnual) {
    clearChildren(gpiAnnualBox);
    var p = document.createElement("p");
    p.textContent = "算入後のGPI（潜在総収入・年額）: " + formatAmount(gpiAnnual) + " 円";
    gpiAnnualBox.appendChild(p);
  }

  function renderPreview(data) {
    renderSummary(data);
    renderRows(data.rows);
    renderMissing(data.missing);
    renderOptionalIncome(data.optional_income);
    renderGpiAnnual(data.gpi_annual);
    show(resultsBox);
    // A successful preview is the only thing that enables Excel generation.
    generateButton.disabled = false;
  }

  fileInput.addEventListener("change", function () {
    selectedFile = fileInput.files && fileInput.files.length > 0 ? fileInput.files[0] : null;
    resetResults();
  });

  previewButton.addEventListener("click", function () {
    if (isSubmitting) {
      return;
    }
    if (!selectedFile) {
      showError("CSVまたはPDFファイルを選択してください。");
      return;
    }

    resetResults();
    isSubmitting = true;
    previewButton.disabled = true;

    var formData = new FormData();
    formData.append("file", selectedFile);

    fetch("/api/preview", { method: "POST", body: formData })
      .then(function (response) {
        return response.json().then(function (data) {
          return { data: data };
        });
      })
      .then(function (result) {
        if (result.data && result.data.ok) {
          renderPreview(result.data);
        } else {
          var message =
            (result.data && result.data.error && result.data.error.message) ||
            "プレビューに失敗しました。";
          showError(message);
        }
      })
      .catch(function () {
        showError("通信エラーが発生しました。しばらくしてから再度お試しください。");
      })
      .finally(function () {
        isSubmitting = false;
        previewButton.disabled = false;
      });
  });

  function downloadWorkbookBlob(blob) {
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = "direct_cap.xlsx";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  generateButton.addEventListener("click", function () {
    if (isSubmitting) {
      return;
    }
    if (!selectedFile) {
      showError("CSVまたはPDFファイルを選択してください。");
      return;
    }

    isSubmitting = true;
    generateButton.disabled = true;

    var formData = new FormData();
    // The same browser-selected File used for preview is resent here,
    // unmodified -- the server re-extracts it from scratch and does not
    // reuse anything from the earlier /api/preview call. Recurring income
    // is always auto-included server-side; there is no selection to send.
    formData.append("file", selectedFile);

    fetch("/api/generate", { method: "POST", body: formData })
      .then(function (response) {
        var contentType = response.headers.get("content-type") || "";
        if (contentType.indexOf("application/json") !== -1) {
          return response.json().then(function (data) {
            var message =
              (data && data.error && data.error.message) || "Excel生成に失敗しました。";
            showError(message);
          });
        }
        return response.blob().then(downloadWorkbookBlob);
      })
      .catch(function () {
        showError("通信エラーが発生しました。しばらくしてから再度お試しください。");
      })
      .finally(function () {
        isSubmitting = false;
        // Re-enable only while the underlying preview is still showing;
        // any failure/new-file-selection path already forces this back to
        // true via resetResults()/showError().
        generateButton.disabled = resultsBox.hidden;
      });
  });
})();
