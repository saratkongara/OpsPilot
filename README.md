# OpsPilot
Ground Staff Allocation Engine using Google OR tools to handle constraints and optimization requirements

---

## 🎯 Optimization Objective: Strategy-Aware, Priority-Driven Assignment

The core goal of this scheduling optimizer is to **maximize total assignments** while favoring staff and service combinations that align with business priorities and operational preferences. The objective is dynamically adjusted based on a configurable strategy and incorporates both **service-level priorities** and **staff-based preferences**.

---

### ✅ Primary Goal: Maximize Total Assignments
At the heart of the objective function is the idea that every service assignment must be covered if possible. So the first priority is:

- **Maximize the total number of valid staff-to-service assignments.**

This ensures high utilization of staff and better service coverage.

---

### ✈️ Service-Level Prioritization
Each `ServiceAssignment` carries a `priority` score, which is a combined value of:

- **Flight priority**: e.g., international departures may have higher urgency.
- **Service priority**: e.g., fueling or boarding may be more time-critical than cabin cleaning.

These priorities are combined as a float (e.g., `22.05`), and **lower values are more important**. To reward high-priority assignments, the objective:

- Applies a **negative weighting to the priority**: lower priorities contribute **more** to the score.

```python
priority_score = -int(service_assignment.priority * 1000)
```

---

### 👩‍🔧 Staff-Based Prioritization
When multiple staff are eligible for the same assignment, the optimizer prefers staff based on the following hierarchy:

#### 1. 🎯 `priority_service_id` Match
Each staff member may indicate a strong preference for a specific `service_id` (e.g., they specialize in refueling). When such a match occurs:

- The assignment receives a **large bonus**, encouraging the optimizer to honor the staff's service preference **if possible**.

#### 2. 🧭 Rank Level (Seniority)
A staff member’s `rank_level` reflects their seniority or expertise. Lower values are better.

- Among equally qualified staff, those with **lower rank levels are preferred**, adding subtle bias toward more experienced workers.

#### 3. 🧰 Fewer Certifications
Staff with fewer certifications are **less flexible**, so it’s efficient to assign them where possible, preserving versatile staff for complex roles.

- Staff with **fewer certifications get a small bonus** to increase the likelihood of assignment.

---

### 🧠 Strategy-Driven Variants

The optimizer supports multiple strategies defined via `AssignmentStrategy`, which adjust secondary goals:

#### **`MINIMIZE_STAFF` Strategy**
- Main objective: **Assign as many services as possible**.
- Then: **Prefer higher-priority services and staff preferences**.
- Finally: **Minimize the number of staff used**, increasing operational efficiency.

```python
self.model.Maximize(
    1_000_000_000 * total_assignments +
    sum(weighted_objective_terms) -
    total_staff_used
)
```

#### **`BALANCE_WORKLOAD` Strategy**
- Main objective: **Assign as many services as possible**.
- Then: **Prefer higher-priority services and staff preferences**.
- Finally: **Encourage broader staff usage** to balance workload and reduce burnout.

```python
self.model.Maximize(
    1_000_000_000 * total_assignments +
    sum(weighted_objective_terms) +
    total_staff_used
)
```

---

### ⚙️ Summary of Objective Weights
| Component                   | Weight        | Purpose                                                |
|----------------------------|---------------|--------------------------------------------------------|
| Total assignments          | `1_000_000_000`| Most important: cover all services                     |
| Priority match bonus       | `10_000_000`   | Strongly prefer staff for their chosen service         |
| Service priority           | `10_000`       | Prefer high-priority flights and services              |
| Staff rank level           | `1_000`        | Prefer senior staff when equally qualified             |
| Fewer certifications       | `1`            | Prefer less flexible staff for simpler tasks           |
| Staff used (minimize/max) | `±1`           | Either minimize or balance number of staff used        |

> You can tweak these weights based on real-world constraints, KPIs, or business policies.

---

                         +--------------------------+
                         |   Start Optimization     |
                         +--------------------------+
                                     |
                                     v
                     +-------------------------------+
                     |  Generate assignment vars      |
                     |  (staff_id, service_id) → Bool |
                     +-------------------------------+
                                     |
                                     v
                   +-----------------------------------+
                   | Compute Total Assignments         |
                   |  total_assignments = sum(vars)    |
                   +-----------------------------------+
                                     |
                                     v
                   +------------------------------------+
                   | Compute Staff Usage                |
                   |  staff_used[staff_id] = max(assignments) |
                   +------------------------------------+
                                     |
                                     v
            +----------------------------------------------+
            | Score each assignment with priority weights  |
            | - Service priority (lower is better)         |
            | - Staff preference match (priority_service)  |
            | - Rank level (seniority)                     |
            | - Fewer certifications                       |
            +----------------------------------------------+
                                     |
                                     v
              +--------------------------------------+
              | Apply Strategy Decision Branch:      |
              |   - MINIMIZE_STAFF                   |
              |   - BALANCE_WORKLOAD                 |
              +--------------------------------------+
                    /                                      \
                   /                                        \
   +-------------------------------+         +-------------------------------+
   | MINIMIZE_STAFF                |         | BALANCE_WORKLOAD              |
   | ----------------------------  |         | ----------------------------  |
   | Maximize:                     |         | Maximize:                     |
   |   1. Total Assignments        |         |   1. Total Assignments        |
   |   2. Priority score           |         |   2. Priority score           |
   |   3. (-) Staff used count     |         |   3. (+) Staff used count     |
   +-------------------------------+         +-------------------------------+
                    \                                      /
                     \                                    /
                      \                                  /
                       +-------------------------------+
                       |      Set final objective      |
                       +-------------------------------+
                                     |
                                     v
                        +---------------------------+
                        |     Solve with OR-Tools    |
                        +---------------------------+
