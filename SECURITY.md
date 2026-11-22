# Security policy

VITALINK v0.1 is a local research prototype, not a hardened multi-user service.

## Reporting

Report security issues privately to the repository maintainer through GitHub's private vulnerability reporting feature when available. Include a minimal reproduction and affected commit. Do not publish credentials or sensitive company data in a public issue.

## Current boundaries

- The API has no authentication or authorization.
- The dashboard is intended for local/demo deployment.
- No live ERP, supplier portal, payment, or purchase-order execution is connected.
- No sensitive operating data should be committed to this public repository.

Do not expose the demo service to untrusted networks or use it to make real purchasing commitments. Authentication, authorization, audit logging, input limits and deployment hardening are roadmap work.
