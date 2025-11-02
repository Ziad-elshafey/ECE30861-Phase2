# CI Quick Reference Card

## 🚀 Quick Start

### Test CI Locally
```bash
# Run all checks locally before pushing
flake8 src tests --max-line-length=120
isort --check-only src tests
mypy src --ignore-missing-imports
pytest tests/ --cov=src --cov-report=term-missing
```

### Create Demo PR
```bash
git checkout -b demo/ci-test
echo 'def test_demo(): assert True' > tests/test_ci_demo.py
git add tests/test_ci_demo.py
git commit -m "feat: add CI demo test"
git push origin demo/ci-test
# Create PR on GitHub
```

---

## 📊 CI Pipeline Jobs

| # | Job Name | Purpose | Must Pass? |
|---|----------|---------|------------|
| 1 | Code Quality | Linting, formatting, types | No* |
| 2 | Unit Tests | Test suite (3.10, 3.11, 3.12) | **YES** |
| 3 | Database Tests | DB operations | **YES** |
| 4 | API Tests | Endpoint validation | **YES** |
| 5 | Security Scan | Vulnerability detection | No* |
| 6 | Build Summary | Status aggregation | Auto |

*Warnings only, doesn't block merge

---

## ✅ CI Triggers

- Pull requests to `main` or `develop`
- Pushes to `main` or `develop`
- Automatic re-run on new commits to PR

---

## 📈 Key Metrics

- **Jobs**: 6 parallel
- **Python Versions**: 3.10, 3.11, 3.12
- **Tests**: ~200+ cases
- **Coverage**: ~80% (min: 70%)
- **Runtime**: 2-5 minutes

---

## 🔗 Quick Links

- **Actions**: github.com/Ziad-elshafey/ECE30861-Phase2/actions
- **Workflow**: `.github/workflows/ci.yml`
- **Docs**: `docs/CI_CD_DOCUMENTATION.md`
- **Demo**: `docs/CI_DEMO_GUIDE.md`

---

## 📸 Screenshot Checklist

- [ ] PR with all checks passed
- [ ] Actions tab workflow view
- [ ] Code quality job logs
- [ ] Unit tests with coverage
- [ ] Database tests output
- [ ] API tests results
- [ ] Build summary
- [ ] Coverage HTML report
- [ ] Artifacts list

---

## 🎤 Demo Talking Points

1. "Automatic trigger on every PR"
2. "Tests across 3 Python versions"
3. "6 parallel jobs for speed"
4. "70% minimum coverage enforced"
5. "Failed tests block merging"
6. "2-5 minute feedback loop"
7. "Security scanning included"
8. "Coverage reports for developers"

---

## 🐛 Troubleshooting

**CI not triggering?**
- Check workflow file exists
- Verify PR targets main/develop
- Check GitHub Actions enabled

**Tests failing?**
- View logs in Actions tab
- Run tests locally first
- Check for missing dependencies

**Coverage too low?**
- Download HTML report artifact
- See which files need tests
- Add tests, push again

---

## 📝 Files Modified

```
.github/
  workflows/ci.yml          ← CI pipeline
  pull_request_template.md  ← PR template
docs/
  CI_CD_DOCUMENTATION.md    ← Full docs
  CI_DEMO_GUIDE.md          ← Demo steps
  CI_STATUS.md              ← Status page
README.md                   ← Updated
DELIVERABLE_CI.md           ← Submission doc
```

---

## ⚡ Fast Demo (5 minutes)

1. Show existing CI workflow file (1 min)
2. Create branch & add test file (1 min)
3. Create PR on GitHub (1 min)
4. Show CI running in Actions tab (1 min)
5. Show all checks passed (1 min)

---

**Need help?** See `docs/CI_DEMO_GUIDE.md`
