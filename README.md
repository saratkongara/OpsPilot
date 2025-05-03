# ✈️ Ground Staff Scheduling Optimizer

This project implements a **strategy-aware, priority-driven optimization engine** for assigning airport ground staff to service tasks across flights. It uses **Google OR-Tools** to maximize service coverage while respecting flight priorities, staff preferences, and operational strategies like minimizing staff count or balancing workload.

---

## 🚀 Overview

Airports operate under strict timing constraints, and multiple below-the-wing services must be handled for each flight (e.g., refueling, cleaning, baggage loading). Each service:

- Has a **specific time window** based on flight schedule (e.g., A+5 to D-10).
- Requires **certified staff** with the right qualifications.
- Can have **varying urgency** based on flight type and service criticality.

This optimizer assigns staff to these services while maximizing overall efficiency and honoring configurable business strategies.

---

## 🎯 Optimization Objective: Strategy-Aware, Priority-Driven Assignment

The core goal is to **maximize total service coverage**, while factoring in business priorities and staff preferences.

### ✅ Primary Goal: Maximize Total Assignments

Ensure the highest number of valid assignments possible:

- `total_assignments = sum(staff_service_assignment_vars)`

This is the foundation of the optimization.

---

### ✈️ Service-Level Prioritization

Each `ServiceAssignment` has a `priority` value (e.g., `12.05`) where:

- **Lower priority value = more urgent or important.**
- Combines:
  - **Flight priority** (e.g., international > domestic).
  - **Service priority** (e.g., fueling > toilet cleaning).

To favor high-priority tasks:

```python
priority_score = -int(service_assignment.priority * 1000)
```

This ensures that lower values (i.e., more critical services) contribute more positively to the objective function.

---

### 👩‍🔧 Staff-Based Prioritization

The optimizer rewards desirable staff-service matches:

#### 1. 🎯 Preferred Service Match (`priority_service_id`)
If a staff member prefers a specific service (`priority_service_id`):

- A large **bonus** encourages satisfying that preference.

#### 2. 🧭 Staff Seniority (`rank_level`)
Staff with lower `rank_level` are more senior:

- Slight preference is given to senior workers when otherwise equal.

#### 3. 🧰 Fewer Certifications
Staff with fewer certifications are **less flexible**:

- Assigning them early helps preserve versatile staff for later.
- Slight bonus for such assignments.

---

## 🧠 Assignment Strategies

The optimizer supports multiple strategies via `AssignmentStrategy`:

### `MINIMIZE_STAFF`
- Goal: Cover all services using the **fewest number of staff**.
- Reduces operational cost and overstaffing.

```python
model.Maximize(
    1_000_000_000 * total_assignments +
    sum(weighted_scores) -
    total_staff_used
)
```

### `BALANCE_WORKLOAD`
- Goal: Cover all services while **distributing work more evenly**.
- Reduces burnout and increases fairness.

```python
model.Maximize(
    1_000_000_000 * total_assignments +
    sum(weighted_scores) +
    total_staff_used
)
```

> Staff usage is tracked via:
```python
staff_used[staff_id] = max(assignments involving staff_id)
```

---

## ⚙️ Objective Function Weights

| Component                   | Weight        | Purpose                                                |
|----------------------------|---------------|--------------------------------------------------------|
| Total assignments          | `1_000_000_000`| Most important: cover all services                     |
| Priority match bonus       | `10_000_000`   | Strongly prefer staff for their chosen service         |
| Service priority           | `10_000`       | Prefer high-priority flights and services              |
| Staff rank level           | `1_000`        | Prefer senior staff when equally qualified             |
| Fewer certifications       | `10`           | Prefer less flexible staff for simpler tasks           |
| Staff used (min/max)       | `±1`           | Encourage staff efficiency or fairness based on strategy|

You can tune these weights to match business policies or operational KPIs.

---

## 🧩 Optimization Flow (Text Summary)

1. Start optimization.
2. Generate boolean assignment variables for each (staff_id, service_assignment_id).
3. Compute total number of assignments.
4. Track whether each staff member is used.
5. Score each assignment based on:
   - Service priority (lower = better)
   - Staff's preferred service match
   - Staff seniority (lower rank_level = better)
   - Number of certifications (fewer = better)
6. Choose strategy:
   - `MINIMIZE_STAFF`: Cover services with fewest staff.
   - `BALANCE_WORKLOAD`: Cover services while distributing workload evenly.
7. Set objective function accordingly.
8. Solve the model with Google OR-Tools.

---

## ✅ Tests

Tests are written using `behave` and structured around constraint expectations and strategy outcomes.

```bash
behave
```

---

## 📚 References

- [Google OR-Tools](https://developers.google.com/optimization)
- Airport Ground Operations Standards (IATA/ACI)

---

## 🧠 Contributing

Contributions are welcome! Please file issues for bugs or enhancement requests, or submit a PR with clear explanations and test coverage.

---
