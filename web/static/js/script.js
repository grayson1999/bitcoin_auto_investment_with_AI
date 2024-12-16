
// 성과 그래프 데이터 로드 및 렌더링
async function loadPerformanceGraph() {
    try {
        const response = await fetch("/api/performance-graph");
        if (!response.ok) throw new Error("그래프 API 호출 실패");

        const data = await response.json();

        if (!data.cumulative_profit_rate || !data.daily_profit_loss) {
            throw new Error("그래프 데이터가 올바르지 않습니다.");
        }

        // 누적 수익률 데이터
        const cumulativeLabels = data.cumulative_profit_rate.map((item) => item.date);
        const cumulativeData = data.cumulative_profit_rate.map((item) => item.rate);

        // 일간 손익 데이터
        const dailyLabels = data.daily_profit_loss.map((item) => item.date);
        const dailyData = data.daily_profit_loss.map((item) => item.loss);

        // 누적 수익률 그래프 렌더링
        new Chart(document.getElementById("cumulativeProfitChart"), {
            type: "line",
            data: {
                labels: cumulativeLabels,
                datasets: [
                    {
                        label: "누적 수익률 (%)",
                        data: cumulativeData,
                        borderColor: "rgba(75, 192, 192, 1)",
                        backgroundColor: "rgba(75, 192, 192, 0.2)",
                        fill: true,
                        tension: 0.4,
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: "top" },
                    tooltip: {
                        callbacks: { label: (context) => `${context.raw.toFixed(2)}%` },
                    },
                },
            },
        });

        // 일간 손익 그래프 렌더링
        new Chart(document.getElementById("dailyProfitChart"), {
            type: "bar",
            data: {
                labels: dailyLabels,
                datasets: [
                    {
                        label: "일간 손익 (KRW)",
                        data: dailyData,
                        backgroundColor: dailyData.map((val) =>
                            val >= 0 ? "rgba(54, 162, 235, 0.5)" : "rgba(255, 99, 132, 0.5)"
                        ),
                        borderColor: dailyData.map((val) =>
                            val >= 0 ? "rgba(54, 162, 235, 1)" : "rgba(255, 99, 132, 1)"
                        ),
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: "top" },
                    tooltip: {
                        callbacks: { label: (context) => `${context.raw.toLocaleString()} KRW` },
                    },
                },
                scales: {
                    y: { beginAtZero: true },
                },
            },
        });
    } catch (error) {
        console.error("그래프 로드 실패:", error);
        alert("그래프 데이터를 불러오지 못했습니다. 다시 시도해주세요.");
    }
}

// 성과 그래프 로드
loadPerformanceGraph();


// 거래 기록 데이터 로드 및 페이징
async function loadTradeLogs(page) {
    try {
        const response = await fetch(`/api/trade-logs?page=${page}&per_page=5`);
        if (!response.ok) throw new Error("거래 기록 API 호출 실패");

        const data = await response.json();
        const tableBody = document.querySelector("#tradeLogsTable");
        tableBody.innerHTML = ""; // 기존 데이터를 초기화

        data.trade_logs.forEach(log => {
            const currency = log.amount > 1 ? "KRW" : "BTC"; // 통화 결정
            const row = document.createElement("tr");
            row.innerHTML = `
                    <td>${log.timestamp}</td>
                    <td>${log.action}</td>
                    <td>${log.amount.toLocaleString()} ${currency}</td>
                    <td class="reason-cell">${log.reason || "N/A"}</td>
                `;
            tableBody.appendChild(row);
        });

        // 페이지 네비게이션 업데이트
        currentPage = data.page;
        document.querySelector("#currentPage").innerText = `페이지: ${currentPage}`;
        document.querySelector("#prevPage").disabled = currentPage <= 1;
        document.querySelector("#nextPage").disabled = (currentPage * 5) >= data.total_records;
    } catch (error) {
        console.error("거래 기록 로드 실패:", error);
        alert("거래 기록 데이터를 불러오지 못했습니다. 다시 시도해주세요.");
    }
}

// 초기 데이터 로드
loadTradeLogs(1);

// 페이지 버튼 이벤트
document.querySelector("#prevPage").addEventListener("click", () => {
    if (currentPage > 1) loadTradeLogs(currentPage - 1);
});
document.querySelector("#nextPage").addEventListener("click", () => {
    loadTradeLogs(currentPage + 1);
});
