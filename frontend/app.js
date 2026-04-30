(() => {
  "use strict";

  const API_BASE = "";

  const sel1      = document.getElementById("currency1");
  const sel2      = document.getElementById("currency2");
  const amountIn  = document.getElementById("amount");
  const amountOut = document.getElementById("convertedAmount");
  const convertBtn= document.getElementById("convertBtn");
  const swapBtn   = document.getElementById("swapBtn");
  const errorMsg  = document.getElementById("errorMsg");
  const resultLabel     = document.getElementById("resultLabel");
  const resultRate      = document.getElementById("resultRate");
  const resultTimestamp = document.getElementById("resultTimestamp");
  const tableBody       = document.getElementById("currencyTableBody");

  let currencyMap = {};

  // ── Boot ──────────────────────────────────────────────────────────────────
  async function init() {
    try {
      const resp = await fetch(`${API_BASE}/currency`);
      if (!resp.ok) throw new Error("Failed to load currencies.");
      currencyMap = await resp.json();
      populateDropdowns();
      populateTable();
    } catch (err) {
      showError(err.message);
    }
  }

  // ── Dropdown population ───────────────────────────────────────────────────
  function buildOptions(codes, exclude = null) {
    return codes
      .filter(c => c !== exclude)
      .map(c => {
        const opt = document.createElement("option");
        opt.value = c;
        opt.textContent = `${c} – ${currencyMap[c].currencyName}`;
        return opt;
      });
  }

  function populateDropdowns() {
    const codes = Object.keys(currencyMap).sort();

    const placeholder1 = new Option("-- Select --", "");
    const placeholder2 = new Option("-- Select --", "");

    sel1.innerHTML = "";
    sel2.innerHTML = "";

    sel1.appendChild(placeholder1);
    sel2.appendChild(placeholder2);

    buildOptions(codes).forEach(o => sel1.appendChild(o));
    buildOptions(codes).forEach(o => sel2.appendChild(o));
  }

  function refreshCurrency2() {
    const selected1 = sel1.value;
    const selected2 = sel2.value;
    const codes     = Object.keys(currencyMap).sort();

    sel2.innerHTML = "";
    const ph = new Option("-- Select --", "");
    sel2.appendChild(ph);

    buildOptions(codes, selected1).forEach(o => sel2.appendChild(o));

    if (selected2 && selected2 !== selected1) {
      sel2.value = selected2;
    }

    toggleConvertButton();
  }

  function toggleConvertButton() {
    convertBtn.disabled = !(sel1.value && sel2.value);
  }

  // ── Table ─────────────────────────────────────────────────────────────────
  function populateTable() {
    tableBody.innerHTML = "";
    Object.values(currencyMap)
      .sort((a, b) => a.currencyCode.localeCompare(b.currencyCode))
      .forEach(({ currencyCode, currencyName, countryName }) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${currencyCode}</td><td>${currencyName}</td><td>${countryName}</td>`;
        tableBody.appendChild(tr);
      });
  }

  // ── Conversion ────────────────────────────────────────────────────────────
  async function convert() {
    clearError();
    const from   = sel1.value;
    const to     = sel2.value;
    const amount = parseFloat(amountIn.value);

    if (!from || !to) { showError("Please select both currencies."); return; }
    if (isNaN(amount) || amount <= 0) { showError("Please enter a valid positive amount."); return; }

    resultRate.innerHTML = '<span class="spinner"></span>';
    resultLabel.textContent = "Fetching exchange rate…";
    resultTimestamp.textContent = "";
    amountOut.value = "";

    try {
      const resp = await fetch(`${API_BASE}/exchange-rate/${from}/${to}`);
      const data = await resp.json();

      if (!resp.ok) {
        showError(data.error || "Could not retrieve exchange rate.");
        resultRate.textContent = "";
        resultLabel.textContent = "Select currencies to see the exchange rate";
        return;
      }

      const rate      = parseFloat(data.exchangeRate);
      const converted = (amount * rate).toFixed(4);
      const fromName  = currencyMap[from]?.currencyName || from;
      const toName    = currencyMap[to]?.currencyName   || to;

      resultLabel.textContent = `${amount} ${fromName} equals`;
      resultRate.textContent  = `${converted} ${toName}`;
      amountOut.value         = converted;

      const now = new Date();
      resultTimestamp.textContent =
        `${now.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" })}, ` +
        `${now.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })} UTC · Rate: 1 ${from} = ${rate} ${to}`;
    } catch {
      showError("Network error. Is the Flask server running?");
      resultRate.textContent  = "";
      resultLabel.textContent = "Select currencies to see the exchange rate";
    }
  }

  // ── Swap ──────────────────────────────────────────────────────────────────
  function swap() {
    const v1 = sel1.value;
    const v2 = sel2.value;
    if (!v1 || !v2) return;

    sel1.value = v2;
    refreshCurrency2();
    sel2.value = v1;
    toggleConvertButton();
    clearError();
    amountOut.value = "";
    resultRate.textContent  = "";
    resultLabel.textContent = "Select currencies to see the exchange rate";
    resultTimestamp.textContent = "";
  }

  // ── Helpers ───────────────────────────────────────────────────────────────
  function showError(msg) { errorMsg.textContent = msg; }
  function clearError()   { errorMsg.textContent = ""; }

  // ── Event Listeners ───────────────────────────────────────────────────────
  sel1.addEventListener("change", () => {
    refreshCurrency2();
    clearError();
    amountOut.value = "";
    resultRate.textContent  = "";
    resultLabel.textContent = "Select currencies to see the exchange rate";
    resultTimestamp.textContent = "";
  });

  sel2.addEventListener("change", () => {
    toggleConvertButton();
    clearError();
  });

  convertBtn.addEventListener("click", convert);
  swapBtn.addEventListener("click", swap);

  amountIn.addEventListener("keydown", e => { if (e.key === "Enter") convert(); });

  init();
})();
