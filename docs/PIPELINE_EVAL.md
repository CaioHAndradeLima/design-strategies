# Pipeline evaluation

Profile **`ci-design-eval`** scores synthetic architecture simulation:

- `success_rate` — golden checklist checks pass for `enterprise_multi_tenant`
- `reliability_score` — mean synthetic uptime fit across cases
- `compliance_checklist_pass_rate` — labeled compliance scenarios
- `fintech_fit_rate` — regulated workloads without negative controls
- `max_cost_index_p95` — tail FinOps index (via `cost_index_p95` on measure profiles)

Run:

```bash
design-lab evaluate-pipeline --profile ci-design-eval --output reports/measure-ci-design-eval.json
design-lab check-measure --profile ci-design-eval --report reports/measure-ci-design-eval.json
```