# Regression Testing Guide

## What is Regression Testing?
Regression testing ensures that recent code changes have not adversely affected existing functionality. It is a critical part of our CI/CD pipeline and is executed before every release.

## Regression Test Strategy

### When to Run Regression Tests
- Before every production release
- After any hotfix deployment
- When merging feature branches into main
- After database migrations
- After infrastructure changes (server upgrades, config changes)

### Test Prioritization
We use a risk-based approach to prioritize regression tests:

**Priority 1 - Smoke Tests (must pass before proceeding)**
- User login and authentication
- Homepage loading and navigation
- Product search functionality
- Add to cart and checkout flow
- Payment processing (see Payment Module Test Plan)

**Priority 2 - Core Business Logic**
- Order placement and tracking
- Inventory management updates
- User profile management
- Email notification delivery
- Coupon and discount application

**Priority 3 - Secondary Features**
- Wishlist functionality
- Product reviews and ratings
- Social media sharing
- Newsletter subscription
- Multi-language support

## Automated Regression Suite

### Tools and Framework
- **Test Framework**: Pytest with Selenium WebDriver
- **CI/CD**: Jenkins pipeline (Jenkinsfile in repo root)
- **Browser Coverage**: Chrome (latest), Firefox (latest), Safari (latest)
- **Parallel Execution**: 4 parallel threads using pytest-xdist
- **Reporting**: Allure reports generated after each run

### Running the Suite
```bash
# Full regression suite
pytest tests/regression/ --alluredir=reports/allure -n 4

# Smoke tests only
pytest tests/regression/ -m smoke --alluredir=reports/allure

# Specific module
pytest tests/regression/test_payment.py -v
```

### Test Configuration
- Base URL: Configured via environment variable `BASE_URL`
- Timeouts: Default wait 10 seconds, page load 30 seconds
- Screenshots: Captured on failure, stored in reports/screenshots/
- Video Recording: Enabled for critical path tests

## Manual Regression Checklist
For scenarios that cannot be fully automated:

1. [ ] Cross-browser visual consistency check
2. [ ] Mobile responsive layout verification (iOS Safari, Android Chrome)
3. [ ] Accessibility audit (screen reader, keyboard navigation)
4. [ ] Performance spot-check (page load under 3 seconds)
5. [ ] Third-party integration verification (payment gateway, shipping API)
6. [ ] Email template rendering across clients (Gmail, Outlook, Apple Mail)

## Test Environment Management
- **Staging**: Mirrors production, refreshed weekly from prod snapshot
- **QA**: Dedicated environment for exploratory testing
- **Dev**: Shared development environment, may be unstable
- **Data Reset**: Staging data resets every Sunday at 2 AM UTC

## Defect Reporting
When a regression test fails:
1. Verify the failure is reproducible
2. Check if it is a known issue in Jira
3. Create a bug report with: steps to reproduce, expected vs actual, screenshots, environment details
4. Tag with "regression" label and assign to the responsible team
5. Escalate P0/P1 bugs immediately to the release manager

## Metrics and KPIs
- **Pass Rate Target**: >= 98% for release approval
- **Execution Time**: Full suite under 45 minutes
- **Flaky Test Rate**: < 2% of total tests
- **Defect Escape Rate**: < 1 regression bug per release
