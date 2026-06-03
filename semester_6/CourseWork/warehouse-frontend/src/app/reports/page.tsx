import Link from "next/link";

const REPORTS = [
  {
    href: "/reports/stock-valuation",
    title: "Stock Valuation",
    description: "Review current stock quantities, unit costs, and inventory valuation.",
  },
  {
    href: "/reports/production-cost",
    title: "Production Cost",
    description: "Inspect production order cost snapshots and unit costs for finished goods.",
  },
  {
    href: "/reports/movements",
    title: "Inventory Movements",
    description: "Audit receipt, sale issue, and production inventory transactions.",
  },
];

export default function ReportsPage() {
  return (
    <main className="page-container">
      <section className="hero-card">
        <div>
          <div className="eyebrow">Reports</div>
          <h1 className="hero-title">Report center</h1>
          <p className="hero-description">Open a focused analytics view for stock, production costs, or inventory movement history.</p>
        </div>
      </section>

      <section className="stats-grid report-card-grid">
        {REPORTS.map((report) => (
          <Link className="stat-card report-card" href={report.href} key={report.href}>
            <div className="stat-label">Report</div>
            <div className="report-card-title">{report.title}</div>
            <p className="muted-text">{report.description}</p>
          </Link>
        ))}
      </section>
    </main>
  );
}
