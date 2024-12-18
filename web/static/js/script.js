// 숫자를 3자리마다 콤마로 포맷팅
function formatNumber(value) {
    return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// 최근 거래 기록 렌더링
function renderRecentTrades(recentTrades) {
    const recentTradesTable = document.getElementById('recentTradesTable');

    if (!recentTrades || recentTrades.length === 0) {
        recentTradesTable.innerHTML = `
            <tr>
                <td colspan="4" class="text-center">최근 거래 기록이 없습니다.</td>
            </tr>
        `;
        return;
    }

    recentTradesTable.innerHTML = recentTrades
        .filter(trade => trade.action !== 'hold') // 'hold' 제외
        .slice(0, 4) // 최근 4개만
        .map(trade => `
            <tr>
                <td data-label="거래 시점">${new Date(trade.timestamp).toLocaleString()}</td>
                <td data-label="유형">${trade.action}</td>
                <td data-label="거래 금액">${trade.amount.toFixed(8)} ${trade.currency}</td>
                <td data-label="거래 이유">${trade.reason}</td>
            </tr>
        `).join('');
}

// 현재 성과 데이터를 렌더링
function renderPerformanceData(performance) {
    const currentProfitRate = document.getElementById("currentProfitRate");
    const currentProfitLoss = document.getElementById("currentProfitLoss");
    const cumulativeProfitRate = document.getElementById("cumulativeProfitRate");
    const cumulativeProfitLoss = document.getElementById("cumulativeProfitLoss");

    // 데이터 존재 여부 확인 후 렌더링
    currentProfitRate.innerText = performance?.current_profit_rate !== undefined
        ? `${formatNumber(performance.current_profit_rate)}`
        : "데이터 없음";
    currentProfitLoss.innerText = performance?.current_profit_loss !== undefined
        ? `${formatNumber(performance.current_profit_loss)}`
        : "데이터 없음";
    cumulativeProfitRate.innerText = performance?.cumulative_profit_rate !== undefined
        ? `${formatNumber(performance.cumulative_profit_rate)}`
        : "데이터 없음";
    cumulativeProfitLoss.innerText = performance?.cumulative_profit_loss !== undefined
        ? `${formatNumber(performance.cumulative_profit_loss)}`
        : "데이터 없음";
}

// 포트폴리오 데이터를 렌더링
function renderPortfolioData(portfolio) {
    const totalInvestment = document.getElementById("totalInvestment");
    const portfolioList = document.getElementById("portfolioList");

    if (!portfolio) {
        totalInvestment.innerText = "데이터 없음";
        portfolioList.innerHTML = "<li>데이터가 없습니다.</li>";
        return;
    }

    // 총 투자 금액 렌더링
    totalInvestment.innerText = portfolio.total_investment
        ? formatNumber(portfolio.total_investment)
        : "데이터 없음";

    // 포트폴리오 데이터 렌더링
    portfolioList.innerHTML = `
        <li class="list-group-item d-flex justify-content-between align-items-center">
            <strong>KRW</strong>
            <span>보유량: ${portfolio.cash_balance.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
        </li>
        <li class="list-group-item d-flex justify-content-between align-items-center">
            <strong>${portfolio.currency}</strong>
            <span>보유량: ${portfolio.balance.toFixed(8)}</span>
        </li>
    `;
}


// 성과 그래프 렌더링
function loadPerformanceGraphs(graphData) {
    if (!graphData || !graphData.cumulative_profit || !graphData.daily_profit) {
        console.error("그래프 데이터가 유효하지 않습니다.");
        return;
    }

    // 누적 수익 그래프 데이터 준비
    const cumulativeLabels = graphData.cumulative_profit.map(item => item.date);
    const cumulativeData = graphData.cumulative_profit.map(item => item.value);

    // 누적 수익 그래프
    new Chart(document.getElementById("cumulativeProfitChart"), {
        type: "line",
        data: {
            labels: cumulativeLabels,
            datasets: [{
                label: "누적 수익",
                data: cumulativeData,
                borderColor: "#B2E4A8", // 파스텔 초록색
                backgroundColor: "rgba(178, 228, 168, 0.3)", // 투명한 파스텔 초록색
                borderWidth: 2, // 선 굵기
                fill: true, // 아래쪽 색상 채우기
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: context => `${context.raw.toLocaleString()} KRW` } }
            },
            scales: {
                x: { grid: { display: false } },
                y: {
                    ticks: { callback: value => `${value.toLocaleString()} KRW` },
                    beginAtZero: true, // Y축 0 기준
                }
            }
        }
    });

    // 일간 수익 그래프 데이터 준비
    const dailyLabels = graphData.daily_profit.map(item => item.date);
    const dailyData = graphData.daily_profit.map(item => item.value);

    // 일간 수익 그래프
    new Chart(document.getElementById("dailyProfitChart"), {
        type: "bar",
        data: {
            labels: dailyLabels,
            datasets: [{
                label: "일간 수익",
                data: dailyData,
                backgroundColor: dailyData.map(value => value >= 0 ? "rgba(160, 211, 232, 0.8)" : "rgba(242, 182, 210, 0.8)"), // 양수: 파스텔 파랑, 음수: 파스텔 분홍
                borderColor: dailyData.map(value => value >= 0 ? "#A0D3E8" : "#F2B6D2"), // 동일 계열 테두리
                borderWidth: 1, // 얇은 테두리
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: context => `${context.raw.toLocaleString()} KRW` } }
            },
            scales: {
                x: { grid: { display: false } },
                y: {
                    ticks: { callback: value => `${value.toLocaleString()} KRW` },
                    beginAtZero: true, // Y축 0 기준
                    suggestedMin: Math.min(...dailyData, 0) - 10, // 최소값 설정
                    suggestedMax: Math.max(...dailyData, 0) + 10, // 최대값 설정
                }
            }
        }
    });
}




