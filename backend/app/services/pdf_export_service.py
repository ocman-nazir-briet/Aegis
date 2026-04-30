import logging
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)


class PDFExportService:
    """Generate PDF reports for simulation results."""

    @staticmethod
    def export_simulation_result(result: Dict[str, Any], repo_url: str = "") -> Optional[bytes]:
        """Generate a PDF report from a simulation result."""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=0.5 * inch,
                leftMargin=0.5 * inch,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch,
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1f2937"),
                spaceAfter=6,
                alignment=TA_CENTER,
            )

            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#374151"),
                spaceAfter=12,
                spaceBefore=12,
            )

            normal_style = ParagraphStyle(
                "CustomBody",
                parent=styles["BodyText"],
                fontSize=11,
                textColor=colors.HexColor("#4b5563"),
            )

            story = []

            # Title
            story.append(Paragraph("🛡️ Aegis Twin — Risk Analysis Report", title_style))
            story.append(Spacer(1, 0.2 * inch))

            # Risk Summary
            risk_score = result.get("risk_score", "Unknown")
            confidence = result.get("confidence", 0)
            story.append(Paragraph("Risk Assessment", heading_style))

            risk_color_map = {
                "Low": colors.HexColor("#22c55e"),
                "Medium": colors.HexColor("#f59e0b"),
                "High": colors.HexColor("#f97316"),
                "Critical": colors.HexColor("#ef4444"),
            }
            risk_color = risk_color_map.get(risk_score, colors.black)

            risk_data = [
                [
                    Paragraph("Risk Level", normal_style),
                    Paragraph(f"<b style='color:#{risk_color.hexval()[1:]}'>{risk_score}</b>", normal_style),
                ],
                [
                    Paragraph("Confidence", normal_style),
                    Paragraph(f"{confidence * 100:.1f}%", normal_style),
                ],
                [
                    Paragraph("Report Date", normal_style),
                    Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), normal_style),
                ],
            ]

            if repo_url:
                risk_data.append([Paragraph("Repository", normal_style), Paragraph(repo_url, normal_style)])

            risk_table = Table(risk_data, colWidths=[2 * inch, 3 * inch])
            risk_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1f2937")),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 11),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
                    ]
                )
            )
            story.append(risk_table)
            story.append(Spacer(1, 0.3 * inch))

            # Blast Radius
            blast_radius = result.get("blast_radius", {})
            if blast_radius:
                story.append(Paragraph("Blast Radius", heading_style))
                radius_data = [
                    [Paragraph("Services", normal_style), Paragraph(str(blast_radius.get("services", 0)), normal_style)],
                    [Paragraph("Endpoints", normal_style), Paragraph(str(blast_radius.get("endpoints", 0)), normal_style)],
                    [Paragraph("Databases", normal_style), Paragraph(str(blast_radius.get("databases", 0)), normal_style)],
                ]
                radius_table = Table(radius_data, colWidths=[2 * inch, 3 * inch])
                radius_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("FONTSIZE", (0, 0), (-1, -1), 11),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
                        ]
                    )
                )
                story.append(radius_table)
                story.append(Spacer(1, 0.3 * inch))

            # Analysis
            explanation = result.get("explanation", "")
            if explanation:
                story.append(Paragraph("Analysis", heading_style))
                story.append(Paragraph(explanation, normal_style))
                story.append(Spacer(1, 0.2 * inch))

            # Mitigations
            mitigations = result.get("mitigations", [])
            if mitigations:
                story.append(Paragraph("Recommended Mitigations", heading_style))
                for i, mitigation in enumerate(mitigations, 1):
                    story.append(Paragraph(f"{i}. {mitigation}", normal_style))
                    story.append(Spacer(1, 0.1 * inch))

            # Generate PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            return None
