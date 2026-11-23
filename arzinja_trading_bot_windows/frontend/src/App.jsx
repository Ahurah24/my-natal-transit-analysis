import { useEffect, useState } from "react";
import { Activity, ArrowDownUp, Bot, ChartNoAxesCombined, CircleAlert, Clock3, Gauge, LayoutDashboard, LockKeyhole, RefreshCw, Settings2, ShieldCheck, Wallet } from "lucide-react";

const API = "http://127.0.0.1:8000";

function Metric({ icon: Icon, label, value, hint }) {
  return <article className="metric">
    <div className="metric-top"><span>{label}</span><Icon size={18}/></div>
    <strong>{value}</strong><small>{hint}</small>
  </article>;
}

export default function App() {
  const [status, setStatus] = useState(null);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState("—");

  useEffect(() => {
    let socket;
    let retry;
    let alive = true;
    const connect = () => {
      socket = new WebSocket("ws://127.0.0.1:8000/ws/status");
      socket.onopen = () => alive && setConnected(true);
      socket.onmessage = (event) => {
        if (!alive) return;
        try { setStatus(JSON.parse(event.data)); setLastUpdate(new Date().toLocaleTimeString("fa-IR")); } catch {}
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

  const refresh = async () => {
    try {
      const response = await fetch(`${API}/api/status`);
      setStatus(await response.json());
      setLastUpdate(new Date().toLocaleTimeString("fa-IR"));
    } catch { setConnected(false); }
  };

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
        <div className="top-actions"><span className={connected ? "connection online" : "connection"}><i/>{connected ? "اتصال به سرور برقرار" : "در انتظار اتصال"}</span><button className="icon-btn" onClick={refresh} title="بروزرسانی"><RefreshCw size={17}/></button></div>
      </header>

      <section className="welcome">
        <div><span className="pill"><Activity size={14}/> وضعیت سیستم</span><h2>به پنل ربات ارزینجا خوش آمدی</h2><p>زیرساخت ویندوزی آماده راه‌اندازی است. اتصال صرافی و موتور معاملات در مرحله بعد اعتبارسنجی می‌شوند.</p></div>
        <div className="welcome-art"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="orb-core"><Bot size={36}/></div></div>
      </section>

      <section className="metrics">
        <Metric icon={Wallet} label="ارزش کل دارایی" value="—" hint="پس از اتصال امن به حساب" />
        <Metric icon={ChartNoAxesCombined} label="سود و زیان امروز" value="—" hint="هنوز معامله‌ای ثبت نشده" />
        <Metric icon={ArrowDownUp} label="معاملات فعال" value="۰" hint="اجرای واقعی غیرفعال است" />
        <Metric icon={Gauge} label="وضعیت استراتژی" value="متوقف" hint="منتظر اتصال داده بازار" />
      </section>

      <section className="grid-two">
        <article className="panel">
          <div className="panel-head"><div><h3>وضعیت اجرا</h3><p>اطلاعات زنده از سرویس محلی</p></div><span className="live-dot">LIVE</span></div>
          <div className="status-list">
            <div><span>سرور FastAPI</span><b className="ok">فعال</b></div>
            <div><span>ارتباط زنده داشبورد</span><b className={connected ? "ok" : "warn"}>{connected ? "متصل" : "قطع"}</b></div>
            <div><span>حالت معاملاتی</span><b className="warn">{status?.mode === "live" ? "واقعی" : "آزمایشی"}</b></div>
            <div><span>اتصال به ارزینجا</span><b className="muted">بررسی‌نشده</b></div>
            <div><span>آخرین بروزرسانی</span><b className="muted">{lastUpdate}</b></div>
          </div>
        </article>
        <article className="panel safety">
          <div className="panel-head"><div><h3><LockKeyhole size={17}/> ایمنی معاملات</h3><p>محافظت از سرمایه در زمان توسعه</p></div></div>
          <div className="safety-state"><div className="safe-icon"><ShieldCheck size={25}/></div><div><b>معاملات واقعی غیرفعال</b><small>تا زمان تأیید API، داده بازار، مدیریت ریسک و اجرای سفارش</small></div></div>
          <div className="notice"><CircleAlert size={17}/><span>{status?.notice || "در حال دریافت وضعیت سرویس محلی..."}</span></div>
        </article>
      </section>

      <section className="panel roadmap">
        <div className="panel-head"><div><h3>مراحل آماده‌سازی</h3><p>مسیر توسعه نسخه ویندوز</p></div><span className="step-count">مرحله ۱ از ۵</span></div>
        <div className="steps">
          <div className="step done"><i>✓</i><span>ساختار وب و API محلی</span></div>
          <div className="step current"><i>۲</i><span>یکپارچه‌سازی API ارزینجا</span></div>
          <div className="step"><i>۳</i><span>انتقال استراتژی و بک‌تست معتبر</span></div>
          <div className="step"><i>۴</i><span>پیاده‌سازی Paper Trading</span></div>
          <div className="step"><i>۵</i><span>آزمون نهایی و آماده‌سازی ویندوز</span></div>
        </div>
      </section>
      <footer><span>Arzinja Trading Bot · Windows Edition</span><span><Clock3 size={14}/> داده‌های مالی تا اتصال رسمی نمایش داده نمی‌شوند</span></footer>
    </main>
  </div>;
}
