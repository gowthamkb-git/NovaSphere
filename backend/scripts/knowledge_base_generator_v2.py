from __future__ import annotations

import json
from dataclasses import dataclass, field
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


Faker.seed(42)
fake = Faker()
fake.seed_instance(42)


@dataclass(frozen=True)
class SubsectionSpec:
    title: str
    paragraphs: list[str] = field(default_factory=list)
    bullets: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SectionSpec:
    title: str
    paragraphs: list[str] = field(default_factory=list)
    bullets: list[str] = field(default_factory=list)
    subsections: list[SubsectionSpec] = field(default_factory=list)


@dataclass(frozen=True)
class DocumentSpec:
    title: str
    department: str
    filename: str
    version: str
    owner_role: str
    access_level: str
    summary: str
    purpose: list[str]
    scope: list[str]
    scope_bullets: list[str]
    responsibilities: dict[str, list[str]]
    body_sections: list[SectionSpec]
    exception_guidance: list[str]
    records_and_review: list[str]


def sub(title: str, paragraphs: list[str] | None = None, bullets: list[str] | None = None) -> SubsectionSpec:
    return SubsectionSpec(title=title, paragraphs=paragraphs or [], bullets=bullets or [])


def section(
    title: str,
    paragraphs: list[str] | None = None,
    bullets: list[str] | None = None,
    subsections: list[SubsectionSpec] | None = None,
) -> SectionSpec:
    return SectionSpec(
        title=title,
        paragraphs=paragraphs or [],
        bullets=bullets or [],
        subsections=subsections or [],
    )


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DocumentTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#16324F"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1B4965"),
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Subheading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#355070"),
            spaceBefore=5,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Meta",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=10.5,
            textColor=colors.HexColor("#566573"),
            spaceAfter=3,
        )
    )
    return styles


def create_output_folders(root: Path) -> None:
    for folder_name in ["hr", "onboarding", "engineering", "sop", "operations", "faq"]:
        (root / folder_name).mkdir(parents=True, exist_ok=True)


def numbered_sections(spec: DocumentSpec) -> list[SectionSpec]:
    standard_sections = [
        section("Purpose", paragraphs=spec.purpose),
        section("Scope", paragraphs=spec.scope, bullets=spec.scope_bullets),
        section(
            "Responsibilities",
            paragraphs=[
                "The responsibilities below define who must act, approve, review, and maintain records so the process can be executed consistently across teams and audit periods."
            ],
            subsections=[
                sub(role, bullets=duties) for role, duties in spec.responsibilities.items()
            ],
        ),
    ]
    closing_sections = [
        section("Exceptions and Escalation", paragraphs=spec.exception_guidance),
        section("Records and Review", paragraphs=spec.records_and_review),
    ]
    return standard_sections + spec.body_sections + closing_sections


def generate_content(spec: DocumentSpec) -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = []
    for section_index, sec in enumerate(numbered_sections(spec), start=1):
        section_number = f"{section_index}.0"
        content.append({"type": "heading", "text": f"{section_number} {sec.title}"})
        for paragraph in sec.paragraphs:
            content.append({"type": "paragraph", "text": paragraph})
        if sec.bullets:
            content.append({"type": "bullets", "items": sec.bullets})
        for subsection_index, subsection in enumerate(sec.subsections, start=1):
            subsection_number = f"{section_index}.{subsection_index}"
            content.append({"type": "subheading", "text": f"{subsection_number} {subsection.title}"})
            for paragraph in subsection.paragraphs:
                content.append({"type": "paragraph", "text": paragraph})
            if subsection.bullets:
                content.append({"type": "bullets", "items": subsection.bullets})
    return content


def text_word_count(spec: DocumentSpec) -> int:
    parts = [spec.summary]
    parts.extend(spec.purpose)
    parts.extend(spec.scope)
    parts.extend(spec.scope_bullets)
    parts.extend(spec.exception_guidance)
    parts.extend(spec.records_and_review)
    for duties in spec.responsibilities.values():
        parts.extend(duties)
    for sec in spec.body_sections:
        parts.extend(sec.paragraphs)
        parts.extend(sec.bullets)
        for subsection in sec.subsections:
            parts.extend(subsection.paragraphs)
            parts.extend(subsection.bullets)
    return sum(len(part.split()) for part in parts)


def validate_document_specs(specs: list[DocumentSpec]) -> None:
    if len(specs) != 14:
        raise ValueError(f"Expected 14 document specs, found {len(specs)}")
    for spec in specs:
        word_count = text_word_count(spec)
        if word_count < 800:
            raise ValueError(f"{spec.filename} is below the 800-word minimum at {word_count} words")


