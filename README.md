# Customer Cohort Retention Analysis

## The Business Question

How many customers come back after their first transaction, and does that change over time?

A fintech business can acquire thousands of new customers every month. But acquisition alone does not build a sustainable business. The real question is whether those customers stick around. This analysis was built to answer that: of all the customers who transacted for the first time in a given month, how many returned 1, 2, 3... months later?

---

## What Was Done

Transaction data was pulled from a PostgreSQL database covering October 2024 to October 2025, 13 months of activity.

Each customer was assigned to a cohort based on the month of their **first transaction** (not their sign-up date). This ensures month 0 always represents 100% of the cohort, the baseline every other month is measured against.

From there, the pipeline calculates:
- How many months after their first transaction each customer returned
- What percentage of the original cohort was still active at each month
- A retention grid showing all cohorts side by side

The output is a heatmap where each row is a cohort month and each column is months since first transaction.

---

## What the Data Shows

**Retention drops sharply after month 0.** Across most cohorts, only 19 to 28% of customers return in month 1. This is the single biggest drop in the entire grid.

**After that initial drop, retention stabilises.** Cohorts from October to December 2024 hold between 16 and 27% consistently across months 2 to 11. There are effectively two types of customers in this data: those who never come back after their first transaction, and those who stick around for a long time. The business question worth asking is what separates them.

**More recent cohorts are retaining better at month 1.** The trend is notable:

| Cohort | Month 1 Retention |
|--------|------------------|
| 2024-10 | 19% |
| 2024-11 | 22% |
| 2025-03 | 26% |
| 2025-06 | 41% |
| 2025-07 | 42% |
| 2025-08 | 46% |

Month 1 retention has more than doubled between the October 2024 cohort and the August 2025 cohort. Something changed, whether that is product improvements, a different acquisition channel, or a shift in customer profile. This is worth investigating.

**The zeros on the right are expected.** Recent cohorts simply have not had enough time to reach those months yet. A 2025-09 cohort cannot have a month 6 retention rate in October 2025.

---

## What the Business Should Do Next

**1. Investigate the month 1 improvement.** The jump from about 20% to 46% retention at month 1 across 2025 cohorts is significant. If the business can identify what drove this and replicate it, it would have a direct impact on long-term revenue.

**2. Focus retention effort on the first 30 days.** Most churn happens between month 0 and month 1. A targeted re-engagement campaign in the first 30 days after a customer's first transaction would have the highest possible leverage.

**3. Revisit this analysis in Q1 2026.** The 2025 cohorts currently have incomplete data. Revisiting once they have 6 or more months of history will give a clearer picture of whether the retention improvement holds over time.

---

## Technical Overview

Built in Python using pandas, SQLAlchemy, seaborn, and PostgreSQL.

| File | What it does |
|------|-------------|
| `analytics.py` | Core pipeline functions, load, transform, calculate retention |
| `main.py` | Entry point, runs the full pipeline end to end |
| `raw.ipynb` | Exploratory notebook used to build and test the pipeline |
| `db_conn/` | Database connection module |

The pipeline is structured as four clean functions:

1. `load_tables()` loads one or more tables from the database
2. `generate_cohort()` assigns each customer to their first transaction cohort
3. `generate_retention_tbl()` calculates months since first transaction for every subsequent transaction
4. `generate_cohort_table()` merges cohort sizes, calculates retention rates, and pivots into the final grid
