# CI/CD Pipeline Documentation

## Overview
Our CI/CD pipeline automates build, test, and deployment processes using Jenkins and GitHub Actions. Every code change goes through automated quality gates before reaching production.

## Pipeline Stages

### Stage 1: Code Quality
- **Linting**: ESLint for JavaScript, Pylint for Python, Checkstyle for Java
- **Static Analysis**: SonarQube scan for code smells, security vulnerabilities, and technical debt
- **Threshold**: Quality gate requires zero critical issues, coverage >= 80%

### Stage 2: Unit Tests
- **Backend**: Pytest with coverage report (target: 85% line coverage)
- **Frontend**: Jest with React Testing Library (target: 80% coverage)
- **Execution Time**: Unit tests must complete within 5 minutes
- **Failure Policy**: Pipeline stops if any unit test fails

### Stage 3: Integration Tests
- **Database Tests**: Test against PostgreSQL test instance with seeded data
- **API Tests**: Automated Postman collection run via Newman
- **Service Tests**: Docker Compose spins up dependent services
- **Execution Time**: Integration tests must complete within 15 minutes

### Stage 4: End-to-End Tests
- **Tool**: Cypress for web UI, Appium for mobile
- **Browsers**: Chrome, Firefox (headless mode in CI)
- **Scenarios**: Critical user journeys (login, search, checkout, payment)
- **Parallel Execution**: 3 parallel containers via Cypress Dashboard
- **Execution Time**: E2E tests must complete within 30 minutes

### Stage 5: Security Scanning
- **SAST**: SonarQube security rules
- **DAST**: OWASP ZAP scan against staging deployment
- **Dependency Scan**: Snyk for vulnerable npm/pip packages
- **Container Scan**: Trivy for Docker image vulnerabilities
- **Policy**: No critical or high vulnerabilities allowed in production

### Stage 6: Deployment
- **Staging**: Automatic deployment on merge to develop branch
- **Production**: Manual approval required after staging verification
- **Strategy**: Blue-green deployment with automatic rollback on health check failure
- **Rollback**: One-click rollback to previous version via Jenkins UI

## Environment Configuration

| Environment | Branch    | Auto-Deploy | URL                          |
|-------------|-----------|-------------|------------------------------|
| Dev         | feature/* | Yes         | dev.example.com              |
| Staging     | develop   | Yes         | staging.example.com          |
| Production  | main      | No (manual) | www.example.com              |

## Monitoring After Deployment
- **Health Check**: /api/health endpoint polled every 30 seconds
- **Error Rate**: Alert if 5xx error rate exceeds 1% in 5-minute window
- **Latency**: Alert if p99 latency exceeds 2 seconds
- **Rollback Trigger**: Automatic rollback if health check fails 3 consecutive times

## Troubleshooting Common Pipeline Failures

### Build Failures
- Check for missing dependencies in package.json or requirements.txt
- Verify Docker base image is accessible
- Check disk space on build agents

### Test Failures
- Review test logs in Jenkins console output
- Check test environment connectivity (database, external services)
- Look for flaky tests in the test stability report
- Re-run failed tests with --rerun-failures flag

### Deployment Failures
- Verify AWS credentials are not expired
- Check Kubernetes cluster health (kubectl get nodes)
- Review deployment manifests for syntax errors
- Check container registry for image availability

## Contact
- Pipeline issues: DevOps team (#devops-support on Slack)
- Test failures: QA team (#qa-automation on Slack)
- Security findings: Security team (security@example.com)
