import json
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.incident import Incident


def _json_list(value: str) -> list[str]:
    try:
        return json.loads(value or "[]")
    except (TypeError, ValueError):
        return []


def generate_incident_report_pdf(incident: Incident) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Disaster Incident Report", styles["Title"]))
    story.append(Paragraph(f"Incident #{incident.id} &mdash; {incident.title}", styles["Heading2"]))
    story.append(Paragraph(f"Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    story.append(Spacer(1, 0.6 * cm))

    overview_rows = [
        ["Status", incident.status],
        ["Disaster type", incident.disaster_type],
        ["Location", incident.location],
        ["Severity", incident.severity],
        ["Priority", incident.priority_level],
        ["Risk score", f"{incident.risk_score}/100"],
        ["People affected", str(incident.people_affected)],
        ["Injuries", str(incident.injuries)],
        ["Reported at", incident.created_at.strftime("%Y-%m-%d %H:%M UTC")],
        ["Last updated", incident.updated_at.strftime("%Y-%m-%d %H:%M UTC")],
    ]
    table = Table(overview_rows, colWidths=[5 * cm, 10 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.6 * cm))

    story.append(Paragraph("Description", styles["Heading3"]))
    story.append(Paragraph(incident.description or "-", styles["Normal"]))
    if incident.additional_info:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph("Additional information from reporter", styles["Heading3"]))
        story.append(Paragraph(incident.additional_info, styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    hazards = _json_list(incident.secondary_hazards)
    if hazards:
        story.append(Paragraph("Secondary hazards", styles["Heading3"]))
        for hazard in hazards:
            story.append(Paragraph(f"&bull; {hazard}", styles["Normal"]))
        story.append(Spacer(1, 0.3 * cm))

    recommendations = _json_list(incident.immediate_recommendations)
    if recommendations:
        story.append(Paragraph("AI-recommended actions", styles["Heading3"]))
        for rec in recommendations:
            story.append(Paragraph(f"&bull; {rec}", styles["Normal"]))
        story.append(Spacer(1, 0.3 * cm))

    if incident.allocations:
        allocation = incident.allocations[-1]
        story.append(Paragraph("Recommended resource allocation", styles["Heading3"]))
        alloc_rows = [
            ["Ambulances", str(allocation.ambulances)],
            ["Rescue teams", str(allocation.rescue_teams)],
            ["Vehicles", str(allocation.vehicles)],
            ["Food kits", str(allocation.food_kits)],
            ["Water (liters)", str(allocation.water_liters)],
            ["Shelters", str(allocation.shelters)],
        ]
        alloc_table = Table(alloc_rows, colWidths=[5 * cm, 10 * cm])
        alloc_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        story.append(alloc_table)
        story.append(Spacer(1, 0.4 * cm))

    if incident.assignments:
        story.append(Paragraph("Department response summary", styles["Heading3"]))
        dept_rows = [["Department", "Status", "Officer", "Action taken"]]
        for assignment in incident.assignments:
            report = assignment.action_report
            dept_rows.append(
                [
                    assignment.department.name,
                    assignment.status,
                    report.officer_name if report else "-",
                    (report.action_taken[:80] + "...") if report and len(report.action_taken) > 80 else (report.action_taken if report else "-"),
                ]
            )
        dept_table = Table(dept_rows, colWidths=[4 * cm, 2.5 * cm, 3 * cm, 5.5 * cm])
        dept_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(dept_table)

    doc.build(story)
    return buffer.getvalue()
