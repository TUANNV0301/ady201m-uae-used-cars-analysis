"""Reproducible analysis for the ADY201m used-car listings project."""
from __future__ import annotations

import json
import math
import os
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = Path(os.getenv("CAR_DATA_PATH", "data/raw/uae_used_cars_10k.csv"))
if not DATA_PATH.is_absolute():
    DATA_PATH = ROOT / DATA_PATH
OUT_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "docs" / "figures"
DB_PATH = Path(os.getenv("CAR_DB_PATH", "database/uae_used_cars.db"))
if not DB_PATH.is_absolute():
    DB_PATH = ROOT / DB_PATH

for configured_path in (DATA_PATH, DB_PATH):
    if configured_path != ROOT and ROOT not in configured_path.parents:
        raise ValueError(f"Configured project paths must stay inside {ROOT}: {configured_path}")


def load_and_clean(path: Path = DATA_PATH) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(path, dtype={"Cylinders": "string"})
    initial_rows = len(raw)
    raw.columns = [c.strip() for c in raw.columns]
    for col in ["Make", "Model", "Body Type", "Transmission", "Fuel Type", "Color", "Location", "Description"]:
        raw[col] = raw[col].astype("string").str.strip()
    raw["Cylinders"] = raw["Cylinders"].replace(
        {"": pd.NA, "None": pd.NA, "Unknown": pd.NA, "nan": pd.NA, "null": pd.NA}
    )
    for col in ["Year", "Price", "Mileage", "Cylinders"]:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    missing_before = raw.isna().sum().to_dict()
    duplicate_count = int(raw.duplicated().sum())
    # Keep valid target and basic numeric predictors; retain missing cylinders for descriptive work.
    clean = raw.drop_duplicates().copy()
    clean = clean.dropna(subset=["Price", "Year", "Mileage"])
    clean["Year"] = clean["Year"].astype(int)
    clean["Mileage"] = clean["Mileage"].astype(int)
    clean["Cylinders"] = clean["Cylinders"].astype("Int64")
    clean["Listing_ID"] = np.arange(1, len(clean) + 1)
    audit = {
        "rows_source": initial_rows,
        "rows_analysis": len(clean),
        "columns": list(clean.columns.drop("Listing_ID")),
        "duplicate_rows_removed": duplicate_count,
        "missing_after_normalization": {k: int(v) for k, v in missing_before.items()},
        "cylinders_missing_normalized": int(clean["Cylinders"].isna().sum()),
        "location_values_trimmed": int((raw["Location"] != pd.read_csv(path)["Location"].astype("string")).sum()),
    }
    return clean, audit


