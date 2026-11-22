(() => {
    const body = document.body;
    const api = {
        status: body.dataset.statusUrl,
        temperature: body.dataset.temperatureUrl,
        temperatureHistory: `${body.dataset.temperatureHistoryUrl}?page_size=100`,
        jobs: `${body.dataset.jobsUrl}?page_size=10`,
    };
    const pollInterval = Number(body.dataset.pollInterval) || 15000;
    const $ = (id) => document.getElementById(id);
    const alertBox = $("api-alert");
    const refreshState = $("refresh-state");
    let refreshing = false;
    let nextJobsUrl = null;
    let currentJobPage = 1;
    let totalJobs = 0;
    let nozzleChart;
    let bedChart;

    $("poll-label").textContent = String(Math.round(pollInterval / 1000));

    async function getJson(url) {
        const response = await fetch(url, {
            headers: { Accept: "application/json" },
            credentials: "same-origin",
        });
        if (!response.ok) throw new Error(`API respondeu ${response.status}`);
        return response.json();
    }

    function setText(id, value, fallback = "—") {
        $(id).textContent = value === null || value === undefined || value === "" ? fallback : value;
    }

    function formatNumber(value) {
        if (value === null || value === undefined || value === "") return "—";
        return new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(Number(value));
    }

    function formatDuration(seconds) {
        if (seconds === null || seconds === undefined || Number.isNaN(Number(seconds))) return "—";
        const totalMinutes = Math.max(0, Math.floor(Number(seconds) / 60));
        const days = Math.floor(totalMinutes / 1440);
        const hours = Math.floor((totalMinutes % 1440) / 60);
        const minutes = totalMinutes % 60;
        if (days) return `${days}d ${hours}h`;
        if (hours) return `${hours}h ${minutes}m`;
        return `${minutes} min`;
    }

    function formatDate(value) {
        if (!value) return "—";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return "—";
        return new Intl.DateTimeFormat("pt-BR", {
            day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit",
        }).format(date);
    }

    function updateConnection(status) {
        const indicator = $("connection-indicator");
        const inlineDot = $("status-dot-inline");
        const operational = status?.flags?.operational;
        indicator.classList.remove("is-online", "is-offline", "is-unknown");
        inlineDot.classList.remove("is-online", "is-offline");
        if (operational === true) {
            indicator.classList.add("is-online");
            inlineDot.classList.add("is-online");
            setText("connection-label", "Conectada");
            setText("status-foot-label", "OctoPrint operacional");
            setText("connection-detail", "Impressora operacional");
        } else if (operational === false) {
            indicator.classList.add("is-offline");
            inlineDot.classList.add("is-offline");
            setText("connection-label", "Desconectada");
            setText("status-foot-label", "Impressora não operacional");
            setText("connection-detail", "Verifique a conexão com a impressora");
        } else {
            indicator.classList.add("is-unknown");
            setText("connection-label", "Sem dados");
            setText("status-foot-label", "Sem dados de conexão");
            setText("connection-detail", "Estado reportado pelo monitoramento");
        }
    }

    function updateStatus(payload) {
        const status = payload?.data;
        if (!status) {
            setText("printer-state", "Sem leitura");
            updateConnection(null);
            return;
        }
        setText("printer-state", status.state, "Desconhecido");
        updateConnection(status);
    }

    function updateTemperature(payload) {
        const temperature = payload?.data;
        if (!temperature) {
            ["nozzle-actual", "nozzle-target", "bed-actual", "bed-target"].forEach((id) => setText(id, null));
            return;
        }
        setText("nozzle-actual", formatNumber(temperature.nozzle_actual));
        setText("nozzle-target", formatNumber(temperature.nozzle_target));
        setText("bed-actual", formatNumber(temperature.bed_actual));
        setText("bed-target", formatNumber(temperature.bed_target));
    }

    function updateChart(existingChart, canvasId, labels, current, target, currentColor) {
        if (typeof Chart === "undefined") {
            $(`${canvasId}-unavailable`).hidden = false;
            $(canvasId).hidden = true;
            return existingChart;
        }
        const context = $(canvasId).getContext("2d");
        const datasets = [
            { label: "Atual", data: current, borderColor: currentColor, backgroundColor: `${currentColor}20`, pointRadius: 0, borderWidth: 2, tension: 0.35, fill: true },
            { label: "Alvo", data: target, borderColor: "#747d74", pointRadius: 0, borderWidth: 1.5, borderDash: [5, 5], tension: 0.25 },
        ];
        if (existingChart) {
            existingChart.data.labels = labels;
            existingChart.data.datasets.forEach((dataset, index) => { dataset.data = datasets[index].data; });
            existingChart.update("none");
            return existingChart;
        }
        return new Chart(context, {
            type: "line",
            data: { labels, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: "index" },
                plugins: { legend: { display: false }, tooltip: { backgroundColor: "#202620", titleColor: "#edf1eb", bodyColor: "#c5cec4", borderColor: "#3a443a", borderWidth: 1 } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#89938a", maxTicksLimit: 6, maxRotation: 0, font: { size: 9 } }, border: { display: false } },
                    y: { grid: { color: "#293029" }, ticks: { color: "#89938a", font: { size: 9 } }, border: { display: false } },
                },
            },
        });
    }

    function updateTemperatureCharts(payload) {
        const records = [...(payload?.results || [])].reverse();
        const labels = records.map((record) => new Intl.DateTimeFormat("pt-BR", { hour: "2-digit", minute: "2-digit" }).format(new Date(record.recorded_at)));
        nozzleChart = updateChart(nozzleChart, "nozzle-chart", labels, records.map((record) => record.nozzle_actual), records.map((record) => record.nozzle_target), "#ffa96b");
        bedChart = updateChart(bedChart, "bed-chart", labels, records.map((record) => record.bed_actual), records.map((record) => record.bed_target), "#72c6ff");
    }

    function updateActiveJob(payload) {
        const jobs = payload?.results || [];
        const active = jobs.find((job) => ["Printing", "Paused"].includes(job.state) && !job.completed_at);
        $("active-job").hidden = !active;
        $("empty-job").hidden = Boolean(active);
        if (!active) {
            setText("job-state", "Sem atividade");
            $("job-state").classList.remove("active");
            return;
        }
        setText("job-filename", active.file_name);
        setText("job-state", active.state);
        $("job-state").classList.add("active");
        const progress = Math.min(100, Math.max(0, Number(active.progress) || 0));
        setText("job-progress-label", `${formatNumber(progress)}%`);
        $("job-progress-fill").style.width = `${progress}%`;
        $("job-progress-bar").setAttribute("aria-valuenow", String(progress));
        setText("job-elapsed", formatDuration(active.print_time));
        setText("job-remaining", formatDuration(active.print_time_left));
    }

    function renderJobs(records, append = false) {
        const tableBody = $("jobs-table-body");
        if (!append) tableBody.replaceChildren();
        if (!records.length && !append) {
            const row = document.createElement("tr");
            row.innerHTML = '<td colspan="5" class="table-message">Nenhum trabalho registrado ainda.</td>';
            tableBody.append(row);
            return;
        }
        records.forEach((job) => {
            const row = document.createElement("tr");
            const values = [job.file_name, job.state, `${formatNumber(job.progress)}%`, formatDate(job.started_at), formatDate(job.completed_at)];
            values.forEach((value, index) => {
                const cell = document.createElement("td");
                if (index === 1) {
                    const badge = document.createElement("span");
                    badge.className = `table-state${["Printing", "Paused"].includes(job.state) && !job.completed_at ? " is-active" : ""}`;
                    badge.textContent = value || "—";
                    cell.append(badge);
                } else {
                    cell.textContent = value || "—";
                }
                row.append(cell);
            });
            tableBody.append(row);
        });
    }

    function updateJobs(payload) {
        totalJobs = payload.count || 0;
        currentJobPage = 1;
        nextJobsUrl = payload.next;
        setText("job-count", `${totalJobs} ${totalJobs === 1 ? "trabalho" : "trabalhos"}`);
        renderJobs(payload.results || []);
        setText("history-page-label", `${(payload.results || []).length} de ${totalJobs}`);
        $("next-jobs-page").disabled = !nextJobsUrl;
        updateActiveJob(payload);
    }

    async function refresh() {
        if (refreshing) return;
        refreshing = true;
        try {
            const [status, temperature, temperatureHistory, jobs] = await Promise.all([
                getJson(api.status), getJson(api.temperature), getJson(api.temperatureHistory), getJson(api.jobs),
            ]);
            updateStatus(status);
            updateTemperature(temperature);
            updateTemperatureCharts(temperatureHistory);
            updateJobs(jobs);
            alertBox.hidden = true;
            refreshState.textContent = `Atualizado às ${new Intl.DateTimeFormat("pt-BR", { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(new Date())}`;
        } catch (error) {
            console.error("Falha ao atualizar o dashboard:", error);
            alertBox.hidden = false;
            refreshState.textContent = "Falha na atualização";
        } finally {
            refreshing = false;
        }
    }

    $("next-jobs-page").addEventListener("click", async () => {
        if (!nextJobsUrl) return;
        const button = $("next-jobs-page");
        button.disabled = true;
        try {
            const payload = await getJson(nextJobsUrl);
            currentJobPage += 1;
            nextJobsUrl = payload.next;
            renderJobs(payload.results || [], true);
            const shown = Math.min(currentJobPage * 10, totalJobs);
            setText("history-page-label", `${shown} de ${totalJobs}`);
            button.disabled = !nextJobsUrl;
        } catch (error) {
            console.error("Falha ao carregar mais trabalhos:", error);
            alertBox.hidden = false;
            button.disabled = false;
        }
    });

    refresh();
    window.setInterval(refresh, pollInterval);
})();
