/*
 * Browser-side preview UI for revenue-kun's Step 3 Web UI (Issue #81).
 *
 * Scope: file selection, calling the existing POST /api/preview endpoint,
 * and rendering its JSON response. This file must not parse CSV/PDF,
 * compute missing information, decide optional-income GPI inclusion, or
 * perform any NOI/valuation/Excel-formula calculation -- all of that
 * stays in src/revenue_kun/ and is reused by webui/preview.py on the
 * server. See Issue #78 for the approved architecture decision.
 *
 * The generate/download action is intentionally always disabled here;
 * POST /api/generate and Excel generation are implemented in Issue #82.
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

  function renderOptionalIncome(optionalIncome) {
    clearChildren(optionalIncomeBox);
    optionalIncome = optionalIncome || {};
    Object.keys(OPTIONAL_INCOME_LABELS).forEach(function (key) {
      var entry = optionalIncome[key] || { present: false, total: 0 };

      var wrapper = document.createElement("div");
      wrapper.className = "optional-income-row";

      var label = document.createElement("label");

      var checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = false; // always unchecked by default, regardless of extracted data
      checkbox.disabled = !entry.present;
      checkbox.className = "optional-income-checkbox";
      checkbox.setAttribute("data-optional-income-key", key);

      label.appendChild(checkbox);

      var text = document.createElement("span");
      text.textContent =
        " " + OPTIONAL_INCOME_LABELS[key] +
        "（抽出: " + (entry.present ? "あり" : "なし") +
        " / 合計: " + formatAmount(entry.total) + " 円）";
      label.appendChild(text);

      wrapper.appendChild(label);
      optionalIncomeBox.appendChild(wrapper);
    });
  }

  // Exposed for a future #82 generate action; reading the current
  // selections here does not decide GPI inclusion by itself.
  function getSelectedOptionalIncomeKeys() {
    var checkboxes = optionalIncomeBox.querySelectorAll(".optional-income-checkbox");
    var keys = [];
    for (var i = 0; i < checkboxes.length; i += 1) {
      if (checkboxes[i].checked) {
        keys.push(checkboxes[i].getAttribute("data-optional-income-key"));
      }
    }
    return keys;
  }
  window.revenueKunGetSelectedOptionalIncomeKeys = getSelectedOptionalIncomeKeys;

  function renderPreview(data) {
    renderSummary(data);
    renderRows(data.rows);
    renderMissing(data.missing);
    renderOptionalIncome(data.optional_income);
    show(resultsBox);
    // Excel generation belongs to #82; this action stays disabled here
    // regardless of whether the preview succeeded.
    generateButton.disabled = true;
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
})();