def create_database(df: pd.DataFrame, db_path: Path = DB_PATH) -> None:
    if db_path.exists():
        db_path.unlink()
    schema = (ROOT / "database" / "schema.sql").read_text(encoding="utf-8")
    conn = sqlite3.connect(db_path)
    conn.executescript(schema)
    conn.execute("PRAGMA foreign_keys = ON")
    make = sorted(df["Make"].dropna().unique())
    body = sorted(df["Body Type"].dropna().unique())
    emirates = sorted(df["Location"].dropna().unique())
    conn.executemany("INSERT INTO make(make_name) VALUES (?)", [(x,) for x in make])
    conn.executemany("INSERT INTO body_type(body_type_name) VALUES (?)", [(x,) for x in body])
    conn.executemany("INSERT INTO emirate(emirate_name) VALUES (?)", [(x,) for x in emirates])
    ids = {
        "make": dict(conn.execute("SELECT make_name, make_id FROM make")),
        "body": dict(conn.execute("SELECT body_type_name, body_type_id FROM body_type")),
        "emirate": dict(conn.execute("SELECT emirate_name, emirate_id FROM emirate")),
    }
    values = []
    for r in df.itertuples(index=False):
        cylinders = None if pd.isna(r.Cylinders) else int(r.Cylinders)
        values.append((
            int(r.Listing_ID), ids["make"][r.Make], r.Model, int(r.Year), float(r.Price),
            int(r.Mileage), ids["body"][r[5]], cylinders, r.Transmission, r[8],
            r.Color, ids["emirate"][r.Location], r.Description,
        ))
    conn.executemany(
        """INSERT INTO car_listing
        (listing_id, make_id, model, year, price_aed, mileage_km, body_type_id,
         cylinders, transmission, fuel_type, color, emirate_id, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", values
    )
    conn.commit()
    conn.close()


def mann_whitney_approx(a: np.ndarray, b: np.ndarray) -> dict:
    """Mann–Whitney U with tie-corrected normal approximation (two-sided)."""
    combined = np.concatenate([a, b])
    ranks = pd.Series(combined).rank(method="average").to_numpy()
    n1, n2 = len(a), len(b)
    r1 = float(ranks[:n1].sum())
    u1 = r1 - n1 * (n1 + 1) / 2
    u2 = n1 * n2 - u1
    u = min(u1, u2)
    _, counts = np.unique(combined, return_counts=True)
    n = n1 + n2
    tie_sum = float(np.sum(counts**3 - counts))
    variance = n1 * n2 / 12 * ((n + 1) - tie_sum / (n * (n - 1)))
    z = (u - n1 * n2 / 2 + 0.5) / math.sqrt(variance) if variance > 0 else 0.0
    p = math.erfc(abs(z) / math.sqrt(2))
    return {"U": float(u), "z_approx": float(z), "p_value_approx": float(p), "n_group1": n1, "n_group2": n2}


def model_evaluation(df: pd.DataFrame) -> dict:
    # Deterministic 80/20 hold-out; log target limits influence of the long right tail.
    x = df[["Year", "Mileage"]].to_numpy(dtype=float)
    y = np.log(df["Price"].to_numpy(dtype=float))
    rng = np.random.default_rng(201)
    order = rng.permutation(len(df))
    n_train = int(0.8 * len(order))
    train, test = order[:n_train], order[n_train:]
    mean, std = x[train].mean(axis=0), x[train].std(axis=0)
    std[std == 0] = 1
    x_scaled = (x - mean) / std
    design = np.column_stack([np.ones(len(x_scaled)), x_scaled])
    beta, *_ = np.linalg.lstsq(design[train], y[train], rcond=None)
    pred_price = np.exp(design[test] @ beta)
    actual = np.exp(y[test])
    baseline = np.full(len(test), float(np.median(np.exp(y[train]))))

    def metrics(pred):
        residual = actual - pred
        denom = float(np.sum((actual - actual.mean()) ** 2))
        return {
            "MAE_AED": float(np.mean(np.abs(residual))),
            "RMSE_AED": float(np.sqrt(np.mean(residual**2))),
            "R2_AED": float(1 - np.sum(residual**2) / denom) if denom else None,
        }
    return {
        "n_train": int(len(train)), "n_test": int(len(test)),
        "predictors": ["Year", "Mileage"], "target_transform": "natural log of Price",
        "coefficients_log_price": {"intercept": float(beta[0]), "Year_standardized": float(beta[1]), "Mileage_standardized": float(beta[2])},
        "baseline_train_median": metrics(baseline), "linear_regression": metrics(pred_price),
        "note": "Metrics are on AED scale after exponentiating predicted log price; a simple baseline, not a valuation product.",
    }


def create_svg_charts(df: pd.DataFrame) -> None:
    """Create lightweight SVG plots if matplotlib/seaborn are unavailable."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    width, height = 900, 520
    left, right, top, bottom = 85, 35, 65, 75
    plot_w, plot_h = width - left - right, height - top - bottom
    sample = df.sample(min(1800, len(df)), random_state=201)
    max_mileage = float(df["Mileage"].quantile(.99))
    max_log_price = float(np.log(df["Price"].quantile(.99)))
    points = []
    for r in sample.itertuples(index=False):
        px = left + min(float(r.Mileage), max_mileage) / max_mileage * plot_w
        py = top + (1 - min(float(np.log(r.Price)), max_log_price) / max_log_price) * plot_h
        points.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.4" fill="#2878B5" fill-opacity="0.38"/>')
    scatter = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="450" y="32" text-anchor="middle" font-family="Arial" font-size="21">Giá niêm yết và số km (mẫu; trục Y log)</text>',
        f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="#333"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#333"/>']
    scatter.extend(points)
    for tick in range(6):
        x = left + tick * plot_w / 5
        scatter.append(f'<text x="{x:.1f}" y="{top+plot_h+24}" text-anchor="middle" font-family="Arial" font-size="12">{tick*max_mileage/5:,.0f}</text>')
    for tick in range(6):
        y = top + plot_h - tick * plot_h / 5
        value = math.exp(tick * max_log_price / 5)
        scatter.append(f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end" font-family="Arial" font-size="12">{value:,.0f}</text>')
    scatter += [f'<text x="{left+plot_w/2}" y="{height-20}" text-anchor="middle" font-family="Arial" font-size="15">Quãng đường (km)</text>',
        f'<text x="22" y="{top+plot_h/2}" text-anchor="middle" transform="rotate(-90 22 {top+plot_h/2})" font-family="Arial" font-size="15">Giá niêm yết (AED, log)</text>', '</svg>']
    (FIGURES_DIR / "price_vs_mileage.svg").write_text("\n".join(scatter), encoding="utf-8")

    stats = df.groupby("Year")["Price"].median().sort_index()
    chart_top, chart_bottom = 65, 85
    chart_h = height - chart_top - chart_bottom
    max_val = float(stats.quantile(.95))
    bar_w = plot_w / len(stats) * .62
    bars = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="450" y="32" text-anchor="middle" font-family="Arial" font-size="21">Trung vị giá niêm yết theo năm xe</text>',
        f'<line x1="{left}" y1="{chart_top+chart_h}" x2="{left+plot_w}" y2="{chart_top+chart_h}" stroke="#333"/>']
    for i, (year, val) in enumerate(stats.items()):
        cx = left + (i + .5) * plot_w / len(stats)
        bh = min(float(val), max_val) / max_val * chart_h
        bars.append(f'<rect x="{cx-bar_w/2:.1f}" y="{chart_top+chart_h-bh:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" fill="#32A287"/>')
        bars.append(f'<text x="{cx:.1f}" y="{chart_top+chart_h+22}" text-anchor="middle" font-family="Arial" font-size="11">{year}</text>')
    bars.append(f'<text x="{left-10}" y="{chart_top+5}" text-anchor="end" font-family="Arial" font-size="12">{max_val:,.0f}</text>')
    bars += [f'<text x="{left+plot_w/2}" y="{height-22}" text-anchor="middle" font-family="Arial" font-size="15">Năm sản xuất</text>',
        f'<text x="22" y="{chart_top+chart_h/2}" text-anchor="middle" transform="rotate(-90 22 {chart_top+chart_h/2})" font-family="Arial" font-size="15">Trung vị AED</text>', '</svg>']
    (FIGURES_DIR / "median_price_by_year.svg").write_text("\n".join(bars), encoding="utf-8")

    # Raster versions are saved at 300 DPI for report/slide insertion even when
    # matplotlib cannot be installed in the current runtime.
    try:
        from PIL import Image, ImageDraw, ImageFont

        W, H = 1800, 1050
        L, R, T, B = 180, 75, 115, 170
        pw, ph = W - L - R, H - T - B
        font_path = Path("C:/Windows/Fonts/arial.ttf")
        def font(size):
            try:
                return ImageFont.truetype(str(font_path), size)
            except OSError:
                return ImageFont.load_default()
        def vertical_label(image, text, y_center):
            label = Image.new("RGBA", (620, 72), (255, 255, 255, 0))
            ImageDraw.Draw(label).text((310, 36), text, fill="#333333", font=label_font, anchor="mm")
            rotated = label.rotate(90, expand=True)
            image.paste(rotated, (22, int(y_center - rotated.height/2)), rotated)
        title_font, label_font, tick_font = font(48), font(34), font(27)
        bg = Image.new("RGB", (W, H), "white")
        draw = ImageDraw.Draw(bg)
        draw.text((W/2, 42), "Listed price vs mileage (log price axis)", fill="#142648", font=title_font, anchor="mt")
        draw.line((L, T+ph, L+pw, T+ph), fill="#333333", width=3)
        draw.line((L, T, L, T+ph), fill="#333333", width=3)
        pts = Image.new("RGBA", (W, H), (255,255,255,0))
        pd = ImageDraw.Draw(pts)
        for r in sample.itertuples(index=False):
            x = L + min(float(r.Mileage), max_mileage) / max_mileage * pw
            y = T + (1 - min(float(np.log(r.Price)), max_log_price) / max_log_price) * ph
            pd.ellipse((x-4,y-4,x+4,y+4), fill=(40,120,181,110))
        bg = Image.alpha_composite(bg.convert("RGBA"), pts).convert("RGB")
        draw = ImageDraw.Draw(bg)
        for tick in range(6):
            x = L + tick*pw/5
            draw.text((x,T+ph+25), f"{tick*max_mileage/5:,.0f}", fill="#333333", font=tick_font, anchor="mt")
            y = T+ph-tick*ph/5
            draw.text((L-18,y), f"{math.exp(tick*max_log_price/5):,.0f}", fill="#333333", font=tick_font, anchor="rm")
        draw.text((L+pw/2,H-53), "Mileage (km)", fill="#333333", font=label_font, anchor="mt")
        vertical_label(bg, "Listed price (AED, log)", T+ph/2)
        bg.save(FIGURES_DIR / "price_vs_mileage.png", dpi=(300,300))

        bg = Image.new("RGB", (W, H), "white")
        draw = ImageDraw.Draw(bg)
        draw.text((W/2,42), "Median listed price by model year", fill="#142648", font=title_font, anchor="mt")
        chart_top, chart_bottom = 125, 170
        chart_h = H-chart_top-chart_bottom
        draw.line((L,chart_top+chart_h,L+pw,chart_top+chart_h),fill="#333333",width=3)
        for i,(year,val) in enumerate(stats.items()):
            cx=L+(i+.5)*pw/len(stats)
            bh=min(float(val),max_val)/max_val*chart_h
            draw.rectangle((cx-bar_w/2,chart_top+chart_h-bh,cx+bar_w/2,chart_top+chart_h),fill="#28A387")
            draw.text((cx,chart_top+chart_h+22),str(year),fill="#333333",font=tick_font,anchor="mt")
        for tick in range(5):
            y=chart_top+chart_h-tick*chart_h/4
            val=tick*max_val/4
            draw.line((L-8,y,L+pw,y),fill="#e3e9ef",width=2)
            draw.text((L-20,y),f"{val:,.0f}",fill="#333333",font=tick_font,anchor="rm")
        draw.text((L+pw/2,H-50),"Model year",fill="#333333",font=label_font,anchor="mt")
        vertical_label(bg, "Median price (AED)", chart_top+chart_h/2)
        bg.save(FIGURES_DIR / "median_price_by_year.png", dpi=(300,300))
    except ImportError:
        pass


def run() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    df, audit = load_and_clean()
    df.to_csv(OUT_DIR / "clean_car_listings.csv", index=False)
    create_database(df)
    conn = sqlite3.connect(DB_PATH)
    make_sql = pd.read_sql_query("""SELECT m.make_name AS make, COUNT(*) AS listings,
        ROUND(AVG(c.price_aed),2) AS mean_price_aed
        FROM car_listing c JOIN make m ON c.make_id=m.make_id
        GROUP BY m.make_name HAVING COUNT(*) >= 50 ORDER BY mean_price_aed DESC""", conn)
    body_sql = pd.read_sql_query("""SELECT b.body_type_name AS body_type, COUNT(*) AS listings,
        ROUND(AVG(c.price_aed),2) AS mean_price_aed
        FROM car_listing c JOIN body_type b ON c.body_type_id=b.body_type_id
        GROUP BY b.body_type_name ORDER BY listings DESC""", conn)
    location_sql = pd.read_sql_query("""SELECT e.emirate_name AS emirate, c.price_aed
        FROM car_listing c JOIN emirate e ON c.emirate_id=e.emirate_id
        ORDER BY e.emirate_name, c.price_aed""", conn)
    conn.close()
    make_sql.to_csv(OUT_DIR / "sql_mean_price_by_make.csv", index=False)
    body_sql.to_csv(OUT_DIR / "sql_price_by_body_type.csv", index=False)
    medians = location_sql.groupby("emirate")["price_aed"].agg(median="median", count="count").reset_index()
    medians.to_csv(OUT_DIR / "median_price_by_emirate.csv", index=False)
    numerical = df[["Year", "Mileage", "Price"]]
    correlations = {
        "pearson": numerical.corr(method="pearson").round(4).to_dict(),
        "spearman": numerical.corr(method="spearman").round(4).to_dict(),
    }
    suv = df.loc[df["Body Type"] == "SUV", "Price"].to_numpy(dtype=float)
    sedan = df.loc[df["Body Type"] == "Sedan", "Price"].to_numpy(dtype=float)
    test = mann_whitney_approx(suv, sedan)
    test.update({"group1": "SUV", "group2": "Sedan", "median_SUV_AED": float(np.median(suv)), "median_Sedan_AED": float(np.median(sedan))})
    model = model_evaluation(df)
    results = {
        "audit": audit,
        "price_summary_AED": {"mean": float(df.Price.mean()), "median": float(df.Price.median()), "q1": float(df.Price.quantile(.25)), "q3": float(df.Price.quantile(.75)), "min": float(df.Price.min()), "max": float(df.Price.max())},
        "year_summary": {"min": int(df.Year.min()), "median": float(df.Year.median()), "max": int(df.Year.max())},
        "mileage_summary_km": {"min": int(df.Mileage.min()), "median": float(df.Mileage.median()), "max": int(df.Mileage.max())},
        "correlations": correlations,
        "mann_whitney_SUV_vs_Sedan": test,
        "model": model,
    }
    (OUT_DIR / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=df.sample(min(2000, len(df)), random_state=201), x="Mileage", y="Price", hue="Body Type", alpha=.55, ax=ax, legend=False)
        ax.set(title="Listed price vs mileage", xlabel="Mileage (km)", ylabel="Listed price (AED)")
        fig.tight_layout()
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(FIGURES_DIR / "price_vs_mileage.png", dpi=300)
        plt.close(fig)
        fig, ax = plt.subplots(figsize=(9, 5))
        sns.boxplot(data=df, x="Year", y="Price", ax=ax, showfliers=False)
        ax.tick_params(axis="x", rotation=45)
        ax.set(title="Listed price by model year (outliers hidden for readability)", xlabel="Year", ylabel="Listed price (AED)")
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / "median_price_by_year.png", dpi=300)
        plt.close(fig)
        results["charts"] = "created"
    except ImportError as exc:
        create_svg_charts(df)
        results["charts"] = f"SVG fallback created; install matplotlib and seaborn for notebook-native plotting ({exc})"
    (OUT_DIR / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
