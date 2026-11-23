import { useCallback, useEffect, useRef, useState } from "react";
import { Activity, ArrowDownUp, Bot, ChartNoAxesCombined, CircleAlert, Clock3, Gauge, LayoutDashboard, LockKeyhole, RefreshCw, Settings2, ShieldCheck, Wallet, Search } from "lucide-react";

const API = "http://127.0.0.1:8000";
const SCAN_INTERVAL_MS = 60_000;

function Metric({ icon: Icon, label, value, hint }) {
  return <article className="metric">
    <div className="metric-top"><span>{label}</span><Icon size={18}/></div>
    <strong>{value}</strong><small>{hint}</small>
  </article>;
}

function formatCount(value) {
  return Number(value || 0).toLocaleString("fa-IR");
}

function formatAmount(value) {
  return Number(value || 0).toLocaleString("en-US", { maximumFractionDigits: 4 });
}

export default function App() {
  const [status, setStatus] = useState(null);
  const [connected, setConnected] = useState(false);
  const [exchangeConnected, setExchangeConnected] = useState(false);
  const [marketCounts, setMarketCounts] = useState({ total: 0, active: 0 });
  const [paper, setPaper] = useState({ total_trades: 0, open_positions: 0, realized_net_pnl: 0 });
  const [lastUpdate, setLastUpdate] = useState("—");
  const [scan, setScan] = useState([]);
  const [scanLoading, setScanLoading] = useState(false);
  const [scanError, setScanError] = useState("");
  const scanInFlight = useRef(false);

  const runScan = useCallback(async () => {
    if (scanInFlight.current) return;
    scanInFlight.current = true;
    setScanLoading(true);
    setScanError("");

    const results = await Promise.allSettled([
      fetch(`${API}/api/exchange/markets`).then(async (r) => {
        const data = await r.json();
        if (!r.ok) throw new Error(data.detail || "خطا در دریافت فهرست بازارها");
        return data;
      }),
      fetch(`${API}/api/exchange/scan?max_markets=24&max_spread_percent=0.8`).then(async (r) => {
        const data = await r.json();
        if (!r.ok) throw new Error(data.detail || "خطا در اسکن بازارها");
        return data;
      }),
      fetch(`${API}/api/status`).then(async (r) => {
        if (!r.ok) throw new Error("خطا در وضعیت Backend");
        return r.json();
      }),
      fetch(`${API}/api/paper/summary`).then(async (r) => {
        if (!r.ok) throw new Error("خطا در دفتر معاملات آزمایشی");
        return r.json();
      }),
    ]);

    const [marketsResult, scanResult, statusResult, paperResult] = results;
    if (marketsResult.status === "fulfilled") {
      setMarketCounts({
        total: marketsResult.value.total_p2p_markets || 0,
        active: marketsResult.value.active_p2p_markets || 0,
      });
      setExchangeConnected(true);
    } else {
      setExchangeConnected(false);
    }

    if (scanResult.status === "fulfilled") {
      setScan(scanResult.value.results || []);
    } else {
      setScanError(scanResult.reason?.message || "خطای نامشخص هنگام اسکن");
    }

    if (statusResult.status === "fulfilled") setStatus(statusResult.value);
    if (paperResult.status === "fulfilled") setPaper(paperResult.value);

    setLastUpdate(new Date().toLocaleTimeString("fa-IR"));
    scanInFlight.current = false;
    setScanLoading(false);
  }, []);

  useEffect(() => {
    let socket;
    let retry;
    let alive = true;
    const connect = () => {
      socket = new WebSocket("ws://127.0.0.1:8000/ws/status");
      socket.onopen = () => alive && setConnected(true);
      socket.onmessage = (event) => {
        if (!alive) return;
        try { setStatus(JSON.parse(event.data)); } catch {}
      };
      socket.onclose = () => {
        if (!alive) return;
        setConnected(false);
        retry = setTimeout(connect, 2500);
      };
      socket.onerror = () => socket.close();
    };
    connect();
    return () => { alive = false; clearTimeout(retry); socket?.close(); };
  }, []);

  useEffect(() => {
    runScan();
    const interval = setInterval(runScan, SCAN_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [runScan]);

  const refresh = () => runScan();

  return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-icon"><Bot size={23}/></div><div><b>ARZINJA BOT</b><small>نسخه ویندوز · محلی</small></div></div>
      <div className="nav-label">میز کار</div>
      <a className="nav active"><LayoutDashboard size={18}/> داشبورد</a>
      <a className="nav disabled"><ChartNoAxesCombined size={18}/> تحلیل و استراتژی <em>به‌زودی</em></a>
      <a className="nav disabled"><ArrowDownUp size={18}/> معاملات <em>به‌زودی</em></a>
      <a className="nav disabled"><Wallet size={18}/> دارایی‌ها <em>به‌زودی</em></a>
      <a className="nav disabled"><Settings2 size={18}/> تنظیمات <em>به‌زودی</em></a>
      <div className="sidebar-bottom"><ShieldCheck size={17}/><span>محافظت‌شده با اجرای محلی</span></div>
    </aside>

    <main className="main">
      <header className="topbar">
        <div><div className="eyebrow">پنل مدیریت ربات</div><h1>داشبورد معاملاتی</h1></div>
        <div className="top-actions"><span className={connected ? "connection online" : "connection"}><i/>{connected ? "ارتباط زنده با Backend" : "در انتظار اتصال Backend"}</span><button className="icon-btn" onClick={refresh} disabled={scanLoading} title="بروزرسانی">{scanLoading ? "…" : <RefreshCw size={17}/>}</button></div>
      </header>

      <section className="welcome">
        <div><span className="pill"><Activity size={14}/> پایش خودکار بازار</span><h2>به پنل ربات ارزینجا خوش آمدی</h2><p>بازارهای فعال Advanced Trade به‌صورت خودکار هر ۶۰ ثانیه اسکن می‌شوند. این نسخه فقط داده عمومی را می‌خواند و هیچ سفارش واقعی ارسال نمی‌کند.</p></div>
        <div className="welcome-art"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="orb-core"><Bot size={36}/></div></div>
      </section>

      <section className="metrics">
        <Metric icon={Search} label="بازارهای فعال P2P" value={`${formatCount(marketCounts.active)} / ${formatCount(marketCounts.total)}`} hint={exchangeConnected ? "دریافت از API آذرینجا" : "اتصال به API برقرار نیست"} />
        <Metric icon={ChartNoAxesCombined} label="بازارهای واجد فیلتر" value={formatCount(scan.length)} hint="اسپرد حداکثر ۰٫۸٪" />
        <Metric icon={ArrowDownUp} label="موقعیت‌های Paper باز" value={formatCount(paper.open_positions)} hint={`${formatCount(paper.total_trades)} معامله ثبت‌شده در کل`} />
        <Metric icon={Wallet} label="سود و زیان تحقق‌یافته" value={formatAmount(paper.realized_net_pnl)} hint="بر اساس دفتر معاملات آزمایشی" />
      </section>

      <section className="panel roadmap">
        <div className="panel-head"><div><h3><Search size={17}/> اسکن خودکار بازارهای Advanced Trade</h3><p>اسکن کامل بازارهای فعال P2P؛ Maker/Taker در شبیه‌سازی صفر، اسپرد و لغزش همچنان هزینه‌اند</p></div><button className="icon-btn" onClick={refresh} disabled={scanLoading} title="شروع اسکن">{scanLoading ? "…" : <RefreshCw size={17}/>}</button></div>
        {scanError && <div className="notice"><CircleAlert size={17}/><span>{scanError}</span></div>}
        {scan.length === 0 ? <p className="muted">{scanLoading ? "در حال دریافت دفتر سفارش‌های بازارها..." : "در حال حاضر بازاری از فیلتر عبور نکرده یا اسکن با خطا روبه‌رو شده است."}</p> : <div className="status-list">{scan.map((item) => <div key={item.pair}><span><b>{item.pair}</b> · اسپرد {item.spread_percent}%</span><b className="ok">عمق {formatAmount(item.liquidity_score)}</b></div>)}</div>}
        <p className="muted">آخرین بررسی: {lastUpdate} · بروزرسانی خودکار هر ۶۰ ثانیه</p>
      </section>

      <section className="grid-two">
        <article className="panel">
          <div className="panel-head"><div><h3>وضعیت اجرا</h3><p>اطلاعات زنده از سرویس محلی</p></div><span className="live-dot">LIVE</span></div>
          <div className="status-list">
            <div><span>سرور FastAPI</span><b className="ok">{status?.status === "ready" ? "فعال" : "در حال بررسی"}</b></div>
            <div><span>ارتباط زنده داشبورد</span><b className={connected ? "ok" : "warn"}>{connected ? "متصل" : "قطع"}</b></div>
            <div><span>دریافت داده از ارزینجا</span><b className={exchangeConnected ? "ok" : "warn"}>{exchangeConnected ? "متصل" : "قطع یا نامشخص"}</b></div>
            <div><span>حالت معاملاتی</span><b className="warn">Paper Trading</b></div>
            <div><span>موتور استراتژی</span><b className="muted">هنوز فعال نشده</b></div>
            <div><span>آخرین بروزرسانی</span><b className="muted">{lastUpdate}</b></div>
          </div>
        </article>
        <article className="panel safety">
          <div className="panel-head"><div><h3><LockKeyhole size={17}/> ایمنی معاملات</h3><p>محافظت از سرمایه در زمان توسعه</p></div></div>
          <div className="safety-state"><div className="safe-icon"><ShieldCheck size={25}/></div><div><b>معاملات واقعی غیرفعال</b><small>حالت Paper قفل است؛ هیچ سفارش واقعی ارسال نمی‌شود</small></div></div>
          <div className="notice"><CircleAlert size={17}/><span>{status?.notice || "وضعیت سرویس محلی در حال دریافت است."}</span></div>
        </article>
      </section>

      <section className="panel roadmap">
        <div className="panel-head"><div><h3>مراحل آماده‌سازی</h3><p>مسیر توسعه نسخه ویندوز</p></div><span className="step-count">مرحله ۳ از ۵</span></div>
        <div className="steps">
          <div className="step done"><i>✓</i><span>ساختار وب و API محلی</span></div>
          <div className="step done"><i>✓</i><span>اتصال و اسکن زنده بازارهای P2P</span></div>
          <div className="step current"><i>۳</i><span>موتور سیگنال و استراتژی</span></div>
          <div className="step"><i>۴</i><span>اجرای خودکار Paper Trading</span></div>
          <div className="step"><i>۵</i><span>آزمون نهایی و آماده‌سازی ویندوز</span></div>
        </div>
      </section>
      <footer><span>Arzinja Trading Bot · Windows Edition</span><span><Clock3 size={14}/> معاملات واقعی غیرفعال · پایش داده عمومی فعال</span></footer>
    </main>
  </div>;
}