def _draw_page_chrome(canvas, doc, spec: DocumentSpec, metadata: dict[str, Any]) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D5DBDB"))
    canvas.setFillColor(colors.HexColor("#5D6D7E"))
    canvas.setFont("Helvetica", 8)
    canvas.line(doc.leftMargin, A4[1] - 34, A4[0] - doc.rightMargin, A4[1] - 34)
    canvas.drawString(doc.leftMargin, A4[1] - 24, f"{spec.title} | Version {metadata['version']}")
    canvas.drawRightString(A4[0] - doc.rightMargin, A4[1] - 24, metadata["access_level"])
    canvas.line(doc.leftMargin, 28, A4[0] - doc.rightMargin, 28)
    canvas.drawString(doc.leftMargin, 16, "Internal Company Knowledge Base")
    canvas.drawRightString(A4[0] - doc.rightMargin, 16, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def create_pdf(output_path: Path, spec: DocumentSpec, content: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.55 * inch,
        title=spec.title,
        author=metadata["owner"],
    )

    story = [
        Paragraph(spec.title, styles["DocumentTitle"]),
        Paragraph(spec.summary, styles["Body"]),
        Paragraph(
            (
                f"Department: {spec.department.title()} | Version: {metadata['version']} | "
                f"Owner: {metadata['owner']}"
            ),
            styles["Meta"],
        ),
        Paragraph(
            (
                f"Access Level: {metadata['access_level']} | Created: {metadata['created_date']} | "
                f"Updated: {metadata['updated_date']} | Source File: {metadata['source_filename']}"
            ),
            styles["Meta"],
        ),
        Spacer(1, 0.1 * inch),
    ]

    for item in content:
        if item["type"] == "heading":
            story.append(Paragraph(item["text"], styles["SectionHeading"]))
        elif item["type"] == "subheading":
            story.append(Paragraph(item["text"], styles["Subheading"]))
        elif item["type"] == "paragraph":
            story.append(Paragraph(item["text"], styles["Body"]))
        elif item["type"] == "bullets":
            bullet_items = [ListItem(Paragraph(text, styles["Body"]), leftIndent=10) for text in item["items"]]
            story.append(
                ListFlowable(
                    bullet_items,
                    bulletType="bullet",
                    bulletFontName="Helvetica",
                    bulletFontSize=8,
                    leftIndent=16,
                )
            )
            story.append(Spacer(1, 0.04 * inch))

    doc.build(
        story,
        onFirstPage=lambda canvas, document: _draw_page_chrome(canvas, document, spec, metadata),
        onLaterPages=lambda canvas, document: _draw_page_chrome(canvas, document, spec, metadata),
    )


def generate_metadata(spec: DocumentSpec) -> dict[str, Any]:
    created = fake.date_between(start_date=date(2024, 1, 8), end_date=date(2025, 12, 15))
    updated = fake.date_between(start_date=created, end_date=min(created + timedelta(days=160), date(2026, 4, 1)))
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


def hr_documents() -> list[DocumentSpec]:
    return [
        DocumentSpec(
            title="Leave and Time-Off Policy",
            department="hr",
            filename="hr_leave_policy_v1.pdf",
            version="1.1",
            owner_role="People Operations Manager",
            access_level="Internal - All Employees",
            summary="This policy sets the enterprise standard for planned leave, unscheduled absence reporting, approvals, workforce coverage, and the records required for compliant payroll and attendance management.",
            purpose=[
                "This policy exists so employees can take time away from work in a predictable, fair, and well-documented manner without creating avoidable service disruption for customers or internal teams. A production-grade knowledge base should answer not only whether leave is available, but also how the process is executed, what approvals are required, and what records support compliance and payroll accuracy.",
                "The document aligns People Operations, line managers, and employees on a shared operating model. It clarifies planning expectations, defines same-day reporting requirements for unplanned absence, and explains how exceptions are handled when legal obligations, business continuity needs, or employee health concerns require additional coordination.",
            ],
            scope=[
                "The policy applies to full-time and part-time employees across the company. Country-specific annexes may provide additional entitlements or legal protections, but the workflow in this document remains the default operating model unless local HR guidance explicitly overrides it.",
                "The policy covers annual leave, sick leave, personal leave, bereavement leave, unpaid leave, and manager-approved short absences recorded through the HR information system. It also governs the handoff, scheduling, calendar management, and approval documentation that accompany leave requests.",
            ],
            scope_bullets=[
                "Covers leave request submission, approval timing, absence recording, and handoff expectations.",
                "Applies to remote, hybrid, and office-based employees unless local law requires different handling.",
                "Does not replace statutory leave obligations, medical accommodation processes, or protected leave rules.",
            ],
            responsibilities={
                "Employees": [
                    "Plan foreseeable leave early enough for workload coverage to be arranged and documented.",
                    "Submit complete requests in the HRIS with dates, leave type, and a concise work handoff summary.",
                    "Notify the manager promptly for same-day illness or emergency absence and update the system when able.",
                ],
                "Managers": [
                    "Review requests consistently, balance fairness with business continuity, and respond within the defined service level.",
                    "Ensure critical customer deliverables, approvals, and on-call coverage are handed off before leave begins.",
                    "Escalate complex or potentially inconsistent decisions to People Operations before rejecting a request.",
                ],
                "People Operations": [
                    "Maintain policy interpretation, local annex guidance, and audit-ready leave records.",
                    "Support exceptions involving extended leave, statutory obligations, or repeated attendance issues.",
                    "Monitor trends, carryover usage, and policy adherence across departments.",
                ],
            },
            body_sections=[
                section(
                    "Leave Categories",
                    paragraphs=[
                        "Annual leave is intended for planned rest, personal commitments, and longer breaks from work. Teams are expected to coordinate around known peak periods such as launches, quarter-close activities, or audit windows, but vacation planning should remain practical and employee-friendly rather than restrictive by default.",
                        "Sick leave is intended for an employee's illness, recovery, medical consultation, or the short-term care of an immediate dependent where local policy permits. Managers should prioritize employee well-being and should not ask an unwell employee to continue working except for a brief voluntary handoff when necessary to prevent active operational risk.",
                    ],
                    subsections=[
                        sub(
                            "Annual Leave Controls",
                            paragraphs=[
                                "Annual leave balances accrue according to contract terms and are displayed in the HRIS. Employees should avoid relying on informal approvals in chat or email because payroll, attendance, and manager visibility depend on the request being formally recorded in the system."
                            ],
                            bullets=[
                                "Requests for one or two days should normally be submitted at least three business days in advance.",
                                "Requests for three or more consecutive days should normally be submitted at least ten business days in advance.",
                                "Year-end carryover is governed by local terms and reviewed by People Operations each December.",
                            ],
                        ),
                        sub(
                            "Sick, Personal, and Unpaid Leave",
                            paragraphs=[
                                "Unplanned leave must be reported as early as possible on the day of absence so workload can be reassigned responsibly. Extended unpaid leave requires a documented business and HR review because payroll, benefits, and statutory implications may apply."
                            ],
                            bullets=[
                                "Medical documentation may be requested where legally allowed for repeated or extended absence.",
                                "Sensitive medical details should be shared only with People Operations when documentation is required.",
                                "Unpaid leave is not final until both manager and HR approval are recorded.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Request and Approval Workflow",
                    paragraphs=[
                        "The leave workflow is designed to create a single source of truth for staffing, payroll, and employee scheduling. Email or chat can be used for early coordination, but the HRIS record is the authoritative approval trail and must reflect the final dates, leave category, and any exception approval.",
                    ],
                    bullets=[
                        "Employee submits request with dates, leave type, and coverage notes.",
                        "Manager validates business impact, overlapping leave, and required handoffs within two business days.",
                        "People Operations reviews extended leave, policy exceptions, and local legal implications where applicable.",
                        "Approved leave syncs with the team calendar and becomes part of attendance reporting.",
                    ],
                ),
                section(
                    "Coverage Planning and Exception Handling",
                    paragraphs=[
                        "Leave planning should not depend on tribal knowledge. Before extended time away, employees should identify active tasks, pending approvals, customer commitments, and escalation contacts so another team member can manage urgent items without recreating context under pressure.",
                        "Managers should not deny leave simply because planning was not done early. Instead, they should work with the employee to resolve coverage gaps, escalate real conflicts, and document the reason for any exception decision so the same standard can be applied consistently across the team.",
                    ],
                    bullets=[
                        "Use a written handoff for high-risk tasks, customer deadlines, and approval dependencies.",
                        "Escalate staffing conflicts that cannot be resolved fairly within the team.",
                        "Document the reason for any exception approval or denial in the HRIS notes field.",
                    ],
                ),
            ],
            exception_guidance=[
                "Country-specific statutory leave, protected leave, and accommodation processes override this baseline where required by law. When a request intersects with a legal protection, managers must pause local interpretation and involve People Operations before confirming the final decision.",
                "Escalations are required when leave conflicts affect customer commitments, repeat attendance patterns suggest a broader issue, or employees raise a concern about inconsistent policy application. The objective is to resolve issues through evidence and policy guidance rather than manager discretion alone.",
            ],
            records_and_review=[
                "The HRIS record is the official source for request status, dates, approvals, and manager notes. Supporting attachments, including required documentation for extended leave, should be stored according to retention and privacy requirements.",
                "People Operations reviews leave utilization, approval timeliness, and year-end carryover data on a quarterly basis. Policy language is reviewed annually or sooner if local law, payroll processes, or business continuity requirements materially change.",
            ],
        ),
        DocumentSpec(
            title="Code of Conduct and Workplace Behavior Policy",
            department="hr",
            filename="hr_code_of_conduct_v1.pdf",
            version="1.1",
            owner_role="Director of Human Resources",
            access_level="Internal - All Employees",
            summary="This policy describes expected professional behavior, decision-making standards, reporting channels, and investigation principles that support a safe and respectful workplace.",
            purpose=[
                "The code of conduct establishes a consistent enterprise standard for respectful communication, ethical decision-making, protection of confidential information, and appropriate workplace behavior across every function of the company. In a production-level knowledge base, employees should be able to retrieve both the expected standard and the action to take when something goes wrong.",
                "The policy is designed to reduce ambiguity in difficult situations. It explains the conduct that is required, the conduct that is prohibited, and the practical reporting routes employees can use when they need help, witness misconduct, or believe a decision may conflict with company values, legal obligations, or employee safety.",
            ],
            scope=[
                "This policy applies to employees, contractors, interns, managers, and executives in all work settings, including remote collaboration, meetings, travel, chat channels, email, company events, and interactions with customers, candidates, partners, and vendors.",
                "The policy covers both daily collaboration norms and serious misconduct concerns. It should be read alongside information security policies, anti-harassment requirements, expense rules, and local employment law guidance where additional obligations exist.",
            ],
            scope_bullets=[
                "Applies to in-person, virtual, and travel-related work interactions.",
                "Covers verbal conduct, written conduct, system usage, and decision-making behavior.",
                "Requires escalation to HR, Security, or Legal when a matter creates safety, privacy, or compliance risk.",
            ],
            responsibilities={
                "All Personnel": [
                    "Communicate respectfully, protect confidential information, and raise concerns in good faith when something appears unsafe or inappropriate.",
                    "Avoid retaliatory behavior, conflicts of interest, or misuse of systems, privileges, or company resources.",
                    "Cooperate honestly with fact-finding, policy reviews, or required compliance training.",
                ],
                "Managers": [
                    "Model the expected standard in daily communication, feedback, and decision-making.",
                    "Respond promptly to reported concerns and involve HR rather than attempting to resolve serious matters informally.",
                    "Protect employees from retaliation and ensure corrective actions are implemented when required.",
                ],
                "Human Resources": [
                    "Maintain the policy, guide investigations, and coordinate with Legal or Security when needed.",
                    "Provide confidential reporting routes and protect sensitive records according to retention requirements.",
                    "Track themes, policy acknowledgements, and remediation activities for governance review.",
                ],
            },
            body_sections=[
                section(
                    "Expected Standards of Conduct",
                    paragraphs=[
                        "Professional behavior includes how people disagree, not just how they agree. Employees are expected to discuss tradeoffs directly, challenge ideas with evidence, and avoid sarcasm, exclusion, intimidation, or repeated dismissive behavior that undermines participation or psychological safety.",
                        "Ethical conduct also includes stewardship of systems and information. Employees should use company assets only for authorized work purposes, avoid conflicts of interest in hiring or vendor decisions, and protect sensitive internal, employee, and customer information from unauthorized disclosure.",
                    ],
                    subsections=[
                        sub(
                            "Respectful Communication",
                            bullets=[
                                "Use clear, professional language in meetings, chat, documentation, and email.",
                                "Address disagreements through evidence, decision records, and escalation paths rather than personal attacks.",
                                "Create space for others to contribute and avoid interrupting, humiliating, or excluding colleagues.",
                            ],
                        ),
                        sub(
                            "Ethical and Secure Conduct",
                            bullets=[
                                "Disclose actual or perceived conflicts of interest before participating in a decision.",
                                "Handle confidential records only through approved systems and workflows.",
                                "Follow legal, privacy, and security requirements whenever sensitive information is involved.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Prohibited Conduct and Risk Indicators",
                    paragraphs=[
                        "The company treats harassment, discrimination, bullying, retaliation, threats, deliberate privacy violations, and abuse of system access as serious policy breaches. Repeated low-grade behavior can also become misconduct when it creates a hostile or exclusionary environment over time.",
                        "Managers should not wait for absolute certainty before escalating a serious concern. If a behavior pattern raises safety, privacy, or retaliation risk, the matter should be referred to HR promptly so evidence can be preserved and the response can be proportionate, consistent, and well-documented.",
                    ],
                    bullets=[
                        "Harassment, discriminatory treatment, or intimidation based on protected characteristics or other inappropriate factors.",
                        "Unauthorized disclosure of confidential company, employee, customer, or candidate information.",
                        "Abuse of company systems, credentials, procurement processes, expense policies, or managerial authority.",
                        "Threatening behavior, physical aggression, or deliberate damage to company property or employee safety.",
                    ],
                ),
                section(
                    "Reporting, Investigation, and Resolution",
                    paragraphs=[
                        "Employees are encouraged to raise concerns early through their manager, Human Resources, or the confidential ethics channel. Where a concern involves a direct manager, a sensitive employee issue, or a possible retaliation risk, employees should bypass the local chain of command and use HR or the ethics route directly.",
                        "Investigations are coordinated by HR, with Legal, Security, and business leaders involved as needed. Outcomes depend on the severity and evidence of the matter and may range from coaching and training to access restrictions, formal disciplinary action, reassignment, or termination.",
                    ],
                    bullets=[
                        "Document the concern with dates, people involved, and available evidence where possible.",
                        "Protect confidentiality on a need-to-know basis during the review period.",
                        "Communicate required corrective actions to relevant leaders and track completion.",
                    ],
                ),
            ],
            exception_guidance=[
                "No manager or employee may create an exception that permits harassment, retaliation, misuse of confidential information, or other prohibited conduct. If a local practice appears to conflict with this policy, HR must review and document the resolution.",
                "Incidents involving physical safety, data exposure, or suspected retaliation should be escalated immediately to HR and the relevant specialist function. The priority is to protect people and preserve evidence before the matter becomes harder to investigate responsibly.",
            ],
            records_and_review=[
                "Policy acknowledgements, investigation records, and corrective action evidence must be stored in approved HR systems with access restricted to authorized personnel. Informal chat history should not be treated as the only record for serious matters.",
                "HR reviews conduct themes, mandatory training completion, and open remediation items at least quarterly. The policy is refreshed annually, with earlier updates when legal requirements, reporting channels, or governance expectations change.",
            ],
        ),
        DocumentSpec(
            title="Employee Benefits Overview",
            department="hr",
            filename="hr_employee_benefits_v1.pdf",
            version="1.1",
            owner_role="Benefits Program Lead",
            access_level="Internal - All Employees",
            summary="This document explains the company's benefits philosophy, enrollment process, employee support model, and the controls used to manage plan changes and benefit records.",
            purpose=[
                "The benefits overview provides employees with a reliable explanation of the health, wellness, and financial support programs offered by the company. In a RAG system, this document should answer what is available, when employees become eligible, how enrollment works, and who owns issue resolution when plan questions become time-sensitive.",
                "The document also standardizes the internal operating model used by People Operations and managers. By defining deadlines, records, and escalation paths, the policy reduces confusion during onboarding, open enrollment, and qualifying life events that require fast but compliant benefit administration.",
            ],
            scope=[
                "This overview applies to regular employees eligible for company-sponsored benefit programs according to local contract terms and carrier requirements. Program availability may vary by country, but the enrollment, support, and governance model described here remains the baseline administrative process.",
                "The document covers health plans, wellness support, retirement-related programs, insurance coverage, stipend administration, enrollment timing, life-event changes, and employee support channels. It does not replace carrier certificates or legal plan documents where more specific terms apply.",
            ],
            scope_bullets=[
                "Includes medical, dental, vision, mental health, retirement, insurance, and stipend programs where offered.",
                "Covers initial enrollment, annual review, and qualifying life-event updates.",
                "Requires approved systems and documented evidence for any plan change or exception request.",
            ],
            responsibilities={
                "Employees": [
                    "Review available plans, submit elections before deadlines, and verify dependent and beneficiary information for accuracy.",
                    "Report qualifying life events promptly and provide required documentation within the stated time window.",
                    "Use approved support channels for coverage questions, claim issues, or payroll deduction concerns.",
                ],
                "Managers": [
                    "Direct employees to People Operations for plan interpretation rather than providing informal benefit advice.",
                    "Support time-sensitive escalations when coverage issues affect employee well-being or ability to work.",
                    "Ensure new hires understand enrollment deadlines during onboarding.",
                ],
                "People Operations": [
                    "Maintain benefit content, enrollment workflows, carrier coordination, and record retention standards.",
                    "Manage open enrollment communications, approvals for exceptions, and broker escalations where required.",
                    "Track response times, recurring issue themes, and plan administration risks.",
                ],
            },
            body_sections=[
                section(
                    "Benefits Program Structure",
                    paragraphs=[
                        "The company maintains a benefits portfolio designed to support employee health, financial resilience, and sustainable remote or hybrid work. Program design is reviewed annually to remain competitive, operationally manageable, and aligned with changing workforce needs.",
                        "Employees should treat this document as a navigation guide rather than a substitute for carrier-level legal language. It provides enough operational detail to answer common questions, while directing employees to the correct source when plan documents or local laws contain the authoritative technical terms.",
                    ],
                    subsections=[
                        sub(
                            "Health and Wellness",
                            bullets=[
                                "Medical, dental, and vision options for employees and eligible dependents.",
                                "Mental health support through confidential counseling and approved wellness vendors.",
                                "A wellness or home-office allowance for eligible expenses under the expense policy.",
                            ],
                        ),
                        sub(
                            "Financial and Protection Benefits",
                            bullets=[
                                "Retirement contribution support where available under local program rules.",
                                "Company-sponsored life and disability insurance for eligible employees.",
                                "Selected stipends and equipment refresh programs for approved work needs.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Enrollment and Life-Event Administration",
                    paragraphs=[
                        "New hires must complete benefits enrollment within the stated onboarding window so coverage, payroll deductions, and dependent records can be activated on time. Outside the standard window, changes are limited to qualifying life events such as marriage, birth, dependent loss of coverage, or a documented change in residence or employment status.",
                        "Employees should not assume a carrier or payroll change is complete until they receive confirmation through the HRIS or benefits administration system. Informal email confirmation is useful for coordination, but the system record is the authoritative source for effective dates, elections, and uploaded documentation.",
                    ],
                    bullets=[
                        "Review plan summaries and contribution details before making elections.",
                        "Submit dependent, beneficiary, and required supporting documentation before the deadline.",
                        "Download the final confirmation summary and retain it for personal reference.",
                    ],
                ),
                section(
                    "Support Model and Issue Resolution",
                    paragraphs=[
                        "Most employee questions can be resolved through the People Operations queue using the internal benefits portal. More complex issues, such as denied claims, cross-border portability, carrier enrollment failures, or time-sensitive medical access problems, should be escalated with clear business urgency and supporting evidence.",
                        "The support model is designed to protect both employee experience and administrative accuracy. Employees should provide claim references, dependent details, and relevant dates when reporting a problem so People Operations can work effectively with brokers, carriers, payroll, or finance teams without repeated back-and-forth.",
                    ],
                    bullets=[
                        "Standard questions should receive an initial response within two business days.",
                        "Coverage gaps involving urgent care or medication access should be escalated the same day.",
                        "Open enrollment changes must be reviewed each cycle, even when employees intend to keep current elections.",
                    ],
                ),
            ],
            exception_guidance=[
                "Exceptions to enrollment windows or documentation requirements may be approved only when a legal obligation, carrier correction, or documented administrative error justifies the change. People Operations must record the reason, approver, and effective date for any exception.",
                "Escalate immediately when coverage issues create medical access risk, payroll deductions appear materially incorrect, or dependent eligibility questions may create compliance exposure. Fast escalation protects employees while preventing incomplete or unauthorized plan changes.",
            ],
            records_and_review=[
                "Benefit election records, supporting documents, carrier communications, and payroll-impacting confirmations must be stored in approved administrative systems with privacy protections that match the sensitivity of the data.",
                "People Operations reviews plan participation, support ticket trends, response times, and broker performance during the annual benefits cycle and at least quarterly for high-volume issue categories. The overview is refreshed before open enrollment each year.",
            ],
        ),
    ]


def onboarding_documents() -> list[DocumentSpec]:
    return [
        DocumentSpec(
            title="New Employee Guide",
            department="onboarding",
            filename="onboarding_new_employee_guide_v1.pdf",
            version="1.1",
            owner_role="Talent Enablement Lead",
            access_level="Internal - All Employees",
            summary="This guide gives new hires an enterprise-level overview of company expectations, support channels, communication norms, and first-month success measures.",
            purpose=[
                "The new employee guide helps a new hire understand how the company works before role-specific detail is layered on top. A strong onboarding document should answer where information lives, how work is coordinated, which systems matter first, and how a new employee can ask for help without losing momentum during the first month.",
                "The guide also creates alignment between managers, onboarding buddies, and support teams. It sets a baseline experience that can be scaled as the company grows, making onboarding knowledge easier to retrieve, maintain, and evaluate in a production-ready RAG environment.",
            ],
            scope=[
                "This guide applies to all new employees joining the company, regardless of department, location, or working model. Department handbooks provide role-specific expectations, but the operating principles described here should remain consistent across the organization.",
                "The content covers first-day orientation, company working norms, first-month expectations, support channels, and the communication habits that help new hires become productive without relying on undocumented tribal knowledge.",
            ],
            scope_bullets=[
                "Applies to remote, hybrid, and office-based hires.",
                "Complements department onboarding plans and manager-created 30-day goals.",
                "Does not replace security training, legal acknowledgements, or job-specific certification requirements.",
            ],
            responsibilities={
                "New Hires": [
                    "Review shared onboarding materials, complete required training, and ask clarifying questions early.",
                    "Confirm access to core systems and report blockers through the approved support channel.",
                    "Use written notes, task systems, and documented follow-ups to build role understanding deliberately.",
                ],
                "Managers": [
                    "Translate the company-level guide into role-specific priorities, meetings, and early deliverables.",
                    "Provide clarity on decision-making, escalation, and the team's working cadence during the first week.",
                    "Hold regular check-ins so confusion is resolved before it becomes a performance concern.",
                ],
                "Onboarding Partners": [
                    "People Operations, IT, and onboarding buddies should help the new hire navigate systems and company norms.",
                    "Each partner is expected to answer questions within the defined support model and route unresolved issues appropriately.",
                    "Shared onboarding trackers should remain current so missing tasks are visible and owned.",
                ],
            },
            body_sections=[
                section(
                    "First-Day Experience",
                    paragraphs=[
                        "The first day should orient a new hire to the company's mission, structure, and practical way of working. Employees should leave the day knowing who their manager is, what success looks like in the first month, where critical systems live, and how to get help when something is unclear.",
                        "A good first day is not overloaded with low-priority detail. It balances administrative setup with contextual information that helps the employee understand the company's products, team interactions, and documentation culture well enough to start absorbing role-specific knowledge.",
                    ],
                    bullets=[
                        "Attend orientation and review the employee handbook, security policies, and communication norms.",
                        "Meet the manager, onboarding buddy, and immediate teammates.",
                        "Confirm email, calendar, chat, HRIS, task tracking, and department documentation access.",
                    ],
                ),
                section(
                    "How the Company Operates",
                    paragraphs=[
                        "Most teams rely on written communication, transparent task ownership, and durable records of decisions. Employees should use shared documents, tickets, and meeting notes rather than relying on private messages or undocumented verbal agreements that are difficult for others to retrieve or review later.",
                        "Work is expected to move through visible systems with owners and due dates. New hires should learn the habit of posting updates, recording meeting outcomes, and escalating blockers early so the team can act before delays affect customers or internal commitments.",
                    ],
                    subsections=[
                        sub(
                            "Communication Norms",
                            bullets=[
                                "Use chat for quick coordination, documents for durable decisions, and email for formal updates.",
                                "Assume positive intent, but raise risks clearly and with enough context for action.",
                                "Capture outcomes with owners and dates after any meeting that changes priorities or commitments.",
                            ],
                        ),
                        sub(
                            "Execution Norms",
                            bullets=[
                                "Track work in the approved task system rather than maintaining personal side lists only.",
                                "Ask for clarification when requirements are vague rather than making hidden assumptions.",
                                "Escalate dependencies early if they may affect launch dates, customer promises, or compliance work.",
                            ],
                        ),
                    ],
                ),
                section(
                    "First 30 Days and Support Channels",
                    paragraphs=[
                        "During the first month, each employee should understand core workflows, meet key cross-functional partners, and complete at least one scoped piece of work with increasing independence. The goal is not perfection, but visible progress supported by documentation, feedback, and practical access to the right systems.",
                        "Support channels should feel easy to use. Employees should know that questions about payroll, benefits, devices, application access, security concerns, or process ambiguity belong in shared support workflows where ownership is clear and response times can be measured.",
                    ],
                    bullets=[
                        "Complete all mandatory compliance and security training within the required window.",
                        "Read the department handbook, current roadmap, and the SOPs that affect the role.",
                        "Use People Operations for HR topics, IT for system access, and the manager or buddy for team-specific guidance.",
                    ],
                ),
            ],
            exception_guidance=[
                "Any onboarding experience that materially differs from the standard model should be documented with a reason, owner, and follow-up action. This includes delayed equipment, temporary manual workarounds, role changes during onboarding, or critical systems not being available by the planned date.",
                "Escalate immediately when a new hire cannot access required systems, lacks a confirmed manager or role plan, or is blocked from completing mandatory compliance tasks. Delays in the first week compound quickly and should be treated as operational issues, not informal inconveniences.",
            ],
            records_and_review=[
                "Orientation completion, assigned trainings, access confirmations, and key onboarding checkpoints should be stored in approved onboarding trackers or HR systems. Managers should avoid relying only on private notes for first-month progress.",
                "The guide is reviewed quarterly against onboarding feedback, access issue trends, and manager observations. Major updates should be made whenever the company changes core systems, communication norms, or compliance expectations.",
            ],
        ),
        DocumentSpec(
            title="First-Week Onboarding Checklist",
            department="onboarding",
            filename="onboarding_checklist_v1.pdf",
            version="1.1",
            owner_role="People Programs Manager",
            access_level="Internal - All Employees",
            summary="This checklist translates the onboarding model into concrete, trackable actions for the period before day one through the end of the first week.",
            purpose=[
                "The checklist exists to turn onboarding from a loose set of good intentions into an operational workflow with visible ownership. It helps new hires, managers, People Operations, and IT complete required tasks in the right order so the employee's first week is productive rather than consumed by avoidable setup delays.",
                "For a production-level RAG dataset, the checklist needs enough operational depth to answer questions like what should happen before day one, who is responsible for access readiness, and how missing tasks are escalated when the standard timeline breaks down.",
            ],
            scope=[
                "This checklist applies to all new hires and the support teams involved in their onboarding. Department leaders may add role-specific tasks, but the baseline company checklist should still be completed because it controls the core administrative and operational handoff.",
                "The document covers pre-start preparation, day-one activities, days-two-through-five tasks, and the manager review that closes the first week. It is intended to be executed alongside the broader new employee guide, not in place of it.",
            ],
            scope_bullets=[
                "Covers People Operations, IT, manager, onboarding buddy, and new-hire responsibilities.",
                "Applies whether onboarding occurs remotely, on-site, or in a hybrid format.",
                "Requires visible ownership for incomplete or blocked tasks by the end of the first week.",
            ],
            responsibilities={
                "New Hires": [
                    "Complete assigned tasks, confirm access, and raise blockers through the shared onboarding tracker.",
                    "Review provided guides, complete required forms, and attend scheduled orientation sessions.",
                    "Document unclear instructions rather than bypassing the process with informal workarounds.",
                ],
                "Managers": [
                    "Confirm the 30-day plan, align meetings, and ensure the role-specific onboarding path is ready.",
                    "Review checklist completion during day-one and end-of-week check-ins.",
                    "Assign owners for missing tasks rather than allowing open issues to remain untracked.",
                ],
                "People Operations and IT": [
                    "Prepare HR, payroll, identity, device, and access prerequisites before the employee starts.",
                    "Maintain the checklist system, respond to issues within service targets, and route unresolved items correctly.",
                    "Provide evidence of completion for tasks that affect payroll, compliance, or security.",
                ],
            },
            body_sections=[
                section(
                    "Pre-Start Preparation",
                    paragraphs=[
                        "A strong first week begins before the employee's first day. Managers, People Operations, and IT should confirm role details, required systems, equipment logistics, payroll setup, and onboarding sessions in advance so the new hire is not forced to spend the first day chasing avoidable administrative issues.",
                        "Preparation tasks should be tracked in a shared system with due dates and owners. If a laptop, account, or signed document is missing, the issue should be visible before the start date rather than discovered after orientation begins.",
                    ],
                    bullets=[
                        "Confirm job title, reporting line, location, manager, and start-date details.",
                        "Prepare equipment, identity records, baseline applications, and payroll setup.",
                        "Send welcome communications with orientation schedule, contact points, and day-one instructions.",
                    ],
                ),
                section(
                    "Day-One Execution",
                    paragraphs=[
                        "Day one should validate that the onboarding plan actually worked. The new hire must be able to access primary systems, understand immediate expectations, and identify where documents, support channels, and upcoming tasks are located. The manager should not assume orientation alone creates clarity.",
                        "The checklist should be used actively during the day-one check-in so unresolved items become explicit actions with owners. This reduces the risk that access gaps or ambiguous instructions linger unaddressed until they slow down the first real assignment.",
                    ],
                    subsections=[
                        sub(
                            "New Hire Day-One Tasks",
                            bullets=[
                                "Log into email, calendar, chat, HRIS, password manager, and any required team workspace.",
                                "Verify emergency contact, tax, payroll, and identity details in the HR system.",
                                "Review orientation content and note any missing access or unclear instructions immediately.",
                            ],
                        ),
                        sub(
                            "Manager Day-One Tasks",
                            bullets=[
                                "Hold a welcome meeting and explain how work is assigned, tracked, and reviewed.",
                                "Review meeting cadence, team communication expectations, and escalation routes.",
                                "Introduce the new hire to the buddy and key cross-functional contacts needed in the first month.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Days Two Through Five and End-of-Week Review",
                    paragraphs=[
                        "The rest of the first week should combine structured learning with early execution. The employee should read role-relevant policies, join recurring team rituals, shadow at least one live workflow, and begin contributing through a scoped task that builds confidence without creating unnecessary risk.",
                        "The end-of-week review closes the operational loop. The manager and new hire should identify what was completed, what remains blocked, and what needs to happen in week two. Open items should be assigned owners and dates rather than being carried forward as informal assumptions.",
                    ],
                    bullets=[
                        "Complete required compliance, privacy, security, and workplace training.",
                        "Read the department handbook, current roadmap, and role-specific SOPs or runbooks.",
                        "Attend recurring meetings and document unresolved onboarding blockers in the shared tracker.",
                        "Review week-one completion status and assign owners for any incomplete tasks.",
                    ],
                ),
            ],
            exception_guidance=[
                "If day-one or first-week tasks cannot be completed, the exception must be documented with an owner, due date, and business impact. Exceptions matter most when they affect compliance training, payroll setup, identity verification, or access to tools needed for the employee's role.",
                "Escalate to People Operations or IT immediately when the missing task affects pay, security controls, required legal documentation, or the employee's ability to begin assigned work safely and correctly.",
            ],
            records_and_review=[
                "Checklist completion status, timestamps, and evidence for key administrative tasks should be retained in the onboarding tracker or HR system. Managers should use the tracker during review conversations instead of relying on memory.",
                "The checklist is reviewed each quarter using support metrics, manager feedback, and new-hire survey themes. Repeated blockers should trigger updates to upstream provisioning or communication processes rather than ad hoc local fixes.",
            ],
        ),
        DocumentSpec(
            title="Account and Access Setup Process",
            department="onboarding",
            filename="onboarding_account_setup_process_v1.pdf",
            version="1.1",
            owner_role="IT Operations Lead",
            access_level="Internal - All Employees",
            summary="This process defines how employee identities, devices, and application permissions are provisioned, validated, and handed off using least-privilege controls.",
            purpose=[
                "The account and access setup process exists to ensure new hires receive the tools they need without exposing the company to avoidable security risk. A well-structured onboarding document should explain not just what access is provided, but how approvals work, when elevated permissions are withheld, and how completion is verified before the ticket is closed.",
                "This document supports a production-grade knowledge base by making identity setup, application provisioning, and role-based access predictable, reviewable, and easy to retrieve. It is intentionally specific about who approves what, which systems are considered baseline, and how exceptions are documented.",
            ],
            scope=[
                "The process applies to every new hire account created in the company's identity provider, device management platform, and approved business systems. It also applies to role changes where the employee requires a different access bundle, even if the individual is not newly hired.",
                "The process covers baseline account creation, multi-factor authentication, device policies, role-based application access, verification, exception handling, and closure criteria for onboarding or internal transfer provisioning requests.",
            ],
            scope_bullets=[
                "Covers identity creation, MFA enrollment, baseline app access, and role-specific access bundles.",
                "Requires manager approval for privileged, financial, personnel, or production-facing systems.",
                "Uses approved ticketing and identity systems as the source of truth for provisioning evidence.",
            ],
            responsibilities={
                "IT Operations": [
                    "Provision baseline accounts and enforce least-privilege controls through approved templates.",
                    "Validate successful authentication, device policy enforcement, and closure evidence before completing the ticket.",
                    "Record exceptions with approver, reason, and expiry date where additional access is granted temporarily.",
                ],
                "Managers": [
                    "Review role-based access requests for business need and avoid unnecessary over-provisioning.",
                    "Confirm that the resulting access is sufficient for first-week work without exposing unrelated systems.",
                    "Approve privileged or high-risk access only through the designated workflow.",
                ],
                "Employees": [
                    "Complete MFA enrollment, password manager setup, and account verification promptly.",
                    "Report missing or unexpected access through the onboarding queue rather than sharing credentials or borrowing devices.",
                    "Use approved systems only and follow security requirements from the first login onward.",
                ],
            },
            body_sections=[
                section(
                    "Provisioning Principles",
                    paragraphs=[
                        "Provisioning is based on the principle of least privilege, which means a new hire receives only the access required to begin performing their role safely and effectively. This reduces security exposure, limits accidental access to sensitive systems, and creates a cleaner audit trail when roles change over time.",
                        "Role templates provide the starting point, but managers remain accountable for validating that the requested bundle matches the real business need. Exceptions should be rare, time-bound, and documented with the same rigor as any other security-relevant access decision.",
                    ],
                    bullets=[
                        "Create the employee identity using approved naming and directory conventions.",
                        "Enroll MFA before the first successful login to company-managed systems.",
                        "Apply baseline endpoint, browser, and device security controls before closure.",
                    ],
                ),
                section(
                    "Standard and Role-Based Access Workflow",
                    paragraphs=[
                        "Baseline access typically includes email, calendar, chat, HRIS, ticketing, documentation, and password manager access. These systems support the first week of work for nearly every employee and should be provisioned before more specialized applications are considered.",
                        "Role-based access is layered on top of baseline access. Engineering roles may require source control, CI visibility, and development environments, while business roles may require CRM, finance, or support tools. Production, financial, and personnel systems remain separately controlled even when a role template exists.",
                    ],
                    subsections=[
                        sub(
                            "Engineering Access",
                            bullets=[
                                "Grant source control, issue tracker, CI visibility, and development environment access through the approved template.",
                                "Require separate approval for production consoles, infrastructure administration, or secret-management tools.",
                                "Validate repository or environment membership after provisioning rather than assuming template success.",
                            ],
                        ),
                        sub(
                            "Business Access",
                            bullets=[
                                "Grant CRM, analytics, support, finance, or HR systems only when the role requires them.",
                                "Review bundled permissions carefully to avoid granting unnecessary reporting or export privileges.",
                                "Use the access request workflow for any system not included in the standard role template.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Verification, Handoff, and Closure",
                    paragraphs=[
                        "A provisioning ticket is not complete when accounts are created; it is complete when the employee can authenticate successfully, required controls are active, and the manager confirms that the initial toolset is appropriate. Closing tickets too early creates a false sense of readiness and pushes avoidable work into the first week.",
                        "Verification should include login success, MFA completion, password manager access, and confirmation that key systems open as expected. Any missing access should remain visible as an open action with a named owner rather than being handled informally through direct messages or temporary credential sharing.",
                    ],
                    bullets=[
                        "Confirm login success and MFA enrollment with the employee.",
                        "Have the manager validate first-week access sufficiency before closure.",
                        "Retain exceptions and unresolved gaps in the queue until the final handoff is complete.",
                    ],
                ),
            ],
            exception_guidance=[
                "Privileged or temporary access exceptions must include a business reason, approver, review date, and removal plan. Verbal approval is not sufficient for high-risk systems because the ticket record is the audit source of truth.",
                "Escalate immediately if identity creation fails, baseline access cannot be provided by day one, or an employee receives unexpected access to restricted systems. These issues may indicate either an onboarding failure or a security control gap.",
            ],
            records_and_review=[
                "Provisioning tickets, manager approvals, exception records, and verification evidence must be retained in approved systems so audits can confirm who granted access, why it was granted, and whether the final state matched policy.",
                "IT Operations reviews template accuracy, failed provisioning trends, and exception volume each quarter. Role bundles should be updated when repeated access gaps or over-provisioning patterns are identified.",
            ],
        ),
    ]


def engineering_documents() -> list[DocumentSpec]:
    return [
        DocumentSpec(
            title="API Development Guidelines",
            department="engineering",
            filename="engineering_api_guidelines_v1.pdf",
            version="1.1",
            owner_role="Staff Backend Engineer",
            access_level="Internal - Engineering",
            summary="These guidelines define the enterprise standard for designing, documenting, securing, versioning, and operating internal or customer-facing APIs.",
            purpose=[
                "The API development guidelines establish a shared engineering standard so services expose predictable, secure, and maintainable interfaces over time. In a production-level RAG dataset, the value of this document is that it answers both principle questions, such as how an API should be designed, and operational questions, such as what evidence is required before release.",
                "The guidance aims to reduce inconsistent patterns across teams by codifying request design, response design, security controls, documentation expectations, and change-management practices. It also reinforces that an API is part of the long-term operating surface of the company and must therefore be observable, supportable, and safe to evolve.",
            ],
            scope=[
                "These guidelines apply to new APIs, materially changed endpoints, and service integrations that expose business or operational functionality to internal or external clients. Existing systems should adopt the standard incrementally as part of maintenance or versioning work.",
                "The document covers URL design, payload validation, response semantics, authentication, authorization, observability, documentation, and release governance. It does not replace deeper security reviews, privacy assessments, or system-specific compliance controls where additional scrutiny is required.",
            ],
            scope_bullets=[
                "Applies to REST-style services and documented service endpoints used by internal or external consumers.",
                "Covers design-time, implementation-time, and release-time controls.",
                "Requires coordination with security and platform teams for high-risk endpoints or sensitive data flows.",
            ],
            responsibilities={
                "API Authors": [
                    "Design endpoints using shared conventions, explicit schemas, and stable field semantics.",
                    "Document authentication, expected errors, versioning implications, and rollout notes before release.",
                    "Add observability and tests that make the API supportable after launch.",
                ],
                "Reviewers": [
                    "Evaluate API clarity, backward compatibility, and operational safety during review.",
                    "Challenge ambiguous naming, missing error behavior, weak validation, or undocumented changes.",
                    "Confirm that the change includes enough evidence for safe client adoption and rollout.",
                ],
                "Platform and Security Partners": [
                    "Provide guidance on auth, rate limits, secrets handling, logging, and service standards.",
                    "Support reviews for sensitive integrations or customer-facing changes.",
                    "Monitor recurring design issues and feed them back into the engineering standard.",
                ],
            },
            body_sections=[
                section(
                    "Design Principles",
                    paragraphs=[
                        "APIs should be designed around clarity, consistency, and safe evolution. Consumers should be able to understand the resource model, expected errors, and field meanings without reverse-engineering implementation details from examples or source code. This is especially important in larger companies where the original authors may not be the future maintainers or primary consumers.",
                        "A stable API surface reduces long-term cost. Teams should favor resource-oriented naming, carefully controlled schemas, and backward-compatible change strategies that allow clients to adopt improvements without being surprised by hidden coupling or breaking behavior.",
                    ],
                    bullets=[
                        "Prefer nouns and resource-oriented URLs over action-heavy or ambiguous paths.",
                        "Use explicit request and response schemas rather than informal payload expectations.",
                        "Treat field naming, nullability, and default behavior as part of the API contract.",
                    ],
                ),
                section(
                    "Request, Response, and Error Standards",
                    paragraphs=[
                        "Request design should balance strict validation with practical client usability. APIs should reject malformed or ambiguous payloads early and return clear guidance when the caller can correct the problem. For list or search endpoints, pagination, filtering, and sorting should be designed up front rather than bolted on after clients are already relying on unstable behavior.",
                        "Response design should make state changes and outcomes easy to interpret. Clients should receive stable identifiers, timestamps where meaningful, and structured error responses that include machine-readable codes and correlation identifiers for support and debugging. Generic failures are rarely good enough in production environments where support and incident response depend on precise signals.",
                    ],
                    subsections=[
                        sub(
                            "Request Design",
                            bullets=[
                                "Validate payloads with explicit schemas and handle unknown critical fields deliberately.",
                                "Use idempotency protections for retry-sensitive operations such as provisioning or financial workflows.",
                                "Define pagination and filtering semantics for any endpoint expected to scale.",
                            ],
                        ),
                        sub(
                            "Response and Error Design",
                            bullets=[
                                "Return stable identifiers, status fields, and relevant timestamps for stateful resources.",
                                "Include machine-readable error codes and a correlation ID in error responses.",
                                "Document validation failures, auth failures, and rate-limit behavior with concrete examples.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Security, Documentation, and Release Controls",
                    paragraphs=[
                        "Every API must be reviewed for authentication, authorization, rate limiting, and sensitive data handling before release. Logging should support diagnosis without leaking secrets or regulated content, and access checks should be enforced consistently at the service boundary and within sensitive operations where needed.",
                        "Documentation is a release requirement, not an afterthought. Teams should publish an OpenAPI definition, field-level guidance where necessary, sample payloads, and release notes that explain rollout caveats, deprecations, and expected consumer actions. Strong documentation is part of the operational contract that allows other teams to integrate safely.",
                    ],
                    bullets=[
                        "Require authenticated access unless a public exposure has been reviewed and approved.",
                        "Mask secrets, tokens, and personal data in logs, traces, and debug output.",
                        "Publish contract documentation and notify consumers before making schema changes that require client work.",
                    ],
                ),
            ],
            exception_guidance=[
                "Breaking API changes require documented versioning strategy, consumer communication, and an approved migration plan. Teams should not rely on informal Slack notice for changes that could break a client integration or alter security-sensitive behavior.",
                "Escalate to security or platform engineering when an API handles regulated data, privileged actions, or materially customer-facing availability risk. The earlier the review happens, the lower the cost of correction.",
            ],
            records_and_review=[
                "Source control history, API definitions, release notes, security review decisions, and rollout evidence should be retained with the service documentation so maintainers can trace why the interface behaves the way it does.",
                "The guideline is reviewed at least twice a year by backend and platform engineering leads. Review inputs include incident lessons, API design review findings, and recurring integration pain points reported by consumers.",
            ],
        ),
        DocumentSpec(
            title="Engineering Code Standards",
            department="engineering",
            filename="engineering_code_standards_v1.pdf",
            version="1.1",
            owner_role="Engineering Manager",
            access_level="Internal - Engineering",
            summary="This standard explains how engineering teams write, review, test, document, and operate production code across company systems.",
            purpose=[
                "The engineering code standard exists to help teams produce software that other engineers can understand, review, test, and support under real operating conditions. In a production-level RAG dataset, this document should answer not only style questions, but also how code quality, testing, documentation, and operational readiness are assessed before release.",
                "The standard favors clarity over cleverness and repeatability over heroics. It is intended to reduce review churn, make maintenance easier across team boundaries, and establish a common baseline for what production-ready code actually means within the company.",
            ],
            scope=[
                "This standard applies to backend services, frontend applications, internal tools, scripts that affect production workflows, and infrastructure-related code stored in company-managed repositories. Teams may have language-specific conventions, but they should align to this baseline for review and readiness expectations.",
                "The document covers readability, pull request discipline, testing expectations, documentation, and the operational controls that make software safe to deploy and support. It does not replace secure coding requirements, architecture reviews, or compliance-specific controls where additional standards exist.",
            ],
            scope_bullets=[
                "Applies to new features, bug fixes, refactors, and production-impacting scripts.",
                "Requires evidence of testing, documentation updates, and operational consideration in pull requests.",
                "Encourages incremental improvement of touched code rather than local optimization alone.",
            ],
            responsibilities={
                "Engineers": [
                    "Write readable, testable code with explicit behavior, error handling, and maintainable structure.",
                    "Run local validation, update relevant documentation, and describe impact and risks in the pull request.",
                    "Improve touched areas when practical rather than preserving unnecessary complexity unchanged.",
                ],
                "Reviewers": [
                    "Focus on correctness, risk, maintainability, and behavioral clarity rather than only stylistic preference.",
                    "Ask for missing tests, rollout notes, or documentation when the change would otherwise be hard to support.",
                    "Block merges that create operational risk or unclear behavior without sufficient justification.",
                ],
                "Engineering Leads": [
                    "Maintain language-specific guidance that aligns with this enterprise standard.",
                    "Encourage high-signal review practices and healthy team norms around feedback.",
                    "Track recurring quality gaps and update standards or tooling to reduce them.",
                ],
            },
            body_sections=[
                section(
                    "Code Quality Expectations",
                    paragraphs=[
                        "Production code should be written for the next engineer who must change it under time pressure. Descriptive names, small focused units of logic, and explicit handling of error or edge cases usually outperform dense or overly clever implementations, even when the shorter version appears elegant at first glance.",
                        "Readability also includes the structure around the code. Configuration should be discoverable, side effects should be visible, and non-obvious behavior should be justified through naming or concise comments. When code is hard to follow, engineers should improve it while the context is fresh instead of deferring the cost indefinitely.",
                    ],
                    bullets=[
                        "Use descriptive names and avoid hidden state or surprising side effects.",
                        "Prefer small cohesive functions and clear data flow over deeply nested conditional logic.",
                        "Remove dead code and unused configuration rather than leaving uncertain leftovers behind.",
                    ],
                ),
                section(
                    "Pull Request and Review Standards",
                    paragraphs=[
                        "A pull request is the handoff surface between the author, the reviewer, and future maintainers. It should explain the behavioral change, user impact, rollout considerations, validation steps, and any risk that a reviewer cannot infer directly from the diff. Review quality drops quickly when the reviewer is forced to reconstruct missing context.",
                        "Review is not just a gate; it is part of the engineering knowledge system. Teams should prefer changes that are easy to understand, comment on, and test. Large change sets should be broken down where possible so review can focus on correctness rather than broad uncertainty about too many moving parts at once.",
                    ],
                    bullets=[
                        "Run formatting, linting, and relevant tests before opening the pull request.",
                        "Explain impact, risks, rollout needs, and validation results in the pull request description.",
                        "Avoid merging without informed review unless an approved emergency procedure is in effect.",
                    ],
                ),
                section(
                    "Testing and Operational Readiness",
                    paragraphs=[
                        "Tests should validate meaningful behavior, boundary conditions, and failure scenarios that matter to users or operators. Unit tests are useful for isolated logic, but integration tests become essential when persistence, external services, or API contracts are involved. Manual verification can supplement automation, but it should not become a substitute for durable coverage where the same risks recur.",
                        "Operational readiness means the code can be observed, supported, and rolled back. Services should emit useful logs, metrics, or traces, and risky changes should come with a rollback plan. Engineers should think about on-call impact before the code reaches production, not only after alerts begin firing.",
                    ],
                    bullets=[
                        "Add or update automated tests for the behaviors your change materially affects.",
                        "Document manual verification when automation is not yet practical and explain why.",
                        "Ensure logs, health checks, alerts, and rollback steps exist for production-relevant changes.",
                    ],
                ),
            ],
            exception_guidance=[
                "Exceptions to testing or review expectations require a documented reason and an explicit follow-up action. For example, an urgent hotfix may ship with narrower validation, but it must still carry rollback guidance and a plan to fill the missing coverage.",
                "Escalate if schedule pressure is driving repeated requests to bypass tests, reviews, or documentation. Persistent exceptions usually signal a planning or tooling problem that standards alone cannot solve.",
            ],
            records_and_review=[
                "Pull request descriptions, review comments, test evidence, and updated docs should remain linked through source control and project tracking so future maintainers can reconstruct design and risk decisions.",
                "Engineering leadership reviews the code standard periodically using defect patterns, post-incident findings, and review feedback quality. Teams should update local practice when the shared standard changes rather than drifting silently over time.",
            ],
        ),
        DocumentSpec(
            title="Service Deployment Process",
            department="engineering",
            filename="engineering_deployment_process_v1.pdf",
            version="1.1",
            owner_role="Platform Engineering Lead",
            access_level="Internal - Engineering",
            summary="This document describes the standard deployment lifecycle from readiness checks through release execution, monitoring, and rollback.",
            purpose=[
                "The deployment process standardizes how engineering teams prepare, execute, validate, and if necessary reverse production releases. A production-level RAG dataset should make it easy to retrieve both the high-level deployment flow and the practical details that matter during a real release window, such as who owns monitoring and when a rollback becomes the safer choice.",
                "The process reduces release risk by requiring readiness evidence, explicit ownership, and post-deployment observation. It recognizes that code quality alone is not enough; the release itself is an operational event that must be planned and managed with the same discipline as the implementation.",
            ],
            scope=[
                "This process applies to production deployments for customer-facing services, internal platforms that support business-critical operations, and changes involving infrastructure, migrations, or configuration that materially affect runtime behavior.",
                "It covers readiness validation, deployment execution, post-release monitoring, communication, and rollback criteria. Team-specific runbooks may provide tool-level detail, but they should align to this control sequence unless a platform exception is documented.",
            ],
            scope_bullets=[
                "Applies to standard releases, scheduled fixes, infrastructure changes, and high-risk migrations.",
                "Requires a named release owner and a rollback approach before deployment begins.",
                "Uses release tickets, dashboards, and communication channels as the operational source of truth.",
            ],
            responsibilities={
                "Release Owner": [
                    "Confirm readiness evidence, coordinate the release window, and remain available through validation.",
                    "Communicate release status, risks, and rollback decisions in the designated channel.",
                    "Ensure post-release monitoring is active and closure criteria are satisfied before standing down.",
                ],
                "Reviewers and Approvers": [
                    "Validate that testing, migration safety, and dependency reviews were completed appropriately.",
                    "Challenge unclear rollout assumptions or missing rollback detail before approval.",
                    "Escalate when the release risk appears inconsistent with the proposed release window or safeguards.",
                ],
                "Platform or On-Call Partners": [
                    "Support pipeline execution, environment health review, and incident escalation if needed.",
                    "Help interpret dashboards, alerts, and infrastructure signals during the release.",
                    "Participate in rollback or mitigation when the release impacts shared systems.",
                ],
            },
            body_sections=[
                section(
                    "Readiness Validation",
                    paragraphs=[
                        "Readiness review should confirm more than test success. The release owner must understand schema changes, dependency timing, configuration changes, feature flags, and any business activities that could amplify the blast radius if the rollout goes poorly. Mature teams treat readiness as a decision checkpoint, not a rubber stamp.",
                        "Where the release includes data migration, authentication changes, or infrastructure moves, the review should include a clear rollback strategy and a confidence statement about whether rollback is technically safe after partial execution. That decision should not be improvised during the release window.",
                    ],
                    bullets=[
                        "Verify code review completion, required tests, and linked release ticket scope.",
                        "Confirm migration sequencing, configuration changes, and dependency coordination.",
                        "Review the rollback plan and identify any steps that become irreversible after execution.",
                    ],
                ),
                section(
                    "Deployment Execution",
                    paragraphs=[
                        "The release should be performed from the approved artifact or branch through the standard deployment workflow. Each stage of the rollout should be observed rather than treated as complete simply because the automation advanced. Automated success is useful, but production behavior is the actual release outcome that matters.",
                        "Where staged promotion is available, the service should be validated in lower environments or limited exposure modes before broad rollout. A healthy release is one in which evidence accumulates progressively and the team stays able to pause without confusion or blame if the signals worsen.",
                    ],
                    bullets=[
                        "Start the deployment through the approved pipeline and record the start time and operator.",
                        "Validate staging or progressive rollout behavior before expanding exposure.",
                        "Pause immediately if error rates, latency, queue depth, or auth failures move outside acceptable thresholds.",
                    ],
                ),
                section(
                    "Post-Deployment Monitoring and Rollback",
                    paragraphs=[
                        "The release is not complete at the moment the pipeline finishes. The release owner remains responsible for watching health checks, logs, traces, and user-visible flows until the service is stable and any known transient issues are understood. Teams should explicitly decide when the monitoring window ends rather than drifting away from the release without closure.",
                        "Rollback should be treated as a disciplined mitigation, not an admission of failure. If the new version introduces user harm, data integrity risk, or ongoing instability, rolling back quickly is often the lowest-cost decision. Waiting for certainty can turn a contained release issue into a broader incident.",
                    ],
                    bullets=[
                        "Check core user flows, health endpoints, dashboards, and alerts within the first fifteen minutes.",
                        "Communicate final release state or rollback status in the engineering release channel.",
                        "Capture timeline, observed issues, and follow-up tasks in the release record after stabilization.",
                    ],
                ),
            ],
            exception_guidance=[
                "Any release that cannot meet the standard readiness controls must document the exception, the compensating control, and the approver. Emergency releases may move faster, but they still require explicit ownership, monitoring, and post-release documentation.",
                "Escalate immediately if rollback is unsafe, if migration behavior appears inconsistent, or if shared infrastructure signals indicate the release is affecting more than the intended service. Early escalation is a control, not a failure.",
            ],
            records_and_review=[
                "Release tickets, dashboard links, approver notes, rollback decisions, and final release summaries should be retained with the deployment record. A release without durable operational notes becomes difficult to audit or learn from later.",
                "The deployment process is reviewed quarterly using incident learnings, rollback frequency, release delay causes, and platform feedback. Repeated failure patterns should lead to stronger automation or better pre-release controls rather than repeated heroics during rollout.",
            ],
        ),
    ]


def sop_documents() -> list[DocumentSpec]:
    return [
        DocumentSpec(
            title="Deployment Standard Operating Procedure",
            department="sop",
            filename="sop_deployment_v1.pdf",
            version="1.1",
            owner_role="Release Manager",
            access_level="Internal - Operations and Engineering",
            summary="This SOP standardizes the detailed steps, checks, approvals, and evidence required to perform controlled production deployments.",
            purpose=[
                "This procedure exists to make production deployments repeatable, observable, and audit-ready. A production-level RAG dataset should include not just policy language, but the exact steps an operator follows before, during, and after a release so the retriever can surface execution detail under real pressure.",
                "The SOP bridges engineering preparation with operational control. It defines a step sequence that reduces ambiguity, clarifies who is expected to act at each stage, and ensures the release record captures enough evidence to support review, rollback decisions, and future improvement work.",
            ],
            scope=[
                "This procedure applies to planned production deployments for services and systems that support customer-facing or business-critical workflows. Team-specific tooling may vary, but the control sequence in this SOP is the expected baseline unless an approved platform exception exists.",
                "The SOP covers pre-deployment checks, deployment execution, validation, communication, and closure. It should be used together with service-specific runbooks, migration notes, and monitoring dashboards when a real release is performed.",
            ],
            scope_bullets=[
                "Applies to standard releases, high-risk changes, and progressive rollouts.",
                "Requires named ownership, evidence capture, and rollback preparedness before execution.",
                "Must be followed even when automation performs the technical release steps.",
            ],
            responsibilities={
                "Release Manager": [
                    "Own the checklist, confirm readiness evidence, and coordinate the release timeline.",
                    "Ensure the right approvers, responders, and communication channels are in place before start.",
                    "Close the release only after validation and documentation requirements are completed.",
                ],
                "Implementing Engineer": [
                    "Provide the release artifact, migration notes, rollback guidance, and expected health indicators.",
                    "Execute technical steps or supervise automation behavior during the release.",
                    "Call out unexpected signals immediately rather than waiting for certainty.",
                ],
                "Operational Support": [
                    "Monitor dashboards, confirm incident readiness, and assist with rollback or escalation if needed.",
                    "Record time-stamped actions and communications during the release window.",
                    "Verify closure evidence is stored in the release record.",
                ],
            },
            body_sections=[
                section(
                    "Pre-Deployment Procedure",
                    paragraphs=[
                        "Operators should begin by confirming that the planned release matches the approved scope and that every prerequisite item is present before any environment change starts. This step is deliberately explicit because incomplete preparation is a common cause of rushed release decisions and weak rollback outcomes.",
                    ],
                    subsections=[
                        sub(
                            "Step 4.1 Confirm Scope and Approval",
                            paragraphs=[
                                "Review the release ticket, linked pull requests, and any migration notes to confirm the exact change set. Verify that the named approver, release owner, and technical operator are correct and that the planned window still matches business risk and dependency timing."
                            ],
                            bullets=[
                                "Check the approved artifact or branch.",
                                "Verify rollout window, approver, and owner assignments.",
                                "Confirm that non-release changes are not bundled into the same deployment unexpectedly.",
                            ],
                        ),
                        sub(
                            "Step 4.2 Confirm Readiness Evidence",
                            paragraphs=[
                                "Validate test completion, lower-environment results, dashboard links, and rollback instructions. If a migration, flag, or configuration change is involved, confirm sequencing and identify the last safe rollback point before execution begins."
                            ],
                            bullets=[
                                "Review automated and manual validation results.",
                                "Confirm dashboards, alerts, and health checks are available.",
                                "Verify rollback conditions and any irreversible steps.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Deployment Execution Procedure",
                    paragraphs=[
                        "During deployment, the operator should work from the checklist in order and capture actions as they occur. Even when the rollout is automated, the human operator remains responsible for validating system behavior and pausing when evidence suggests the change is unsafe to continue.",
                    ],
                    subsections=[
                        sub(
                            "Step 5.1 Start the Deployment",
                            paragraphs=[
                                "Trigger the deployment from the approved artifact, record the start time, and announce the beginning of the release in the designated channel. This creates a shared reference point for downstream responders and provides the basis for later timeline reconstruction."
                            ],
                            bullets=[
                                "Start the rollout through the standard pipeline.",
                                "Record operator name, start time, and artifact version.",
                                "Notify stakeholders that deployment is in progress.",
                            ],
                        ),
                        sub(
                            "Step 5.2 Observe Each Rollout Stage",
                            paragraphs=[
                                "As the deployment moves through stages, review health indicators rather than assuming the stage is successful because the pipeline advanced. For progressive rollouts, validate early signals before expanding traffic or promoting the release more broadly."
                            ],
                            bullets=[
                                "Check build status, migration output, and environment health after each stage.",
                                "Pause before broad exposure if error trends, auth failures, or latency regressions appear.",
                                "Use the incident route immediately if service health degrades materially.",
                            ],
                        ),
                        sub(
                            "Step 5.3 Validate Business-Critical Flows",
                            paragraphs=[
                                "Run the agreed validation set for the service, including the user journeys or operational workflows most likely to reveal a bad release. Validation should focus on the behaviors that matter to customers or internal operators, not only generic service health."
                            ],
                            bullets=[
                                "Check critical read, write, auth, and background-processing paths.",
                                "Compare live metrics to expected release behavior.",
                                "Document any known issue or anomaly before deciding to continue.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Post-Deployment and Rollback Procedure",
                    paragraphs=[
                        "Once the rollout completes, the operator should remain in a monitoring posture until the agreed stabilization window ends. If meaningful customer impact or data risk appears, the release manager should move directly to rollback or a documented mitigation path rather than letting uncertainty delay the response.",
                    ],
                    subsections=[
                        sub(
                            "Step 6.1 Stabilization Monitoring",
                            bullets=[
                                "Watch dashboards, alerts, logs, and traces for the agreed observation period.",
                                "Confirm that queue depth, background jobs, and dependent systems remain healthy.",
                                "Communicate status updates at the cadence defined for the release window.",
                            ],
                        ),
                        sub(
                            "Step 6.2 Rollback Decision",
                            paragraphs=[
                                "If health indicators or business outcomes show the release is causing harm, execute the rollback according to the documented plan. The decision should prioritize service stability and data safety over optimism that the issue may self-correct."
                            ],
                            bullets=[
                                "Declare rollback when thresholds or user impact criteria are met.",
                                "Record the rollback trigger, time, and the systems affected.",
                                "Return to monitoring after rollback until the system is stable.",
                            ],
                        ),
                        sub(
                            "Step 6.3 Release Closure",
                            bullets=[
                                "Post the final status, known issues, and follow-up tasks in the release record.",
                                "Attach evidence, timeline notes, and any deviations from the planned checklist.",
                                "Close the release only after documentation and communication are complete.",
                            ],
                        ),
                    ],
                ),
            ],
            exception_guidance=[
                "Any skipped step in this SOP must be documented as an exception with a reason, approver, and compensating control. Operators should never rely on memory to justify why a standard step was omitted during a production release.",
                "Escalate to incident management immediately if the deployment threatens availability, integrity, or customer trust. The SOP is designed to support decisive escalation, not to delay it.",
            ],
            records_and_review=[
                "The release ticket must contain scope, approvals, timestamps, validation evidence, rollback actions if any, and the final release summary. Operational notes should be durable enough that another team can reconstruct the event without private chat history.",
                "Release management reviews deployment adherence, rollback rates, and repeated checklist misses after each major cycle. The SOP should be updated when the same failure mode appears more than once or when automation changes the practical sequence of work.",
            ],
        ),
        DocumentSpec(
            title="Incident Response Standard Operating Procedure",
            department="sop",
            filename="sop_incident_response_v1.pdf",
            version="1.1",
            owner_role="Site Reliability Manager",
            access_level="Internal - Operations and Engineering",
            summary="This SOP provides the detailed sequence for declaring, coordinating, communicating, and resolving service incidents.",
            purpose=[
                "The incident response SOP ensures that service degradation or outage events are handled using a common and time-aware operating model. In a production-grade RAG dataset, the document needs to answer both classification questions and urgent procedural questions, such as what happens first, who owns coordination, and when updates should be issued.",
                "The procedure is designed to reduce confusion under pressure. By standardizing declaration, role assignment, mitigation, communication, and review, it helps teams stabilize service faster while creating the evidence needed for post-incident learning and governance.",
            ],
            scope=[
                "This SOP applies to incidents affecting availability, data integrity, security posture, customer experience, or business-critical internal operations. It is used when an issue requires coordinated response across more than one person or function, even if the root cause is not yet known.",
                "The procedure covers severity classification, incident declaration, immediate response, communication cadence, recovery, and post-incident review. Security incidents may require additional specialist procedures, but the coordination model here still applies unless explicitly superseded.",
            ],
            scope_bullets=[
                "Applies to customer-visible outages, severe degradation, and significant internal operational failures.",
                "Requires a named incident commander and a durable incident record for coordinated events.",
                "Works alongside security, vendor, or product-specific response procedures where needed.",
            ],
            responsibilities={
                "Incident Commander": [
                    "Own incident direction, assign roles, and keep the response focused on service restoration.",
                    "Decide when to escalate severity, request additional responders, or move to rollback or mitigation.",
                    "Ensure updates remain regular, factual, and tied to concrete next actions.",
                ],
                "Technical Responders": [
                    "Investigate symptoms, test mitigations, and communicate findings clearly to the commander.",
                    "Avoid competing uncoordinated changes during the incident unless explicitly assigned.",
                    "Record meaningful technical observations and actions in the incident log.",
                ],
                "Operations and Communications Partners": [
                    "Maintain the incident record, stakeholder updates, and timeline accuracy.",
                    "Coordinate customer-facing messaging when external communication is needed.",
                    "Ensure follow-up actions are assigned before closure.",
                ],
            },
            body_sections=[
                section(
                    "Incident Declaration Procedure",
                    paragraphs=[
                        "The first step is to determine whether the issue requires formal incident handling. Teams should favor declaring early when customer impact or uncertainty is high, because a low-friction declaration is usually cheaper than a delayed coordinated response after the blast radius has widened.",
                    ],
                    subsections=[
                        sub(
                            "Step 4.1 Classify Severity",
                            bullets=[
                                "Assess user impact, revenue risk, security concern, and time sensitivity.",
                                "Assign the initial severity even if some technical facts remain unclear.",
                                "Update the severity later when better evidence becomes available.",
                            ],
                        ),
                        sub(
                            "Step 4.2 Open the Incident Record",
                            paragraphs=[
                                "Create the incident record and response channel within ten minutes of declaration. Include the initial summary, suspected systems affected, severity, incident commander, and the next expected update time so responders and stakeholders know where authoritative information will live."
                            ],
                            bullets=[
                                "Open the designated response channel and tracking record.",
                                "Assign incident commander and note current responder list.",
                                "Capture the initial problem statement and expected next update.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Immediate Response Procedure",
                    paragraphs=[
                        "The response should prioritize stabilization before deep root-cause analysis. Early actions should aim to reduce user harm, restore essential functionality, and limit blast radius while enough signal is collected to support sound technical decisions.",
                    ],
                    subsections=[
                        sub(
                            "Step 5.1 Establish Working Hypotheses",
                            bullets=[
                                "Review alerts, dashboards, recent changes, and known dependencies.",
                                "State likely causes as hypotheses and separate them from confirmed facts.",
                                "Assign owners to parallel investigation tracks only when coordination can be maintained.",
                            ],
                        ),
                        sub(
                            "Step 5.2 Apply Mitigation",
                            paragraphs=[
                                "Use the lowest-risk mitigation available that can materially reduce impact, such as rollback, traffic shift, feature disablement, or queue protection. Mitigation steps should be logged with timestamps because they become critical context for both restoration and later analysis."
                            ],
                            bullets=[
                                "Choose mitigations that reduce customer harm before pursuing perfection.",
                                "Record every configuration or deployment change made during the response.",
                                "Reassess severity and required responders after mitigation is applied.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Communication, Recovery, and Review Procedure",
                    paragraphs=[
                        "Clear communication is part of incident handling, not a separate administrative burden. Internal stakeholders need regular, time-stamped updates with current impact, actions taken, and next steps. When external communication is required, the designated communications lead should coordinate messaging with the incident commander so customers receive accurate and consistent information.",
                    ],
                    subsections=[
                        sub(
                            "Step 6.1 Maintain Update Cadence",
                            bullets=[
                                "Post initial summary, current impact, and next steps as soon as the incident is declared.",
                                "Update every fifteen to thirty minutes for active high-severity incidents.",
                                "Use time stamps and avoid speculation presented as fact.",
                            ],
                        ),
                        sub(
                            "Step 6.2 Confirm Recovery",
                            bullets=[
                                "Verify customer impact has ended and health indicators remain stable.",
                                "Watch for recurrence during the stabilization window before declaring resolution.",
                                "Confirm dependent systems and backlog processing have returned to normal.",
                            ],
                        ),
                        sub(
                            "Step 6.3 Complete the Post-Incident Review",
                            paragraphs=[
                                "After recovery, the commander or designated owner must prepare a review covering timeline, root cause, contributing factors, customer impact, and preventive actions. The goal is not blame allocation; it is to improve systems, processes, and readiness for the next event."
                            ],
                            bullets=[
                                "Assign owners and due dates for follow-up actions.",
                                "Link evidence, dashboards, and decision points used during the response.",
                                "Share the review with the relevant leadership and affected teams.",
                            ],
                        ),
                    ],
                ),
            ],
            exception_guidance=[
                "If the response deviates from this SOP because of security handling, vendor involvement, or unavailable systems, the deviation should be recorded with a reason and the alternative coordination method used. Hidden process changes create confusion during review and repeat events.",
                "Escalate quickly when incident impact expands, responders become overloaded, or communication quality drops. Coordination failure is itself an incident risk and should be treated as such.",
            ],
            records_and_review=[
                "The incident record must include timeline entries, severity changes, responder assignments, communications, mitigations, and closure evidence. Durable records matter because post-incident learning depends on facts captured during the event rather than reconstructed memory.",
                "This SOP is reviewed after major incidents and at least semiannually. Repeated response pain points should trigger updates to tools, role definitions, or mitigation playbooks in addition to procedural wording.",
            ],
        ),
        DocumentSpec(
            title="Data Backup and Recovery Standard Operating Procedure",
            department="sop",
            filename="sop_data_backup_v1.pdf",
            version="1.1",
            owner_role="Infrastructure Operations Manager",
            access_level="Internal - Restricted",
            summary="This SOP sets the step-by-step standard for backup scheduling, validation, restore testing, and controlled production recovery.",
            purpose=[
                "This SOP ensures that backups are not only created, but also verified, retained, and recoverable within the business expectations for critical systems. In a production-level RAG dataset, the procedure must answer practical recovery questions such as what is backed up, how restore confidence is established, and what steps must be followed before service is reopened.",
                "The procedure supports both resilience and governance. It defines a repeatable operating model so teams can prove backups exist, detect failures early, and execute recovery with enough discipline to protect data integrity during stressful incidents.",
            ],
            scope=[
                "This SOP applies to production databases, document stores, file repositories containing regulated or business-critical information, and configuration assets required to restore service. Teams must maintain a current inventory of systems covered by the backup program.",
                "The procedure covers backup schedule design, monitoring, validation, restore testing, production recovery, and recovery record retention. Service-specific runbooks may add product detail, but they should not weaken the controls defined here.",
            ],
            scope_bullets=[
                "Applies to critical data stores, file systems, and infrastructure configuration assets.",
                "Requires encryption, retention rules, and restore testing for systems in scope.",
                "Uses backup logs, monitoring, and recovery records as the auditable source of truth.",
            ],
            responsibilities={
                "Infrastructure Operations": [
                    "Maintain schedules, retention settings, monitoring, and validation routines for systems in scope.",
                    "Investigate failed backups, lead restore drills, and coordinate controlled recoveries during incidents.",
                    "Document recovery timelines, restore points, and exception decisions.",
                ],
                "System Owners": [
                    "Confirm data classification, recovery objectives, and business-critical dependencies for their systems.",
                    "Participate in restore testing and validate that recovered data is operationally usable.",
                    "Review backup coverage when architecture, schemas, or storage patterns change.",
                ],
                "Incident or Change Leads": [
                    "Approve production recovery actions during incidents or recovery tests.",
                    "Coordinate communication, access control, and reopening of systems after validation.",
                    "Ensure follow-up actions are assigned when backup or recovery gaps are discovered.",
                ],
            },
            body_sections=[
                section(
                    "Backup Management Procedure",
                    paragraphs=[
                        "Backup activity should follow an explicit schedule matched to recovery point objectives and data criticality. A backup that technically exists but does not meet the business recovery target or is not being monitored effectively should be treated as a control gap rather than a success.",
                    ],
                    subsections=[
                        sub(
                            "Step 4.1 Define and Run Backup Schedule",
                            bullets=[
                                "Set daily incremental and weekly full backups for critical systems unless a stricter requirement applies.",
                                "Use encryption, approved storage targets, and retention settings aligned to policy.",
                                "Verify that schedule ownership and monitoring are assigned for each covered system.",
                            ],
                        ),
                        sub(
                            "Step 4.2 Monitor Backup Completion",
                            paragraphs=[
                                "Backup jobs should be observed through alerts and periodic review rather than assumed successful. Repeated failures, long runtimes, or missing off-site copies indicate a resilience issue that must be addressed before a real recovery event exposes the weakness."
                            ],
                            bullets=[
                                "Route backup failures and missed jobs to the operations queue.",
                                "Investigate and resolve repeated failures within the same business day.",
                                "Confirm off-site and retention controls remain active after configuration changes.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Validation and Restore Testing Procedure",
                    paragraphs=[
                        "Restore confidence comes from evidence, not assumptions. Regular restore drills should be scheduled so teams can confirm that backups are complete, usable, and consistent with expected recovery times. Validation should include both technical integrity and application-level usefulness where possible.",
                    ],
                    subsections=[
                        sub(
                            "Step 5.1 Run Restore Drill",
                            bullets=[
                                "Select the backup set and target restore point for the scheduled validation.",
                                "Restore into a controlled environment when time and risk profile allow.",
                                "Capture timing, errors, and manual workarounds required to complete the restore.",
                            ],
                        ),
                        sub(
                            "Step 5.2 Validate Recovered Data",
                            paragraphs=[
                                "System owners should confirm that recovered data is complete enough for business use and that the application or reporting layer behaves as expected. Technical success without operational usability should still be treated as a failed or incomplete validation."
                            ],
                            bullets=[
                                "Check schema integrity, record counts, key workflows, and essential reference data.",
                                "Document discrepancies between expected and recovered state.",
                                "Open follow-up actions for missing automation, unclear runbooks, or slow recovery steps.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Production Recovery Procedure",
                    paragraphs=[
                        "When a real recovery is required, the team should confirm the business objective, chosen restore point, and acceptable data-loss window before taking action. Recovery work must be controlled because restoring the wrong point or reopening a system too early can create a second incident on top of the original problem.",
                    ],
                    subsections=[
                        sub(
                            "Step 6.1 Approve Restore Point and Start Recovery",
                            bullets=[
                                "Confirm the selected restore point with the incident lead and system owner.",
                                "Record the expected data-loss window and rationale for the chosen point.",
                                "Begin restoration using the approved runbook and note each major action.",
                            ],
                        ),
                        sub(
                            "Step 6.2 Validate Before Reopening",
                            bullets=[
                                "Check data completeness, application behavior, and security controls before enabling user access.",
                                "Confirm dependent systems or downstream jobs will not reintroduce corruption or inconsistency.",
                                "Reopen service only after the designated approver confirms validation is sufficient.",
                            ],
                        ),
                    ],
                ),
            ],
            exception_guidance=[
                "Any system in scope that cannot meet the backup or restore control sequence requires a documented exception, owner, risk statement, and remediation plan. Teams should not normalize weak recovery posture by treating it as a temporary inconvenience without time-bound follow-up.",
                "Escalate immediately if backup failures persist, if restore drills reveal unusable data, or if recovery timing materially exceeds the agreed objective. Backup confidence erodes quickly when gaps are known but not acted on.",
            ],
            records_and_review=[
                "Backup logs, restore drill outcomes, exception records, and real recovery timelines must be stored in approved operational systems. These records support audit, resilience review, and faster recovery the next time an event occurs.",
                "Infrastructure Operations reviews backup coverage and recovery performance quarterly and after any major recovery event. Repeated manual recovery steps should trigger automation or runbook improvements rather than repeated acceptance of the same risk.",
            ],
        ),
    ]


def operations_documents() -> list[DocumentSpec]:
    return [
        DocumentSpec(
            title="Operations Incident Management Guide",
            department="operations",
            filename="operations_incident_management_v1.pdf",
            version="1.1",
            owner_role="Operations Program Manager",
            access_level="Internal - Operations",
            summary="This guide explains how operations teams coordinate incidents, maintain records, and support specialist responders from intake through closure.",
            purpose=[
                "This guide helps operations teams act as the coordination layer during incidents without confusing that role with technical ownership. In a production-level RAG dataset, the guide should answer what operations does first, how records are maintained, and how handoffs are managed when multiple specialist teams become involved.",
                "The document exists because incidents often fail operationally before they fail technically. Missing records, unclear escalation, and inconsistent stakeholder updates slow down recovery and make later review less reliable. A structured operations guide reduces those gaps.",
            ],
            scope=[
                "This guide applies to incidents where operations is responsible for intake, coordination, stakeholder communication, or record maintenance. It is used alongside engineering or security response procedures when a technical or compliance specialist owns direct remediation.",
                "The guide covers intake, triage, communication, documentation, handoff, and closure. It does not replace product-specific technical runbooks, but it does define the coordination standards that should remain consistent across incidents.",
            ],
            scope_bullets=[
                "Applies to operational incidents, escalations, and service disruptions requiring multi-team coordination.",
                "Defines record-keeping and communication expectations for operations responders.",
                "Requires explicit handoff when technical ownership moves to another team.",
            ],
            responsibilities={
                "Operations Coordinator": [
                    "Open and maintain the incident record, time-stamp major actions, and track current ownership.",
                    "Ensure updates are issued on time and routed to the correct internal audience.",
                    "Drive handoff quality when engineering, security, or vendor teams become primary responders.",
                ],
                "Specialist Responders": [
                    "Provide clear technical or domain updates that operations can relay accurately.",
                    "Confirm current impact, mitigation progress, and next expected action at each update point.",
                    "Notify operations promptly when incident scope, severity, or ownership changes.",
                ],
                "Operations Leadership": [
                    "Support escalation decisions, stakeholder alignment, and closure review quality.",
                    "Help remove coordination bottlenecks when multiple teams are involved.",
                    "Review recurring operational failure points and improve the guide accordingly.",
                ],
            },
            body_sections=[
                section(
                    "Incident Intake and Triage",
                    paragraphs=[
                        "Operations should begin by validating the initial report, confirming whether an incident record already exists, and identifying the likely system or workflow affected. The goal at this stage is not perfect diagnosis but enough structure to establish ownership and keep information from scattering across private channels.",
                        "Triage should capture customer or business impact, detection source, current severity if known, and the next expected update time. Operations should avoid oversummarizing unclear information and instead distinguish facts, assumptions, and open questions explicitly in the record.",
                    ],
                    bullets=[
                        "Create the incident record and note source, impact, affected service, and current severity.",
                        "Identify the current technical owner or request one through the escalation route.",
                        "Confirm the next communication checkpoint before moving deeper into diagnosis.",
                    ],
                ),
                section(
                    "Coordination and Documentation Standards",
                    paragraphs=[
                        "Operations records should be complete enough that another team can understand what happened without needing private screenshots, missing chat context, or verbal memory. This means every major decision, mitigation, handoff, and status change should be time-stamped and attributed clearly.",
                        "Documentation quality directly affects recovery quality. When operations maintains a stable record, responders spend less time repeating themselves and leaders can make decisions based on a coherent timeline rather than fragmented updates from multiple channels.",
                        "A durable record also helps post-incident review remain objective. When timestamps, owners, and stakeholder updates are preserved in one place, the team can evaluate where coordination added value and where it introduced delay instead of debating from incomplete recollection after the pressure has passed.",
                    ],
                    bullets=[
                        "Log every escalation, major mitigation, severity change, and stakeholder update.",
                        "Record who owns the current action and when the next update is due.",
                        "Attach links to dashboards, tickets, or status pages used during the incident.",
                    ],
                ),
                section(
                    "Handoff and Closure",
                    paragraphs=[
                        "A handoff should be treated as a controlled transfer of context, not an informal mention in chat. When another team takes primary ownership, operations should provide current impact, actions completed, open questions, known risks, and the next communication commitment so the receiving team does not restart discovery from scratch.",
                        "Closure requires more than technical recovery. Operations should confirm that internal stakeholders received final status, open follow-up items have named owners, and the record is complete enough for review. A technically resolved incident with incomplete operational closure still creates governance and learning gaps.",
                    ],
                    bullets=[
                        "Include impact, actions completed, open blockers, and next update time in every handoff.",
                        "Confirm recovery and communication completion before marking the incident closed.",
                        "Assign follow-up actions for gaps in process, tooling, or stakeholder management.",
                    ],
                ),
            ],
            exception_guidance=[
                "If standard communication channels or record systems are unavailable, operations must document the fallback method being used and migrate the record back into the primary system as soon as practical. A temporary workaround should never become a permanent evidence gap.",
                "Escalate when there is no clear technical owner, update cadence is slipping, or stakeholder expectations are misaligned with the current severity. Coordination breakdown can prolong incidents even when technical mitigation is progressing.",
            ],
            records_and_review=[
                "Incident records, handoff notes, stakeholder updates, and closure summaries should be stored in approved operational systems. The record should allow someone outside the live response to follow the timeline accurately.",
                "Operations reviews incident handling quality quarterly, with particular attention to delayed escalation, incomplete records, or weak handoffs. The guide should evolve when the same coordination failure repeats.",
                "Review outcomes should be linked to measurable changes in templates, communication expectations, or responder training so lessons become operating improvements rather than standalone observations.",
            ],
        ),
        DocumentSpec(
            title="Operations Escalation Matrix",
            department="operations",
            filename="operations_escalation_matrix_v1.pdf",
            version="1.1",
            owner_role="Business Operations Director",
            access_level="Internal - Operations",
            summary="This matrix defines escalation triggers, routing paths, and communication expectations for operational issues that exceed normal triage boundaries.",
            purpose=[
                "The escalation matrix exists so operational issues are routed quickly to the right team with enough context to act. In a production-level RAG dataset, this document should help users retrieve when to escalate, whom to escalate to, and what information must accompany the escalation so time is not lost on avoidable clarification.",
                "The matrix also protects teams from relying on personal networks or memory when an issue becomes time-sensitive. Standardized escalation paths improve accountability, reduce handoff ambiguity, and make recurring response patterns easier to review and improve.",
            ],
            scope=[
                "This matrix applies to operational issues that exceed frontline triage, involve significant customer or compliance risk, or require specialist intervention from engineering, security, finance systems, HR operations, or leadership.",
                "The document covers escalation triggers, tiered routing, acknowledgement expectations, and governance review. It is not intended to replace technical runbooks, but it should be used whenever routing uncertainty could delay resolution.",
            ],
            scope_bullets=[
                "Applies to service disruption, access anomalies, finance-impacting failures, and compliance-sensitive incidents.",
                "Defines tiered routing and communication expectations across support and specialist teams.",
                "Requires a concise escalation packet rather than informal one-line requests for help.",
            ],
            responsibilities={
                "Operations and Service Desk": [
                    "Validate the issue, create the initial record, and escalate when triggers are met.",
                    "Provide enough context for the receiving team to begin action without avoidable delay.",
                    "Track acknowledgement and follow up if response targets are missed.",
                ],
                "Receiving Specialist Teams": [
                    "Acknowledge escalations within the expected response window for the severity level.",
                    "Confirm ownership, request missing information quickly, and communicate next actions.",
                    "Escalate further when the issue exceeds the team's authority or expertise.",
                ],
                "Operations Leadership": [
                    "Maintain escalation contacts, thresholds, and governance review of the matrix.",
                    "Resolve routing ambiguity when cross-functional ownership is unclear.",
                    "Review repeated misrouting or delayed acknowledgement as process issues, not one-off mistakes.",
                ],
            },
            body_sections=[
                section(
                    "Escalation Triggers",
                    paragraphs=[
                        "Operations should escalate when an issue exceeds standard response thresholds, introduces material customer or compliance risk, or requires specialist expertise that frontline teams do not possess. The goal is to move the issue while it is still manageable rather than waiting until the blast radius becomes obvious to everyone.",
                        "Escalation triggers should be interpreted consistently. If a team repeatedly hesitates to escalate because the threshold feels unclear, that is a sign the matrix or training needs improvement. Delayed escalation is rarely neutral; it usually shifts complexity into a later and more stressful response window.",
                    ],
                    bullets=[
                        "Customer-facing outage or degradation lasting beyond the defined threshold without a viable workaround.",
                        "Repeated payment, identity, access, or provisioning failures affecting multiple users or accounts.",
                        "Security suspicion, data exposure concern, or privileged-access anomaly.",
                        "Vendor dependency outage that blocks a core operational workflow.",
                    ],
                ),
                section(
                    "Tiered Routing and Escalation Packet",
                    paragraphs=[
                        "Tiered routing helps the responder identify the right destination quickly without skipping important context. Tier 1 covers initial validation, Tier 2 covers specialist domain ownership, and Tier 3 involves command-level or leadership escalation when business risk is high or authority is needed to make decisions quickly.",
                        "Every escalation should include a concise but complete packet: summary, severity, customer or business impact, current state, actions already taken, and the help being requested. Weak escalation messages slow the receiving team because they must reconstruct the situation before acting.",
                    ],
                    subsections=[
                        sub(
                            "Tiered Routing",
                            bullets=[
                                "Tier 1: Service desk or operations triage validates the issue and opens the record.",
                                "Tier 2: Domain specialists such as engineering, finance systems, HR operations, or support tooling owners.",
                                "Tier 3: Incident command, security lead, or executive sponsor for critical business risk.",
                            ],
                        ),
                        sub(
                            "Escalation Packet Standard",
                            bullets=[
                                "Include summary, severity, business impact, current mitigation status, and requested support.",
                                "Add links to tickets, dashboards, logs, or user reports when they materially help triage.",
                                "State the next required response time when urgency is high.",
                            ],
                        ),
                    ],
                ),
                section(
                    "Acknowledgement and Governance",
                    paragraphs=[
                        "Receiving teams should acknowledge escalations within the response target for the issue severity, even if full diagnosis has not begun. Acknowledgement confirms ownership and prevents the issue from remaining in a routing void where multiple teams assume someone else is acting.",
                        "Governance matters because escalations reveal organizational friction. Misrouting, delayed acknowledgement, or repeated confusion about who owns a problem are signals that the matrix, contact model, or team boundaries need refinement rather than quiet workarounds.",
                        "Teams should treat the matrix as a living operational control. When services change, vendors shift, or team boundaries move, routing assumptions can become stale quickly unless ownership data and threshold language are maintained intentionally.",
                    ],
                    bullets=[
                        "Track acknowledgement time and escalate again if ownership is not confirmed on time.",
                        "Review repeated routing failures and stale contacts during quarterly matrix governance.",
                        "Update the matrix whenever team ownership, vendor responsibilities, or response targets change.",
                    ],
                ),
            ],
            exception_guidance=[
                "If the standard escalation owner is unavailable or the issue spans multiple domains, operations leadership should assign interim ownership immediately and document the alternate route used. The absence of a perfect owner is not a reason to delay escalation.",
                "Escalate to leadership when acknowledgements are missed repeatedly, when multiple teams dispute ownership, or when the business impact requires authority beyond normal specialist routing.",
            ],
            records_and_review=[
                "Escalation timestamps, acknowledgement times, routing destination, and final resolution path should be captured in the incident or ticket record. These data points are necessary for measuring how well the matrix works in practice.",
                "The matrix is reviewed quarterly by operations, engineering, security, and other affected functions. Contact details, thresholds, and routing language should be updated proactively instead of after a failure exposes stale assumptions.",
            ],
        ),
    ]


def get_document_specs() -> list[DocumentSpec]:
    specs = hr_documents() + onboarding_documents() + engineering_documents() + sop_documents() + operations_documents()
    validate_document_specs(specs)
    return specs


def build_faq_entries() -> list[dict[str, str]]:
    return [
        {"question": "How far in advance should I request annual leave?", "answer": "Submit one- or two-day annual leave at least three business days in advance and longer leave at least ten business days in advance unless an emergency prevents advance notice."},
        {"question": "Can a manager approve leave only in chat or email?", "answer": "No. Informal discussion can happen in chat or email, but the request must be entered and approved in the HRIS because that record drives payroll, attendance, and audit visibility."},
        {"question": "What should I do if I wake up sick and cannot work?", "answer": "Notify your manager as early as possible, record the absence in the HRIS when you are able, and share medical documentation only with People Operations when policy or local law requires it."},
        {"question": "Where can I see my benefits options and payroll deductions?", "answer": "Use the internal benefits portal or HRIS benefits section, which contains plan summaries, contribution details, carrier contacts, and enrollment confirmation records."},
        {"question": "Who should I contact about a workplace conduct concern?", "answer": "Raise the concern through your manager, Human Resources, or the confidential ethics route. If the issue involves your manager or retaliation risk, bypass the local reporting line and contact HR directly."},
        {"question": "What should happen before my first day?", "answer": "Your manager, People Operations, and IT should complete role setup, payroll preparation, identity provisioning, and orientation scheduling before day one so your first week is not blocked by avoidable setup issues."},
        {"question": "What are the most important first-day tasks for a new hire?", "answer": "You should confirm access to core systems, verify HR and payroll details, attend orientation, meet your manager and onboarding buddy, and raise any missing access immediately through the onboarding queue."},
        {"question": "Who approves role-based system access for a new hire?", "answer": "The hiring manager validates the role-based access need, and IT Operations provisions it through approved templates and least-privilege controls."},
        {"question": "What access is considered baseline during onboarding?", "answer": "Baseline access usually includes email, calendar, chat, HRIS, ticketing, documentation, and password manager access, plus company-required device and MFA controls."},
        {"question": "When should missing onboarding access be escalated?", "answer": "Escalate immediately when missing access affects mandatory training, payroll, security setup, or the employee's ability to begin first-week work."},
        {"question": "What makes an API ready for release?", "answer": "An API is release-ready when its contract is documented, validation and error behavior are clear, auth controls are in place, observability exists, and required testing and review evidence are complete."},
        {"question": "Should APIs return generic errors?", "answer": "No. Production APIs should return structured errors with machine-readable codes, human-readable guidance, and a correlation identifier that maps to logs or traces."},
        {"question": "What belongs in a pull request description?", "answer": "A strong pull request description explains behavior change, user impact, risks, rollout needs, validation steps, and any documentation or follow-up work required for safe review and release."},
        {"question": "When do I need integration tests instead of only unit tests?", "answer": "Use integration tests when the change affects persistence, service contracts, external dependencies, or runtime behavior that isolated unit tests cannot validate realistically."},
        {"question": "What should I verify after deploying a service?", "answer": "Verify critical user flows, health checks, dashboards, error rates, latency, queue depth, and any business signals that reflect the change after deployment."},
        {"question": "When should a release be rolled back?", "answer": "Rollback when the release causes material customer impact, sustained instability, authentication failure, or data integrity risk and the rollback path is safer than continuing forward."},
        {"question": "What is the first action in a high-severity incident?", "answer": "Classify the severity, open the incident record and response channel, assign an incident commander, and begin mitigation planning before deep root-cause analysis."},
        {"question": "How often should incident updates be posted?", "answer": "Active high-severity incidents should usually receive updates every fifteen to thirty minutes with current impact, actions taken, and the next expected update time."},
        {"question": "What should be captured in an incident record?", "answer": "Capture severity changes, responder assignments, timeline entries, mitigation actions, stakeholder communications, and closure evidence in the incident record."},
        {"question": "Why do restore drills matter if backups are completing successfully?", "answer": "Because a successful backup job does not prove a usable recovery. Restore drills confirm timing, data integrity, operational usability, and the quality of the runbook under realistic conditions."},
        {"question": "What should happen before a production recovery is started?", "answer": "The incident lead and system owner should confirm the business objective, selected restore point, expected data-loss window, and approval to begin the recovery procedure."},
        {"question": "When should operations escalate beyond normal triage?", "answer": "Escalate when an issue exceeds response thresholds, introduces customer or compliance risk, affects multiple accounts, or needs expertise outside frontline operations."},
        {"question": "What belongs in an escalation message?", "answer": "Include a concise summary, severity, business impact, actions taken, current blockers, requested support, and links to evidence such as tickets or dashboards."},
        {"question": "Who owns communication during an operational incident?", "answer": "The operations coordinator or incident commander owns communication cadence, while specialist responders provide the current facts and technical status needed for accurate updates."},
        {"question": "What makes a good operational handoff?", "answer": "A good handoff includes current impact, work already completed, open questions, known risks, current owner, and the next expected update time so the receiving team does not lose context."},
        {"question": "How often should the escalation matrix be reviewed?", "answer": "The escalation matrix should be reviewed at least quarterly and any time team ownership, vendor responsibility, or response thresholds change materially."},
    ]


def write_metadata(root: Path, metadata_entries: list[dict[str, Any]]) -> None:
    (root / "metadata.json").write_text(json.dumps(metadata_entries, indent=2), encoding="utf-8")


def write_faq(root: Path, faq_entries: list[dict[str, str]]) -> None:
    (root / "faq" / "faq_data.json").write_text(json.dumps(faq_entries, indent=2), encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    data_root = repo_root / "data"
    create_output_folders(data_root)

    specs = get_document_specs()
    faq_entries = build_faq_entries()
    metadata_entries: list[dict[str, Any]] = []

    for spec in specs:
        metadata = generate_metadata(spec)
        metadata_entries.append(metadata)
        create_pdf(data_root / spec.department / spec.filename, spec, generate_content(spec), metadata)

    write_metadata(data_root, metadata_entries)
    write_faq(data_root, faq_entries)

    print(f"Generated {len(specs)} PDF documents in {data_root}")
    print(f"Generated {len(faq_entries)} FAQ entries in {data_root / 'faq' / 'faq_data.json'}")


if __name__ == "__main__":
    main()
