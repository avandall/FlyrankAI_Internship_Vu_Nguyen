# Performance Report: Database Indexing & EXPLAIN ANALYZE

We seeded the database with **10,000** job records and measured the query execution time of searching for a specific company (`'Flyrank AI'`) before and after adding a database index.

## Query Under Test
```sql
SELECT * FROM jobs WHERE company = 'Flyrank AI';
```

---

## 1. Before Creating the Index (Sequential Scan)

Without an index, PostgreSQL must scan every single row in the `jobs` table to check if the `company` matches the condition.

### SQL Explain Output
```sql
Seq Scan on jobs  (cost=0.00..144.50 rows=3 width=1588) (actual time=0.015..1.217 rows=1011 loops=1)
  Filter: ((company)::text = 'Flyrank AI'::text)
  Rows Removed by Filter: 8989
Planning Time: 0.816 ms
Execution Time: 1.307 ms
```

* **Scan Type**: `Seq Scan` (Sequential Scan / Full Table Scan)
* **Execution Time**: **1.307 ms**

---

## 2. Index Creation

We created a B-Tree index on the `company` column:
```sql
CREATE INDEX idx_jobs_company ON jobs (company);
```

---

## 3. After Creating the Index (Bitmap Index Scan)

With the index created, PostgreSQL uses a fast index lookup to find exactly which blocks contain the matching rows, avoiding scanning the entire table.

### SQL Explain Output
```sql
Bitmap Heap Scan on jobs  (cost=4.67..104.76 rows=50 width=1588) (actual time=0.091..0.275 rows=1011 loops=1)
  Recheck Cond: ((company)::text = 'Flyrank AI'::text)
  Heap Blocks: exact=136
  ->  Bitmap Index Scan on idx_jobs_company  (cost=0.00..4.66 rows=50 width=0) (actual time=0.077..0.077 rows=1011 loops=1)
        Index Cond: ((company)::text = 'Flyrank AI'::text)
Planning Time: 0.298 ms
Execution Time: 0.352 ms
```

* **Scan Type**: `Bitmap Index Scan` (using `idx_jobs_company`)
* **Execution Time**: **0.352 ms**

---

## Summary of Results

| Metric | Before Index (Seq Scan) | After Index (Bitmap Index Scan) | Performance Gain |
| :--- | :--- | :--- | :--- |
| **Planning Time** | 0.816 ms | 0.298 ms | ~2.7x faster |
| **Execution Time** | 1.307 ms | 0.352 ms | **~3.7x faster** |

*Note: For larger tables (e.g. 100,000+ or millions of rows), this difference will scale exponentially, saving significant CPU and disk resources.*
