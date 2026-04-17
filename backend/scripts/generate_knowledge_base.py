from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from faker import Faker
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer


fake = Faker()


@dataclass(frozen=True)
class DocumentSpec:
    title: str
    department: str
    filename: str
    version: str
    owner_role: str
    access_level: str
    summary: str
    sections: list[dict[str, Any]]


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DocumentTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#16324F"),
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1B4965"),
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Subheading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#355070"),
            spaceBefore=6,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Meta",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#566573"),
            spaceAfter=4,
        )
    )
    return styles


def create_output_folders(root: Path) -> None:
    for folder_name in ["hr", "onboarding", "engineering", "sop", "operations", "faq"]:
        (root / folder_name).mkdir(parents=True, exist_ok=True)


def generate_content(spec: DocumentSpec) -> list[dict[str, Any]]:
    content = []
    for section in spec.sections:
        content.append({"type": "heading", "text": section["heading"]})
        for paragraph in section.get("paragraphs", []):
            content.append({"type": "paragraph", "text": paragraph})
        for subsection in section.get("subsections", []):
            content.append({"type": "subheading", "text": subsection["heading"]})
            for paragraph in subsection.get("paragraphs", []):
                content.append({"type": "paragraph", "text": paragraph})
            if subsection.get("bullets"):
                content.append({"type": "bullets", "items": subsection["bullets"]})
        if section.get("bullets"):
            content.append({"type": "bullets", "items": section["bullets"]})
    return content


def create_pdf(output_path: Path, spec: DocumentSpec, content: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=spec.title,
        author=metadata["owner"],
    )

    story = [
        Paragraph(spec.title, styles["DocumentTitle"]),
        Paragraph(spec.summary, styles["Body"]),
        Paragraph(
            (
                f"Department: {spec.department.title()} | Version: {metadata['version']} | "
                f"Owner: {metadata['owner']} | Access: {metadata['access_level']}"
            ),
            styles["Meta"],
        ),
        Paragraph(
            (
                f"Created: {metadata['created_date']} | Updated: {metadata['updated_date']} | "
                f"Source File: {metadata['source_filename']}"
            ),
            styles["Meta"],
        ),
        Spacer(1, 0.15 * inch),
    ]

    for item in content:
        if item["type"] == "heading":
            story.append(Paragraph(item["text"], styles["SectionHeading"]))
        elif item["type"] == "subheading":
            story.append(Paragraph(item["text"], styles["Subheading"]))
        elif item["type"] == "paragraph":
            story.append(Paragraph(item["text"], styles["Body"]))
        elif item["type"] == "bullets":
            bullet_items = [
                ListItem(Paragraph(text, styles["Body"]), leftIndent=10) for text in item["items"]
            ]
            story.append(
                ListFlowable(
                    bullet_items,
                    bulletType="bullet",
                    start="circle",
                    bulletFontName="Helvetica",
                    bulletFontSize=8,
                    leftIndent=16,
                )
            )
            story.append(Spacer(1, 0.06 * inch))

    doc.build(story)


def generate_metadata(spec: DocumentSpec) -> dict[str, Any]:
    created = fake.date_between(start_date=date(2024, 1, 8), end_date=date(2025, 12, 15))
    updated = fake.date_between(start_date=created, end_date=min(created + timedelta(days=180), date(2026, 4, 1)))
    return {
        "title": spec.title,
        "department": spec.department,
        "version": spec.version,
        "owner": f"{fake.name()}, {spec.owner_role}",
        "created_date": created.isoformat(),
        "updated_date": updated.isoformat(),
        "access_level": spec.access_level,
        "source_filename": spec.filename,
    }


