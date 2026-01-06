# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

**DO NOT** report security vulnerabilities via public GitHub issues.

If you find a security vulnerability, please email `security@yedan.ai` (or the repository owner directly).

### What to Include

*   Description of the vulnerability.
*   Steps to reproduce.
*   Potential impact.

We will acknowledge receipt within 48 hours.

## Credentials & Secrets

This project uses `.env` files for configuration.
*   **NEVER** commit `.env.reactor` or any file containing real API keys.
*   **ALWAYS** use the provided `.env.example` as a template.
*   The `.gitignore` file is configured to exclude sensitive files.

## Automated Security

*   We use **SafetyGuard** (`modules/safety_guard.py`) to filter outputs.
*   We use **ScamGuard** (`scam_guard_worker.js`) to protect cloud endpoints.
