#!/usr/bin/env python3
"""One-off: add 15 AI-style questions (5 each) for the three underrepresented topics."""

from utils.questions import add_questions_bulk

QUESTIONS = [
    # ============================================================
    # Implementing CI/CD
    # ============================================================
    {
        "topic": "Implementing CI/CD",
        "subtopic": "Automation Bundle (DABs)",
        "objective": "Automation Bundle (DABs)",
        "source": "ai",
        "question": (
            "A data engineer has authored a Databricks Asset Bundle that defines two targets, "
            "`dev` and `prod`, in `databricks.yml`. After running `databricks bundle deploy` "
            "without any flags from the project root, the engineer notices that the resources "
            "were deployed to the `dev` workspace. Why did this happen?"
        ),
        "options": {
            "A": "DABs always deploy to the first target listed in the YAML file.",
            "B": "The `dev` target is configured with `mode: development` and is set as the default target.",
            "C": "`databricks bundle deploy` only deploys to non-production targets unless `--force` is supplied.",
            "D": "The active Databricks CLI profile automatically determines the target, and the profile pointed to dev.",
        },
        "correct_answer": "B",
        "explanation": (
            "When no `--target` flag is supplied, DABs use the target marked as default in `databricks.yml` "
            "(typically `dev` with `mode: development`, which also prefixes resources with the developer's "
            "username to isolate dev work). A is wrong — order in the file does not determine the default. "
            "C is invented — there is no production-protection flag like that on `deploy`. D is wrong — the "
            "CLI profile controls *which workspace* the bundle authenticates to, not which target is selected; "
            "target selection comes from `databricks.yml`, not the profile."
        ),
    },
    {
        "topic": "Implementing CI/CD",
        "subtopic": "Databricks Repos and Git integration",
        "objective": "Databricks Repos and Git integration",
        "source": "ai",
        "question": (
            "A team of data engineers wants to collaborate on a shared pipeline using Databricks Repos. "
            "Each engineer needs to work on features in isolation without affecting the main branch or "
            "each other's work. Which workflow is the recommended approach?"
        ),
        "options": {
            "A": "All engineers commit directly to the `main` branch of a single shared repo in the `/Repos/Shared` folder.",
            "B": "Each engineer clones the repo into their own user folder (e.g., `/Repos/<user>/<repo>`) and works on a personal feature branch, then opens a pull request in the Git provider to merge into `main`.",
            "C": "Engineers share one Repo and switch branches in it as needed, coordinating verbally so no two people edit the same branch at once.",
            "D": "Each engineer creates a new Git provider repository per feature, then merges them all at release time.",
        },
        "correct_answer": "B",
        "explanation": (
            "Databricks Repos are intended to be cloned per user — each engineer gets their own working copy "
            "in `/Repos/<user>/<repo>`, can check out a feature branch, and uses the Git provider (GitHub, "
            "GitLab, etc.) to open pull requests against `main`. This isolates working state and uses the Git "
            "provider for code review. A bypasses code review entirely. C causes conflicts because a Repo's "
            "checked-out branch is shared state — only one branch can be active at a time. D fragments history "
            "across repos and makes integration painful."
        ),
    },
    {
        "topic": "Implementing CI/CD",
        "subtopic": "Databricks CLI",
        "objective": "Databricks CLI",
        "source": "ai",
        "question": (
            "A data engineer is configuring the Databricks CLI on a fresh laptop and wants to authenticate "
            "against two different workspaces (dev and prod) so they can switch between them without "
            "re-entering credentials. What is the correct approach?"
        ),
        "options": {
            "A": "Run `databricks configure` once and then export `DATABRICKS_HOST` to switch workspaces.",
            "B": "Run `databricks configure --profile dev` and `databricks configure --profile prod`, then use `--profile <name>` (or `DATABRICKS_CONFIG_PROFILE`) per command.",
            "C": "Install two separate copies of the CLI, one per workspace, in different directories.",
            "D": "Authenticate once with a personal access token that has cross-workspace scope.",
        },
        "correct_answer": "B",
        "explanation": (
            "The Databricks CLI supports named profiles stored in `~/.databrickscfg`. Creating one profile "
            "per workspace and selecting it with `--profile <name>` (or via the `DATABRICKS_CONFIG_PROFILE` "
            "environment variable) is the standard way to manage multiple workspaces. A only changes the "
            "host, not the credentials — and overrides the profile system in an ad-hoc way. C is unnecessary "
            "and breaks the standard config file pattern. D is incorrect — personal access tokens are scoped "
            "to a single workspace; there is no cross-workspace PAT."
        ),
    },
    {
        "topic": "Implementing CI/CD",
        "subtopic": "Automation Bundle (DABs)",
        "objective": "Automation Bundle (DABs)",
        "source": "ai",
        "question": (
            "A data engineer wants to use the same `databricks.yml` to deploy a pipeline to dev and prod, "
            "but each environment must use a different catalog (`dev_catalog` vs `prod_catalog`) and a "
            "different job schedule. Which DABs feature should they use?"
        ),
        "options": {
            "A": "Maintain two separate bundle directories and copy resources between them before each deploy.",
            "B": "Define variables and per-target overrides in `databricks.yml`, referencing them as `${var.catalog}` in resource definitions.",
            "C": "Use environment variables exported in the shell before each `databricks bundle deploy` call.",
            "D": "Hard-code prod values in `databricks.yml` and use `sed` to substitute them for dev deploys in CI.",
        },
        "correct_answer": "B",
        "explanation": (
            "DABs natively support variables and per-target overrides — you declare a variable like `catalog` "
            "and override its value per target under `targets.<name>.variables`, then reference it as "
            "`${var.catalog}` throughout the bundle. A duplicates code and invites drift. C only works for a "
            "narrow set of substitutions and is not how DABs propagate config into resource definitions. "
            "D is brittle and exactly the anti-pattern DABs were created to eliminate."
        ),
    },
    {
        "topic": "Implementing CI/CD",
        "subtopic": "Databricks Repos and Git integration",
        "objective": "Databricks Repos and Git integration",
        "source": "ai",
        "question": (
            "Inside a Databricks Repo, a data engineer needs to perform several Git operations. "
            "Which operation CANNOT be performed from the Databricks Repos UI and must be done in the "
            "external Git provider (e.g., GitHub, GitLab)?"
        ),
        "options": {
            "A": "Creating a new branch from the current branch.",
            "B": "Committing and pushing local changes.",
            "C": "Creating and reviewing pull requests / merge requests.",
            "D": "Pulling the latest changes from the remote branch.",
        },
        "correct_answer": "C",
        "explanation": (
            "Databricks Repos support common Git operations directly in the workspace UI — creating "
            "branches, committing, pushing, pulling, and resolving simple conflicts. However, pull/merge "
            "request creation and code review are not part of Repos; those happen in the external Git "
            "provider's UI. A, B, and D are all supported in the Repos UI."
        ),
    },
    # ============================================================
    # Troubleshooting, Monitoring, and Optimization
    # ============================================================
    {
        "topic": "Troubleshooting, Monitoring, and Optimization",
        "subtopic": "Liquid Clustering and predictive optimization",
        "objective": "Liquid Clustering and predictive optimization",
        "source": "ai",
        "question": (
            "A data engineer manages a large Delta table that is filtered by `customer_id` in some "
            "queries and by `event_date` in others. The team frequently changes which columns matter "
            "as new dashboards are added. Which optimization strategy is best suited to this access pattern?"
        ),
        "options": {
            "A": "Partition the table by `event_date` and Z-ORDER by `customer_id` weekly.",
            "B": "Enable Liquid Clustering on `customer_id` and `event_date`.",
            "C": "Use bucketing on `customer_id` with 1024 buckets and rely on file pruning for date filters.",
            "D": "Run `OPTIMIZE` with no clustering or Z-Order — Delta will choose layout automatically.",
        },
        "correct_answer": "B",
        "explanation": (
            "Liquid Clustering is designed exactly for this case: multiple, evolving query predicates. Unlike "
            "static partitioning or one-shot Z-Order, clustering keys can be added/changed without rewriting "
            "the entire table, and the engine maintains data layout incrementally. A locks you into a "
            "partition column that may become wrong, and Z-Order requires expensive full re-clustering on "
            "changes. C is a Hive-era technique that does not optimize date predicates and is rarely the "
            "right answer on Delta. D leaves the data unclustered — `OPTIMIZE` alone just compacts files."
        ),
    },
    {
        "topic": "Troubleshooting, Monitoring, and Optimization",
        "subtopic": "Cluster startup failures",
        "objective": "Cluster startup failures",
        "source": "ai",
        "question": (
            "A scheduled job starts a new job cluster every morning. Last week it began failing at startup "
            "with the error `INSTANCE_UNREACHABLE` and a message that the cloud provider could not "
            "provision the requested instance type. What is the most likely root cause?"
        ),
        "options": {
            "A": "The Databricks workspace token has expired and must be rotated.",
            "B": "The cluster's init script is downloading a file from an unreachable URL.",
            "C": "The cloud account has hit its compute quota or the instance type is unavailable in the chosen region/AZ.",
            "D": "Unity Catalog is denying the cluster permission to access the metastore.",
        },
        "correct_answer": "C",
        "explanation": (
            "`INSTANCE_UNREACHABLE` paired with a 'cloud provider could not provision' message is a classic "
            "cloud-side capacity or quota issue — the instance type is exhausted in the chosen AZ or the "
            "account's vCPU quota is exceeded. The fix is to request a quota increase, switch instance "
            "family, or change region/AZ. A would surface as auth failures, not provisioning failures. B "
            "would surface only after the VM came up, with init-script-specific errors. D would manifest as "
            "metastore access errors at query time, not at cluster startup."
        ),
    },
    {
        "topic": "Troubleshooting, Monitoring, and Optimization",
        "subtopic": "Spark UI bottlenecks",
        "objective": "Spark UI bottlenecks",
        "source": "ai",
        "question": (
            "A data engineer investigating a slow Spark job opens the Spark UI and notices that the "
            "longest stage shows large numbers in the 'Shuffle Spill (Memory)' and 'Shuffle Spill (Disk)' "
            "columns for most tasks. What does this indicate, and what is the most appropriate first response?"
        ),
        "options": {
            "A": "The cluster is overloaded with concurrent jobs — pause other workloads.",
            "B": "Executors do not have enough memory to hold their shuffle data, so it is spilling to disk; increase executor memory or reduce the per-partition data size (e.g., by increasing the number of shuffle partitions).",
            "C": "The driver is the bottleneck — increase driver memory.",
            "D": "Network bandwidth between the executors and cloud storage is saturated; switch to a faster storage tier.",
        },
        "correct_answer": "B",
        "explanation": (
            "Shuffle spill columns explicitly track data that did not fit in executor memory during a shuffle "
            "and had to be written to disk (or serialized). The remedy is more executor memory or smaller "
            "partitions (typically by raising `spark.sql.shuffle.partitions`). A is unrelated to spill — that "
            "would manifest as resource starvation, not per-task spill metrics. C is wrong: shuffle spill is "
            "an executor-side phenomenon, not driver-side. D is wrong because shuffle spill is local "
            "memory-to-disk, not network I/O to cloud storage."
        ),
    },
    {
        "topic": "Troubleshooting, Monitoring, and Optimization",
        "subtopic": "Lakeflow Jobs UI",
        "objective": "Lakeflow Jobs UI",
        "source": "ai",
        "question": (
            "A multi-task Lakeflow Job has 6 tasks. Task 4 failed due to a transient external API outage, "
            "while tasks 1–3 succeeded and tasks 5–6 were skipped. The outage is resolved, and the engineer "
            "wants to rerun only task 4 and its downstream tasks 5 and 6, without re-executing the "
            "expensive tasks 1–3. What should they do?"
        ),
        "options": {
            "A": "Click 'Run now' on the job — Databricks will detect which tasks succeeded and skip them automatically.",
            "B": "Use 'Repair run' on the failed run and select the failed/skipped tasks; only those tasks will re-execute.",
            "C": "Manually delete tasks 1–3 from the job, run it, then add them back.",
            "D": "Clone the job, remove tasks 1–3 from the clone, and run the clone.",
        },
        "correct_answer": "B",
        "explanation": (
            "'Repair run' is the exact feature for this scenario. It reuses the original run context and "
            "re-executes only the failed (and optionally skipped) tasks, leaving successful task outputs in "
            "place. A is wrong — 'Run now' starts a new run and re-executes everything. C and D would work "
            "but are destructive/manual workarounds that are unnecessary because Repair run exists."
        ),
    },
    {
        "topic": "Troubleshooting, Monitoring, and Optimization",
        "subtopic": "Job performance monitoring",
        "objective": "Job performance monitoring",
        "source": "ai",
        "question": (
            "A team lead wants to analyze the runtime trends of all production jobs over the past 90 days "
            "(durations, failure counts, retries) using SQL, so they can build a Databricks SQL dashboard. "
            "Which data source is the most appropriate?"
        ),
        "options": {
            "A": "The Lakeflow Jobs UI — export each run page to CSV manually.",
            "B": "The Databricks REST API `/api/2.1/jobs/runs/list` called repeatedly from a notebook.",
            "C": "The `system.lakeflow` (or `system.workflow`) system tables, which expose job and run history as queryable tables.",
            "D": "The driver log files of each cluster, parsed with regex.",
        },
        "correct_answer": "C",
        "explanation": (
            "Databricks publishes job and run metadata into system tables (under the `system` catalog — "
            "e.g., `system.lakeflow.jobs`, `system.lakeflow.job_run_timeline`, etc.). These are queryable "
            "in SQL and are the canonical source for historical job analytics and dashboards. A is manual "
            "and does not scale. B works but is more work and rate-limited compared to direct SQL on system "
            "tables. D is a brittle, very-last-resort approach."
        ),
    },
    # ============================================================
    # Governance and Security
    # ============================================================
    {
        "topic": "Governance and Security",
        "subtopic": "Access controls (GRANT, REVOKE, DENY)",
        "objective": "Access controls (GRANT, REVOKE, DENY)",
        "source": "ai",
        "question": (
            "In Unity Catalog, a data engineer GRANTs `SELECT` on `sales.orders` to the group `analysts`. "
            "User `alice` is a member of `analysts`. The engineer then explicitly issues "
            "`DENY SELECT ON TABLE sales.orders TO alice;`. What is the effect when alice queries the table?"
        ),
        "options": {
            "A": "alice can still query the table — explicit GRANTs override DENYs.",
            "B": "alice receives a permission error — DENY overrides any inherited GRANT.",
            "C": "alice can query the table — DENY only blocks privileges that were granted directly to the principal, not inherited via a group.",
            "D": "alice can query the table, but only if she is the owner of the table.",
        },
        "correct_answer": "B",
        "explanation": (
            "In Unity Catalog, DENY is an explicit block that takes precedence over any GRANT — whether "
            "granted directly or inherited through group membership. Once `DENY SELECT` is issued on `alice`, "
            "she cannot SELECT from the table even though her group has SELECT. A is the inverse of the "
            "actual precedence rule. C is wrong — DENY applies regardless of whether the underlying GRANT "
            "came from a direct or group grant. D is unrelated; ownership doesn't bypass an explicit DENY "
            "on the principal."
        ),
    },
    {
        "topic": "Governance and Security",
        "subtopic": "Column-level masking and row-level security",
        "objective": "Column-level masking and row-level security",
        "source": "ai",
        "question": (
            "A data engineer needs to ensure that the `ssn` column in the `customers` table appears as "
            "`***-**-****` for all users except members of the `pii_readers` group. Which Unity Catalog "
            "feature is the most direct way to implement this?"
        ),
        "options": {
            "A": "Create a separate `customers_redacted` view and revoke SELECT on the base table for everyone except `pii_readers`.",
            "B": "Define a SQL UDF that returns the masked or unmasked value based on `is_account_group_member('pii_readers')`, then attach it as a column mask using `ALTER TABLE customers ALTER COLUMN ssn SET MASK <function>`.",
            "C": "Encrypt the `ssn` column at rest and give the encryption key only to `pii_readers`.",
            "D": "Use `DENY SELECT(ssn) ON TABLE customers` to everyone, and `GRANT SELECT(ssn)` only to `pii_readers`.",
        },
        "correct_answer": "B",
        "explanation": (
            "Unity Catalog supports column masks: a SQL UDF that takes the column value and returns either "
            "the original or a masked value, attached to the column with `ALTER TABLE ... ALTER COLUMN ... "
            "SET MASK`. The UDF can branch on `is_account_group_member(...)` to differentiate users. A works "
            "but duplicates objects and complicates governance. C confuses column masking with at-rest "
            "encryption — at-rest encryption is transparent to readers and doesn't satisfy the requirement. "
            "D would block the entire `ssn` column for non-members rather than showing a masked value, "
            "and column-level GRANT/DENY does not support the masked-vs-original presentation pattern."
        ),
    },
    {
        "topic": "Governance and Security",
        "subtopic": "Column-level masking and row-level security",
        "objective": "Column-level masking and row-level security",
        "source": "ai",
        "question": (
            "A data engineer wants users in the `eu_analysts` group to only see rows where "
            "`customer_region = 'EU'`, while users in `us_analysts` should only see rows where "
            "`customer_region = 'US'`. Both groups should query the same `customers` table without "
            "knowing about the filter. What is the appropriate Unity Catalog feature?"
        ),
        "options": {
            "A": "A row filter: a SQL UDF returning a boolean predicate, attached with `ALTER TABLE customers SET ROW FILTER <function> ON (customer_region)`.",
            "B": "Two materialized views, `customers_eu` and `customers_us`, with SELECT granted to each group.",
            "C": "A column mask on `customer_region` that returns NULL for the other region.",
            "D": "An ABAC policy that revokes SELECT on rows where `customer_region` does not match the user's tag.",
        },
        "correct_answer": "A",
        "explanation": (
            "Row-level security in Unity Catalog is implemented via row filters — SQL UDFs that return a "
            "boolean predicate evaluated against each row, attached to the table with `SET ROW FILTER`. "
            "The UDF can branch on `is_account_group_member(...)`. B works but requires per-region objects "
            "and grants; the question specifies querying the same table. C is wrong — masking a value to "
            "NULL does not remove rows, and users can still see the row count and other columns. D "
            "describes a plausible-sounding ABAC pattern but conflates row filtering with attribute-based "
            "access; ABAC policies govern access decisions, not per-row predicates inside a table."
        ),
    },
    {
        "topic": "Governance and Security",
        "subtopic": "ABAC policies",
        "objective": "ABAC policies",
        "source": "ai",
        "question": (
            "A data governance team wants to control access to hundreds of tables based on tags such as "
            "`sensitivity = 'pii'` rather than writing individual GRANT statements per table. What "
            "Unity Catalog capability addresses this?"
        ),
        "options": {
            "A": "Dynamic views that filter rows based on user attributes.",
            "B": "Attribute-Based Access Control (ABAC) policies that grant or deny privileges based on tags applied to securable objects (and optionally on principal attributes).",
            "C": "Row filters with a UDF that reads table comments to discover sensitivity.",
            "D": "Inheritance: granting SELECT at the catalog level so every tagged table is automatically governed.",
        },
        "correct_answer": "B",
        "explanation": (
            "ABAC in Unity Catalog lets you write policies that reference tags on securable objects (and "
            "principal attributes) instead of enumerating each table. Tag a table with "
            "`sensitivity = 'pii'`, then a policy can restrict it to a specific group across all such "
            "tables — exactly the scale-by-tag pattern described. A and C describe row-level features that "
            "do not address the 'hundreds of tables' scoping problem. D (catalog-level GRANT) is a coarse "
            "blanket approach that doesn't selectively gate on tags."
        ),
    },
    {
        "topic": "Governance and Security",
        "subtopic": "Managed vs external tables",
        "objective": "Managed vs external tables",
        "source": "ai",
        "question": (
            "A data engineer has an external Delta table in Unity Catalog whose underlying files live in a "
            "specific S3 bucket. The team has decided to migrate to managed tables for stronger lifecycle "
            "control and predictive optimization. Which approach correctly converts the external table to "
            "a managed table?"
        ),
        "options": {
            "A": "Run `ALTER TABLE ... SET TBLPROPERTIES ('managed' = 'true')` to flip the table from external to managed in place.",
            "B": "Drop the external table (which leaves the files intact) and recreate it as a managed table — Unity Catalog will automatically reuse the existing files at the same path.",
            "C": "Create a new managed table and copy the data into it (e.g., `CREATE TABLE managed_t AS SELECT * FROM external_t`), then drop the external table once verified. The new table's data lives in the metastore-managed storage location.",
            "D": "Move the underlying files into the metastore root storage path manually, then run `MSCK REPAIR TABLE`.",
        },
        "correct_answer": "C",
        "explanation": (
            "There is no in-place conversion between managed and external tables in Unity Catalog. The "
            "correct migration pattern is to create a new managed table and populate it via CTAS (or `INSERT "
            "INTO ... SELECT`), validate, then drop the original external table. The managed table's data "
            "is automatically stored in the metastore's (or catalog/schema's) managed storage location. A "
            "is fabricated — no such property exists. B is incorrect: dropping an external table leaves "
            "files in place, but a new managed table will not automatically adopt arbitrary external files "
            "and would have its own managed storage path. D conflates Hive-style file manipulation with "
            "Unity Catalog and is unsupported."
        ),
    },
]


def main() -> None:
    count = add_questions_bulk(QUESTIONS)
    print(f"Added {count} questions.")


if __name__ == "__main__":
    main()