def get_document_specs() -> list[DocumentSpec]:
    return [
        DocumentSpec(
            title="Leave and Time-Off Policy",
            department="hr",
            filename="hr_leave_policy_v1.pdf",
            version="1.0",
            owner_role="People Operations Manager",
            access_level="Internal - All Employees",
            summary="This policy defines how employees request, approve, and track paid time off, sick leave, and planned absences across the company.",
            sections=[
                {
                    "heading": "1. Purpose and Scope",
                    "paragraphs": [
                        "The Leave and Time-Off Policy establishes a consistent process for requesting, approving, and recording planned and unplanned absences. It applies to all full-time and part-time employees, with country-specific legal variations handled through local HR guidance.",
                        "The objective is to support employee well-being while ensuring managers can plan staffing, protect customer commitments, and maintain fair practices across departments.",
                    ],
                    "subsections": [
                        {
                            "heading": "Policy Coverage",
                            "paragraphs": [
                                "This document covers annual leave, sick leave, personal leave, bereavement leave, and unpaid leave arrangements approved by HR."
                            ],
                            "bullets": [
                                "Annual leave is accrued monthly and visible through the HRIS portal.",
                                "Sick leave may be used for the employee or an immediate dependent when care is required.",
                                "Unpaid leave requires both manager endorsement and HR approval before confirmation.",
                            ],
                        }
                    ],
                },
                {
                    "heading": "2. Leave Categories",
                    "subsections": [
                        {
                            "heading": "Annual Leave",
                            "paragraphs": [
                                "Employees are expected to plan annual leave in coordination with their manager. Teams should avoid overlapping absences during critical launch periods, quarter-end operations, or scheduled audit windows."
                            ],
                            "bullets": [
                                "Requests of 1-2 days should be submitted at least 3 business days in advance.",
                                "Requests of 3 or more consecutive days should be submitted at least 10 business days in advance.",
                                "Carryover limits are defined by local employment terms and reviewed each December.",
                            ],
                        },
                        {
                            "heading": "Sick Leave",
                            "paragraphs": [
                                "Employees who are unwell should notify their manager as early as possible on the same day. A medical note may be requested for repeated absences or when legally required."
                            ],
                            "bullets": [
                                "Managers may not ask employees to work while on sick leave unless the employee volunteers for a brief handoff.",
                                "Sensitive medical details should be shared only with HR when documentation is required.",
                            ],
                        },
                    ],
                },
                {
                    "heading": "3. Request and Approval Workflow",
                    "paragraphs": [
                        "All leave requests must be submitted through the HRIS system so payroll, team planning, and attendance reporting stay aligned. Email approvals alone are not considered final unless the request is entered in the system."
                    ],
                    "bullets": [
                        "Employee submits the request with dates, leave type, and a handoff note.",
                        "Manager reviews workload coverage and responds within 2 business days.",
                        "HR reviews exceptions, extended leave, and cross-border legal requirements.",
                        "Approved leave syncs automatically with the shared team calendar.",
                    ],
                },
                {
                    "heading": "4. Responsibilities",
                    "subsections": [
                        {
                            "heading": "Employee Responsibilities",
                            "bullets": [
                                "Plan leave early when possible and avoid informal last-minute requests.",
                                "Document critical handoffs for active tasks, customer commitments, and approvals.",
                                "Update out-of-office messages and emergency contacts before the leave begins.",
                            ],
                        },
                        {
                            "heading": "Manager Responsibilities",
                            "bullets": [
                                "Apply the policy consistently across the team.",
                                "Escalate unresolved staffing conflicts to HR before rejecting requests.",
                                "Protect employees from being contacted during approved leave except in genuine emergencies.",
                            ],
                        },
                    ],
                },
                {
                    "heading": "5. Exceptions and Compliance",
                    "paragraphs": [
                        "Country-specific leave entitlements, protected leave, and statutory notice requirements override this global baseline where local law requires different handling. HR maintains the authoritative local annexes and should be consulted before any policy exception is granted."
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="Code of Conduct and Workplace Behavior Policy",
            department="hr",
            filename="hr_code_of_conduct_v1.pdf",
            version="1.0",
            owner_role="Director of Human Resources",
            access_level="Internal - All Employees",
            summary="This document outlines expected standards for professional conduct, respectful collaboration, and ethical decision-making at work.",
            sections=[
                {
                    "heading": "1. Guiding Principles",
                    "paragraphs": [
                        "The company expects every employee, contractor, and manager to contribute to a workplace that is respectful, safe, and accountable. Professional behavior is not limited to office spaces and applies equally in remote work, chat tools, meetings, travel, and company events.",
                        "All team members are expected to act with integrity, treat colleagues fairly, and avoid conduct that undermines trust, inclusion, or employee safety.",
                    ],
                },
                {
                    "heading": "2. Expected Standards of Conduct",
                    "subsections": [
                        {
                            "heading": "Respectful Communication",
                            "bullets": [
                                "Use professional language in meetings, chat, email, and internal documentation.",
                                "Address disagreements through evidence, curiosity, and clear escalation paths.",
                                "Avoid dismissive comments, repeated interruptions, or exclusionary behavior.",
                            ],
                        },
                        {
                            "heading": "Ethical Decision-Making",
                            "bullets": [
                                "Report conflicts of interest that could affect hiring, vendor selection, or review processes.",
                                "Protect confidential company and employee information at all times.",
                                "Comply with legal, security, and privacy requirements when handling records or systems.",
                            ],
                        },
                    ],
                },
                {
                    "heading": "3. Prohibited Conduct",
                    "paragraphs": [
                        "The behaviors below are not compatible with company standards and may lead to disciplinary action. Managers must involve HR promptly when they observe or receive reports of serious misconduct."
                    ],
                    "bullets": [
                        "Harassment, discrimination, bullying, retaliation, or intimidation.",
                        "Unauthorized sharing of confidential company, employee, or customer information.",
                        "Abuse of company systems, credentials, procurement processes, or expense policies.",
                        "Threatening behavior, physical aggression, or deliberate damage to company property.",
                    ],
                },
                {
                    "heading": "4. Reporting Concerns",
                    "paragraphs": [
                        "Employees are encouraged to raise concerns early through their manager, HR, or the confidential ethics channel. Reports are reviewed as discreetly as possible, and retaliation against a person who raises a concern in good faith is prohibited.",
                        "Where a report involves a direct manager or a sensitive people issue, employees should use HR or the ethics channel rather than their normal reporting line.",
                    ],
                },
                {
                    "heading": "5. Investigation and Outcomes",
                    "paragraphs": [
                        "HR coordinates investigations with Legal, Security, and relevant department leaders when appropriate. Findings are based on interviews, documentation, system evidence, and consistency with policy expectations."
                    ],
                    "bullets": [
                        "Possible outcomes include coaching, written warning, restricted access, reassignment, or termination.",
                        "Managers are responsible for implementing any corrective actions assigned to their team.",
                        "Policy acknowledgements are tracked annually as part of compliance training.",
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="Employee Benefits Overview",
            department="hr",
            filename="hr_employee_benefits_v1.pdf",
            version="1.0",
            owner_role="Benefits Program Lead",
            access_level="Internal - All Employees",
            summary="This overview explains the company benefits package, enrollment process, and employee support resources.",
            sections=[
                {
                    "heading": "1. Benefits Philosophy",
                    "paragraphs": [
                        "The company offers a benefits program designed to support employee health, financial stability, and long-term career sustainability. Benefits are reviewed annually to remain competitive and aligned with business needs."
                    ],
                },
                {
                    "heading": "2. Core Benefits",
                    "subsections": [
                        {
                            "heading": "Health and Wellness",
                            "bullets": [
                                "Medical, dental, and vision plans for employees and eligible dependents.",
                                "Mental health support through confidential counseling sessions.",
                                "Annual wellness allowance for approved fitness or preventive care expenses.",
                            ],
                        },
                        {
                            "heading": "Financial Benefits",
                            "bullets": [
                                "Retirement contribution matching after eligibility requirements are met.",
                                "Life and disability insurance coverage through company-sponsored plans.",
                                "Home office stipend for remote employees and a refresh cycle for ergonomic equipment.",
                            ],
                        },
                    ],
                },
                {
                    "heading": "3. Enrollment Process",
                    "paragraphs": [
                        "New hires must complete benefits enrollment within 14 calendar days of their start date unless otherwise noted in local employment documents. Outside the enrollment window, changes are limited to qualifying life events such as marriage, birth, or relocation."
                    ],
                    "bullets": [
                        "Review plan summaries in the HRIS portal.",
                        "Select dependents, coverage tiers, and beneficiary information.",
                        "Upload any required supporting documentation before the deadline.",
                        "Confirm elections and download the enrollment summary for personal records.",
                    ],
                },
                {
                    "heading": "4. Employee Support and Escalations",
                    "paragraphs": [
                        "Employees who need help comparing plans, understanding payroll deductions, or resolving provider issues should contact the People Operations team. Complex escalations involving denied claims or cross-border portability are coordinated with the benefits broker."
                    ],
                    "bullets": [
                        "Standard benefits questions receive a response within 2 business days.",
                        "Urgent medical coverage gaps should be escalated to HR immediately.",
                        "Policy documents and carrier contacts are stored in the internal benefits portal.",
                    ],
                },
                {
                    "heading": "5. Annual Review Cycle",
                    "paragraphs": [
                        "Benefits changes for the upcoming plan year are communicated during open enrollment, typically in the fourth quarter. Employees are expected to review updated premiums, plan terms, and dependent information each cycle."
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="New Employee Guide",
            department="onboarding",
            filename="onboarding_new_employee_guide_v1.pdf",
            version="1.0",
            owner_role="Talent Enablement Lead",
            access_level="Internal - All Employees",
            summary="This guide helps new hires understand company expectations, key systems, and the support available during their first month.",
            sections=[
                {
                    "heading": "1. Welcome and First-Day Goals",
                    "paragraphs": [
                        "The first day should give new hires enough context to understand the company mission, operating model, and immediate team priorities. Managers and onboarding buddies are expected to help new hires feel confident navigating systems, communication norms, and team responsibilities."
                    ],
                    "bullets": [
                        "Attend the welcome orientation and review the company handbook.",
                        "Meet your manager, onboarding buddy, and immediate teammates.",
                        "Confirm access to email, chat, calendar, HRIS, and role-specific systems.",
                    ],
                },
                {
                    "heading": "2. Company Operating Basics",
                    "subsections": [
                        {
                            "heading": "How We Work",
                            "paragraphs": [
                                "Most teams operate with written updates, shared ownership, and clear handoffs. Decisions should be documented in project artifacts rather than relying on private chat or undocumented verbal agreements."
                            ],
                            "bullets": [
                                "Use project tickets to track deliverables and due dates.",
                                "Post weekly updates in the agreed team channel or meeting notes.",
                                "Escalate blockers early when they affect customer commitments or launch timelines.",
                            ],
                        },
                        {
                            "heading": "Communication Norms",
                            "bullets": [
                                "Use chat for short coordination, email for formal updates, and docs for decisions.",
                                "Assume positive intent, but be direct when raising risks or dependencies.",
                                "Document meeting outcomes with owners and dates instead of relying on memory.",
                            ],
                        },
                    ],
                },
                {
                    "heading": "3. First 30 Days Expectations",
                    "paragraphs": [
                        "Managers should define clear first-month outcomes for every new employee. Those outcomes typically include understanding core workflows, meeting key partners, and completing one scoped piece of work independently."
                    ],
                    "bullets": [
                        "Complete mandatory compliance and security training.",
                        "Review your department operating documents and current team roadmap.",
                        "Schedule introductory meetings with cross-functional partners relevant to your role.",
                        "Deliver one early contribution such as a bug fix, documentation update, process map, or analysis.",
                    ],
                },
                {
                    "heading": "4. Support Channels",
                    "paragraphs": [
                        "New hires should never be left guessing where to go for help. Questions about equipment, benefits, payroll, security, and team processes should be raised through the designated support channels so issues can be tracked and resolved quickly."
                    ],
                    "bullets": [
                        "People Operations for HR, payroll, and benefits questions.",
                        "IT Service Desk for laptop, access, or identity issues.",
                        "Your manager and onboarding buddy for role-specific guidance and context.",
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="First-Week Onboarding Checklist",
            department="onboarding",
            filename="onboarding_checklist_v1.pdf",
            version="1.0",
            owner_role="People Programs Manager",
            access_level="Internal - All Employees",
            summary="This checklist breaks the first week into concrete onboarding actions for new hires, managers, and support teams.",
            sections=[
                {
                    "heading": "1. Before Day One",
                    "bullets": [
                        "Manager confirms role goals, reporting line, and 30-day success plan.",
                        "IT prepares laptop, MFA enrollment, and baseline application access.",
                        "People Operations confirms signed documents, payroll setup, and orientation invite.",
                    ],
                },
                {
                    "heading": "2. Day One Checklist",
                    "subsections": [
                        {
                            "heading": "New Hire Tasks",
                            "bullets": [
                                "Log into email, calendar, chat, HRIS, and password manager.",
                                "Review orientation materials and complete identity verification steps.",
                                "Confirm emergency contact, tax, and bank details in the HR system.",
                            ],
                        },
                        {
                            "heading": "Manager Tasks",
                            "bullets": [
                                "Hold a 30-minute welcome meeting and review team priorities.",
                                "Explain how work is assigned, tracked, and reviewed within the team.",
                                "Set expectations for meeting cadence, communication norms, and escalation paths.",
                            ],
                        },
                    ],
                },
                {
                    "heading": "3. Days Two Through Five",
                    "paragraphs": [
                        "The remainder of the first week should blend structured learning with practical setup. Each new hire should leave the week knowing where critical documents live, how to ask for help, and what success looks like in the first month."
                    ],
                    "bullets": [
                        "Complete required security, privacy, and workplace conduct training.",
                        "Read the department handbook and related SOPs that apply to your role.",
                        "Join recurring team meetings and shadow at least one live workflow.",
                        "Document any missing access or unclear processes in the onboarding tracker.",
                    ],
                },
                {
                    "heading": "4. End-of-Week Review",
                    "paragraphs": [
                        "Managers should hold a short end-of-week check-in to review outstanding blockers, training progress, and next-week priorities. Gaps identified in the checklist should be assigned an owner and a due date rather than being left informal."
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="Account and Access Setup Process",
            department="onboarding",
            filename="onboarding_account_setup_process_v1.pdf",
            version="1.0",
            owner_role="IT Operations Lead",
            access_level="Internal - All Employees",
            summary="This process defines how new hires receive secure access to company tools, systems, and department-specific resources.",
            sections=[
                {
                    "heading": "1. Provisioning Principles",
                    "paragraphs": [
                        "Access is granted using least-privilege principles, role-based templates, and manager validation. No employee should receive production, finance, or personnel access without explicit business need and documented approval."
                    ],
                },
                {
                    "heading": "2. Standard Account Setup",
                    "bullets": [
                        "Create the employee identity in the identity provider using the approved naming convention.",
                        "Enroll the employee in multi-factor authentication before first login.",
                        "Provision baseline tools such as email, calendar, chat, HRIS, ticketing, and password manager access.",
                        "Assign device policies, endpoint protection, and approved browser profiles.",
                    ],
                },
                {
                    "heading": "3. Role-Based Access Requests",
                    "subsections": [
                        {
                            "heading": "Engineering Roles",
                            "bullets": [
                                "Source control, issue tracker, CI visibility, documentation portal, and development environment access.",
                                "Cloud and production permissions require separate approval through the access request workflow.",
                            ],
                        },
                        {
                            "heading": "Business Roles",
                            "bullets": [
                                "CRM, analytics dashboards, finance tools, or support systems based on job function.",
                                "Managers must review role bundles before submission to avoid over-provisioning.",
                            ],
                        },
                    ],
                },
                {
                    "heading": "4. Verification and Handoff",
                    "paragraphs": [
                        "IT validates the new hire can authenticate, access the approved tool set, and receive recovery communications before closing the request. Any exception must be documented in the ticket with a reason, expiry, and approver."
                    ],
                    "bullets": [
                        "New hire confirms successful login and MFA setup.",
                        "Manager confirms access is sufficient for the first week.",
                        "Open gaps are retained in the onboarding queue until resolved.",
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="API Development Guidelines",
            department="engineering",
            filename="engineering_api_guidelines_v1.pdf",
            version="1.0",
            owner_role="Staff Backend Engineer",
            access_level="Internal - Engineering",
            summary="These guidelines define the standards for designing, documenting, securing, and versioning internal and customer-facing APIs.",
            sections=[
                {
                    "heading": "1. Design Principles",
                    "paragraphs": [
                        "APIs should be designed for clarity, backward compatibility, and operational observability. Endpoint behavior must be predictable, documented, and consistent with shared service conventions so clients can integrate with confidence."
                    ],
                    "bullets": [
                        "Prefer resource-oriented URLs and explicit nouns over action-heavy endpoint names.",
                        "Return structured error responses with machine-readable codes and human-readable guidance.",
                        "Avoid introducing breaking changes without versioning or a documented migration plan.",
                    ],
                },
                {
                    "heading": "2. Request and Response Standards",
                    "subsections": [
                        {
                            "heading": "Request Design",
                            "bullets": [
                                "Validate payloads using explicit schemas and reject unknown critical fields when appropriate.",
                                "Support pagination, filtering, and sorting for list endpoints expected to grow over time.",
                                "Use idempotency controls for retry-sensitive operations such as payment or provisioning flows.",
                            ],
                        },
                        {
                            "heading": "Response Design",
                            "bullets": [
                                "Return stable identifiers, timestamps, and status fields for stateful resources.",
                                "Ensure error responses include correlation IDs that map to logs and traces.",
                                "Document field semantics so downstream teams do not infer behavior from examples alone.",
                            ],
                        },
                    ],
                },
                {
                    "heading": "3. Security and Compliance",
                    "paragraphs": [
                        "Every API must be reviewed for authentication, authorization, rate limits, and sensitive data handling before release. Teams are responsible for identifying data classification risks and ensuring logging does not expose secrets or protected content."
                    ],
                    "bullets": [
                        "Require authenticated access unless the endpoint is intentionally public and approved.",
                        "Apply authorization checks at the service boundary and again for sensitive resource operations.",
                        "Mask secrets, tokens, and personal data in logs, traces, and error reports.",
                    ],
                },
                {
                    "heading": "4. Documentation and Change Management",
                    "paragraphs": [
                        "APIs are not complete until their contracts and examples are published. Documentation must cover authentication requirements, sample payloads, expected errors, and any rollout caveats that matter to client teams."
                    ],
                    "bullets": [
                        "Publish an OpenAPI definition before beta release.",
                        "Add release notes for behavior changes, deprecations, and known limitations.",
                        "Notify impacted consumers before introducing schema changes that require client updates.",
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="Engineering Code Standards",
            department="engineering",
            filename="engineering_code_standards_v1.pdf",
            version="1.0",
            owner_role="Engineering Manager",
            access_level="Internal - Engineering",
            summary="This standard describes how engineering teams write, review, test, and maintain production code across services and applications.",
            sections=[
                {
                    "heading": "1. Code Quality Expectations",
                    "paragraphs": [
                        "Production code should be readable, testable, and straightforward for another engineer to maintain. Teams are expected to optimize for clarity over cleverness and to leave changed areas of the codebase in a better state than they found them."
                    ],
                    "bullets": [
                        "Use descriptive names, small functions, and explicit error handling.",
                        "Avoid dead code, hidden side effects, and unreviewed configuration drift.",
                        "Prefer incremental improvements that reduce complexity during feature work.",
                    ],
                },
                {
                    "heading": "2. Pull Request Standards",
                    "subsections": [
                        {
                            "heading": "Before Opening a PR",
                            "bullets": [
                                "Run formatting, linting, and relevant tests locally.",
                                "Update docs, API specs, or runbooks when behavior changes.",
                                "Break large changes into reviewable units whenever possible.",
                            ],
                        },
                        {
                            "heading": "During Review",
                            "bullets": [
                                "Summarize user impact, risks, rollout needs, and validation steps in the PR description.",
                                "Respond to review feedback with context, not just code changes.",
                                "Avoid merging without at least one informed reviewer unless an emergency process applies.",
                            ],
                        },
                    ],
                },
                {
                    "heading": "3. Testing Expectations",
                    "paragraphs": [
                        "Tests should reflect meaningful behavior, not implementation trivia. Engineers should add or update automated coverage for user-visible logic, failure paths, and integrations affected by the change."
                    ],
                    "bullets": [
                        "Use unit tests for isolated business logic and boundary conditions.",
                        "Use integration tests for persistence, service boundaries, and API behavior.",
                        "Document manual verification when automation is not yet practical.",
                    ],
                },
                {
                    "heading": "4. Operational Readiness",
                    "paragraphs": [
                        "Code is not production-ready unless it can be observed, supported, and rolled back safely. Services should expose useful logs, metrics, traces, and health signals before launch."
                    ],
                    "bullets": [
                        "Emit structured logs with request or job correlation identifiers.",
                        "Add alerts for critical failure modes and SLO-impacting conditions.",
                        "Prepare rollback steps for risky migrations or infrastructure changes.",
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="Service Deployment Process",
            department="engineering",
            filename="engineering_deployment_process_v1.pdf",
            version="1.0",
            owner_role="Platform Engineering Lead",
            access_level="Internal - Engineering",
            summary="This document defines the deployment lifecycle for services, from readiness review through post-release monitoring.",
            sections=[
                {
                    "heading": "1. Deployment Readiness",
                    "paragraphs": [
                        "Before a change is deployed, the owning engineer must confirm that the implementation has passed code review, required tests, and environment-specific checks. Risky releases should include a rollback plan and clear ownership during the rollout window."
                    ],
                    "bullets": [
                        "Confirm the PR is approved and linked to the release ticket.",
                        "Verify migrations, feature flags, and secret changes are coordinated.",
                        "Review dependencies on downstream systems, background jobs, and third-party APIs.",
                    ],
                },
                {
                    "heading": "2. Deployment Steps",
                    "bullets": [
                        "Trigger the deployment pipeline from the approved branch or release artifact.",
                        "Review automated checks for build integrity, migration safety, and environment parity.",
                        "Promote to staging, validate core flows, and confirm no new error spikes appear.",
                        "Deploy to production during the agreed release window with the designated owner present.",
                    ],
                },
                {
                    "heading": "3. Post-Deployment Validation",
                    "paragraphs": [
                        "The release owner remains accountable for post-deployment monitoring until the service is stable. Monitoring should include logs, traces, latency, error rates, and any KPI or business metric tied to the change."
                    ],
                    "bullets": [
                        "Check health endpoints and core user journeys within 15 minutes of release.",
                        "Review alerts, dashboards, and queue depths for regressions.",
                        "Communicate release completion or rollback status in the engineering release channel.",
                    ],
                },
                {
                    "heading": "4. Rollback Criteria",
                    "paragraphs": [
                        "A rollback should be executed quickly when a release causes user impact, data integrity risk, or sustained operational instability. Teams should not wait for perfect certainty when evidence indicates active harm."
                    ],
                    "bullets": [
                        "Roll back immediately for widespread request failures or authentication issues.",
                        "Pause rollout and escalate if data migrations produce inconsistent results.",
                        "Record the timeline, impact, and follow-up actions in the incident or release report.",
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="Deployment Standard Operating Procedure",
            department="sop",
            filename="sop_deployment_v1.pdf",
            version="1.0",
            owner_role="Release Manager",
            access_level="Internal - Operations and Engineering",
            summary="This SOP standardizes how production deployments are prepared, executed, communicated, and reviewed.",
            sections=[
                {
                    "heading": "1. Objective",
                    "paragraphs": [
                        "The purpose of this SOP is to reduce avoidable release risk by ensuring that deployment activities follow a standard sequence, include documented approvals, and produce consistent operational records."
                    ],
                },
                {
                    "heading": "2. Preconditions",
                    "bullets": [
                        "Release ticket approved and scoped to the planned change set.",
                        "Testing completed in lower environments with evidence attached to the release record.",
                        "Rollback plan prepared for high-risk changes involving schema, billing, or authentication behavior.",
                    ],
                },
                {
                    "heading": "3. Execution Steps",
                    "subsections": [
                        {
                            "heading": "Pre-Deployment",
                            "bullets": [
                                "Notify stakeholders of the release window and expected user impact, if any.",
                                "Verify on-call ownership and incident channel readiness.",
                                "Freeze unrelated changes if the release contains sensitive infrastructure updates.",
                            ],
                        },
                        {
                            "heading": "During Deployment",
                            "bullets": [
                                "Run the release checklist in real time and record start time, operator, and artifact version.",
                                "Watch health indicators during each stage instead of waiting until the end of the rollout.",
                                "Pause the release immediately if error rates, queue depth, or CPU saturation move outside thresholds.",
                            ],
                        },
                        {
                            "heading": "Post-Deployment",
                            "bullets": [
                                "Complete validation of critical paths and background processing.",
                                "Post a release summary with final status, known issues, and follow-up tasks.",
                                "Archive deployment notes for audit and incident reference.",
                            ],
                        },
                    ],
                },
                {
                    "heading": "4. Documentation Requirements",
                    "paragraphs": [
                        "All production deployments must leave behind a clear operational trail. This includes the release owner, time window, systems affected, observed issues, and whether rollback was required."
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="Incident Response Standard Operating Procedure",
            department="sop",
            filename="sop_incident_response_v1.pdf",
            version="1.0",
            owner_role="Site Reliability Manager",
            access_level="Internal - Operations and Engineering",
            summary="This SOP describes the response process for service incidents, from detection and triage through recovery and post-incident review.",
            sections=[
                {
                    "heading": "1. Incident Classification",
                    "paragraphs": [
                        "Incidents are classified by user impact, revenue risk, security implications, and time sensitivity. Severity should be assigned as soon as enough information is available to coordinate the right level of response."
                    ],
                    "bullets": [
                        "Severity 1: Major outage, severe customer impact, or security-critical event.",
                        "Severity 2: Significant degradation affecting a core workflow or a large customer segment.",
                        "Severity 3: Localized or moderate issue with a viable workaround.",
                    ],
                },
                {
                    "heading": "2. Immediate Response",
                    "bullets": [
                        "Acknowledge the alert and assign an incident commander.",
                        "Open the incident channel and incident record within 10 minutes of declaration.",
                        "Stabilize the system first, then deepen root cause analysis once impact is contained.",
                    ],
                },
                {
                    "heading": "3. Communication Protocol",
                    "paragraphs": [
                        "Internal updates should be frequent, concise, and time-stamped. External communications must be coordinated through the designated communications lead when customers or partners may notice service disruption."
                    ],
                    "bullets": [
                        "Post an initial internal summary with symptoms, suspected scope, and next actions.",
                        "Provide updates every 15 to 30 minutes for active high-severity incidents.",
                        "Document decisions, mitigations, and unresolved risks in the incident log.",
                    ],
                },
                {
                    "heading": "4. Recovery and Follow-Up",
                    "paragraphs": [
                        "The incident is only considered resolved when customer impact has ended and system health is stable. A post-incident review must capture the timeline, root cause, contributing factors, and preventive actions."
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="Data Backup and Recovery Standard Operating Procedure",
            department="sop",
            filename="sop_data_backup_v1.pdf",
            version="1.0",
            owner_role="Infrastructure Operations Manager",
            access_level="Internal - Restricted",
            summary="This SOP defines backup frequency, validation, retention, and recovery procedures for critical systems and business data.",
            sections=[
                {
                    "heading": "1. Backup Scope",
                    "paragraphs": [
                        "Backups are required for production databases, file storage containing regulated records, and configuration assets necessary for service restoration. Teams must maintain an inventory of systems covered by this SOP and review it quarterly."
                    ],
                },
                {
                    "heading": "2. Backup Schedule and Retention",
                    "bullets": [
                        "Daily incremental backups for operational databases and document stores.",
                        "Weekly full backups retained according to the applicable retention policy.",
                        "Encrypted off-site backup copies for critical recovery scenarios.",
                    ],
                },
                {
                    "heading": "3. Validation Requirements",
                    "paragraphs": [
                        "A backup is only useful if it can be restored. Infrastructure Operations performs scheduled restore tests, verifies integrity checks, and documents any exceptions or gaps in the backup review log."
                    ],
                    "bullets": [
                        "Run restore validation for one representative system each month.",
                        "Confirm backup completion alerts are routed to the operations queue.",
                        "Escalate repeated backup failures within the same business day.",
                    ],
                },
                {
                    "heading": "4. Recovery Procedure",
                    "bullets": [
                        "Confirm the recovery objective and the desired restore point with the incident lead.",
                        "Restore into a controlled environment first when time and risk profile allow.",
                        "Validate data completeness and application behavior before reopening user access.",
                        "Document the recovery timeline, data loss window, and approval to resume service.",
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="Operations Incident Management Guide",
            department="operations",
            filename="operations_incident_management_v1.pdf",
            version="1.0",
            owner_role="Operations Program Manager",
            access_level="Internal - Operations",
            summary="This guide explains how operations teams coordinate incidents, communicate updates, and hand off to specialist responders.",
            sections=[
                {
                    "heading": "1. Role of Operations During Incidents",
                    "paragraphs": [
                        "Operations acts as the coordination layer during many service incidents by ensuring records are complete, stakeholders are informed, and escalations happen on time. The operations lead does not replace the technical responder, but keeps the response organized and auditable."
                    ],
                },
                {
                    "heading": "2. Incident Handling Workflow",
                    "bullets": [
                        "Receive the alert, validate scope, and create the incident record.",
                        "Assign an operations coordinator for updates, timestamps, and stakeholder tracking.",
                        "Route the issue to the right technical owner based on affected system, severity, and business impact.",
                        "Maintain the communication cadence until the incident is resolved or handed over.",
                    ],
                },
                {
                    "heading": "3. Documentation Standards",
                    "paragraphs": [
                        "Operations records should be complete enough that another team can review the timeline without needing missing context from chat screenshots or memory. All major actions, decisions, and communications should be timestamped."
                    ],
                    "bullets": [
                        "Capture customer impact, detection source, and current severity.",
                        "Log each escalation, mitigation, and service recovery milestone.",
                        "Attach links to dashboards, tickets, or status updates used during the response.",
                    ],
                },
                {
                    "heading": "4. Handoff and Closure",
                    "paragraphs": [
                        "When operations hands off to engineering, security, or vendor teams, the handoff must include current impact, actions completed, pending decisions, and the next expected update time. Closure requires confirmation that communications are complete and follow-up actions are assigned."
                    ],
                },
            ],
        ),
        DocumentSpec(
            title="Operations Escalation Matrix",
            department="operations",
            filename="operations_escalation_matrix_v1.pdf",
            version="1.0",
            owner_role="Business Operations Director",
            access_level="Internal - Operations",
            summary="This matrix defines when and how operational issues are escalated across support, engineering, security, and leadership teams.",
            sections=[
                {
                    "heading": "1. Escalation Philosophy",
                    "paragraphs": [
                        "Escalations are intended to reduce response time, not to assign blame. Operations teams should escalate when a situation exceeds documented response thresholds, requires specialized expertise, or poses material customer, compliance, or revenue risk."
                    ],
                },
                {
                    "heading": "2. Escalation Triggers",
                    "bullets": [
                        "Customer-facing outage lasting more than 15 minutes without a viable workaround.",
                        "Repeated payment, identity, or provisioning failures affecting multiple accounts.",
                        "Security suspicion, data exposure concern, or privileged access anomaly.",
                        "Vendor dependency outage that blocks a core operational workflow.",
                    ],
                },
                {
                    "heading": "3. Escalation Paths",
                    "subsections": [
                        {
                            "heading": "Tiered Routing",
                            "bullets": [
                                "Tier 1: Service desk or operations triage for initial validation and ticket creation.",
                                "Tier 2: Department specialists such as engineering, finance systems, or HR operations.",
                                "Tier 3: Incident commander, security lead, or executive sponsor for critical events.",
                            ],
                        },
                        {
                            "heading": "Communication Expectations",
                            "bullets": [
                                "Each escalation must include summary, severity, business impact, actions taken, and requested support.",
                                "The receiving team should acknowledge ownership within the response target for the severity level.",
                            ],
                        },
                    ],
                },
                {
                    "heading": "4. Review and Governance",
                    "paragraphs": [
                        "The escalation matrix is reviewed quarterly by Operations, Engineering, and Security leadership to ensure contacts, thresholds, and response expectations remain accurate."
                    ],
                },
            ],
        ),
    ]


def build_faq_entries() -> list[dict[str, str]]:
    return [
        {"question": "How far in advance should I request annual leave?", "answer": "Submit 1-2 day leave requests at least 3 business days in advance and longer leave requests at least 10 business days in advance unless there is an emergency."},
        {"question": "Can I carry over unused annual leave into the next year?", "answer": "Carryover depends on your local employment terms and the year-end HR policy review. Check the HRIS balance rules or contact People Operations for your location."},
        {"question": "What should I do if I wake up sick and cannot work?", "answer": "Notify your manager as early as possible the same day and record the absence in the HRIS once you are able. HR may request documentation for extended or repeated sick leave."},
        {"question": "Where do I find information about medical and dental benefits?", "answer": "Plan summaries, payroll deduction details, and carrier contacts are available in the internal benefits portal and the HRIS benefits section."},
        {"question": "Who should I contact for a workplace conduct concern?", "answer": "You can raise concerns through your manager, HR, or the confidential ethics reporting channel. If the issue involves your manager, use HR or the ethics channel directly."},
        {"question": "What should I complete on my first day?", "answer": "You should log into core systems, complete orientation steps, verify payroll details, and meet your manager, onboarding buddy, and immediate teammates."},
        {"question": "How long do I have to enroll in benefits as a new hire?", "answer": "Most new hires must complete benefits enrollment within 14 calendar days of their start date unless local terms state otherwise."},
        {"question": "What access should every new hire receive by default?", "answer": "Baseline access usually includes email, calendar, chat, HRIS, ticketing, password manager, device security controls, and other tools required by the role template."},
        {"question": "Who approves department-specific access for a new hire?", "answer": "The hiring manager validates role-based access, and IT provisions it according to approved access templates and least-privilege rules."},
        {"question": "When should missing onboarding access be escalated?", "answer": "Missing access that blocks first-week tasks should be raised immediately through the IT or onboarding queue so it can be tracked and resolved with an owner."},
        {"question": "What makes an API ready for release?", "answer": "An API is release-ready when its schema is validated, authentication and authorization controls are in place, examples and error handling are documented, and required testing has passed."},
        {"question": "Should APIs return generic error messages?", "answer": "No. APIs should return structured errors with machine-readable codes, a clear explanation, and a correlation ID that maps to logs and traces."},
        {"question": "What is expected before I open an engineering pull request?", "answer": "Run formatting, linting, and relevant tests, update documentation if behavior changed, and make sure the change is small enough for a reviewer to evaluate clearly."},
        {"question": "When do I need integration tests instead of unit tests?", "answer": "Use integration tests when your change affects databases, service boundaries, external APIs, or end-to-end behavior that unit tests cannot validate realistically."},
        {"question": "What should I verify after a production deployment?", "answer": "Check service health, critical user flows, error rates, latency, queue depth, and any business metrics tied to the released change."},
        {"question": "When should a deployment be rolled back?", "answer": "Rollback should happen quickly when the release causes active customer impact, severe instability, authentication failures, or data integrity risk."},
        {"question": "What is the first action during a high-severity incident?", "answer": "Acknowledge the incident, assign an incident commander, create the incident record, and focus on stabilizing the system before deep root cause analysis."},
        {"question": "How often should teams post updates during an active incident?", "answer": "For active high-severity incidents, internal updates should usually be posted every 15 to 30 minutes with symptoms, actions, and next steps."},
        {"question": "What information belongs in an incident log?", "answer": "Include the timeline, severity, impacted systems, customer impact, decisions, mitigations, escalations, and the people responsible for each action."},
        {"question": "How often are production backups performed?", "answer": "Critical systems typically receive daily incremental backups and weekly full backups, with retention managed according to policy and regulatory needs."},
        {"question": "Why do we test backups with restore drills?", "answer": "Restore drills confirm that backups are usable, complete, and recoverable within the expected recovery objectives instead of just assuming the backups worked."},
        {"question": "When should operations escalate an issue beyond triage?", "answer": "Escalate when the issue exceeds response thresholds, affects multiple customers, introduces security or compliance risk, or requires specialist expertise."},
        {"question": "What should be included in an escalation message?", "answer": "Include a concise summary, severity, business impact, actions already taken, current blockers, and the specific support needed from the receiving team."},
        {"question": "Who owns communication during an operational incident?", "answer": "The assigned operations coordinator or incident commander owns communication cadence, while technical responders focus on diagnosis and recovery."},
        {"question": "What is the purpose of an onboarding buddy?", "answer": "An onboarding buddy helps a new hire navigate day-to-day questions, team norms, document locations, and informal workflow context during the first few weeks."},
        {"question": "Can managers approve leave over email without the HRIS request?", "answer": "No. Email can support discussion, but the request must be entered in the HRIS for it to count as a formal approval and be reflected in records."},
    ]


def write_metadata(root: Path, metadata_entries: list[dict[str, Any]]) -> None:
    metadata_path = root / "metadata.json"
    metadata_path.write_text(json.dumps(metadata_entries, indent=2), encoding="utf-8")


def write_faq(root: Path, faq_entries: list[dict[str, str]]) -> None:
    faq_path = root / "faq" / "faq_data.json"
    faq_path.write_text(json.dumps(faq_entries, indent=2), encoding="utf-8")


def main() -> None:
    from knowledge_base_generator_v2 import main as run_generator

    run_generator()


if __name__ == "__main__":
    main()