// 전체 거래 데이터 페이징
let currentPage = 1;
async function loadTradeLogs(page) {
    try {
        const response = await fetch(`/api/trades?page=${page}&per_page=5`);
        if (!response.ok) throw new Error('Failed to load trade logs');

        const data = await response.json();

        const allTradesTable = document.getElementById('allTradesTable');
        if (!data.trade_logs || data.trade_logs.length === 0) {
            allTradesTable.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center">거래 기록이 없습니다.</td>
                </tr>`;
            return;
        }

        allTradesTable.innerHTML = data.trade_logs.map(trade => `
            <tr>
                <td>${new Date(trade.timestamp).toLocaleString()}</td>
                <td>${trade.action}</td>
                <td>${trade.amount.toFixed(8)} ${trade.currency}</td>
                <td>${trade.reason}</td>
            </tr>
        `).join('');

        // 페이지 네비게이션
        currentPage = data.page;
        document.getElementById('currentPage').innerText = `페이지: ${currentPage}`;
        document.getElementById('prevPage').disabled = currentPage <= 1;
        document.getElementById('nextPage').disabled = currentPage * 5 >= data.total_records;
    } catch (error) {
        console.error('Error loading trade logs:', error);
    }
}

// 초기 데이터 로드 및 이벤트 리스너 설정
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard');
        if (!response.ok) throw new Error('Failed to load dashboard data');

        const data = await response.json();
        console.log('Dashboard Data:', data); // Debugging 용 로그

        // 성과, 포트폴리오 및 그래프 데이터 렌더링
        renderPerformanceData(data.performance);
        renderPortfolioData(data.portfolio);
        loadPerformanceGraphs(data.graphs);

        // 최근 거래 기록 렌더링
        renderRecentTrades(data.recent_trades);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("prevPage").addEventListener("click", () => {
        if (currentPage > 1) loadTradeLogs(currentPage - 1);
    });

    document.getElementById("nextPage").addEventListener("click", () => {
        loadTradeLogs(currentPage + 1);
    });

    loadDashboardData();
    loadTradeLogs(1);
});
