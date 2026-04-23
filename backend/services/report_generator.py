from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter


def generate_pdf(results, company_name="HireSmart AI"):

    file_path = "HireSmart_Report.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=letter)

    styles = getSampleStyleSheet()

    # =========================
    # 🎨 CUSTOM STYLES
    # =========================
    title_style = ParagraphStyle(
        name="Title",
        fontSize=22,
        alignment=1,
        textColor=colors.HexColor("#111827"),
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        name="Subtitle",
        fontSize=10,
        alignment=1,
        textColor=colors.HexColor("#6b7280"),
        spaceAfter=20
    )

    normal_style = ParagraphStyle(
        name="Normal",
        fontSize=10,
        textColor=colors.HexColor("#374151"),
        leading=14
    )

    # 🔥 NEW: table text wrap style
    table_text = ParagraphStyle(
        name="TableText",
        fontSize=9,
        leading=12,
        wordWrap="CJK"   # fixes overlapping
    )

    elements = []

    # =========================
    # 🏢 HEADER SECTION (DYNAMIC)
    # =========================
    elements.append(Paragraph(company_name, title_style))
    elements.append(Paragraph("Candidate Screening Report", subtitle_style))

    # =========================
    # 🏆 SUMMARY TABLE
    # =========================
    table_data = [["Rank", "Candidate", "Score", "Status"]]

    for i, r in enumerate(results, start=1):
        table_data.append([
            str(i),
            Paragraph(r["name"], table_text),  # ✅ wrapped text
            f"{r['match_score']}%",
            r["classification"]
        ])

    table = Table(table_data, colWidths=[40, 260, 70, 90])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 25))

    # =========================
    # 📦 DETAILED CARDS
    # =========================
    for i, item in enumerate(results, start=1):

        # Rank badge
        if i == 1:
            badge = "🏆 Top Candidate"
        elif i == 2:
            badge = "🥈 Second Best"
        elif i == 3:
            badge = "🥉 Third Best"
        else:
            badge = f"Rank {i}"

        # Status color
        if item["classification"] == "Suitable":
            status_color = "#16a34a"
        elif item["classification"] == "Moderate":
            status_color = "#f59e0b"
        else:
            status_color = "#dc2626"

        content = f"""
        <b>{badge}</b><br/>
        <b>{item['name']}</b><br/><br/>
        Score: <b>{item['match_score']}%</b><br/>
        Status: <font color="{status_color}"><b>{item['classification']}</b></font><br/><br/>
        <b>Matched Skills:</b> {", ".join(item['matched_skills']) or "None"}<br/>
        <b>Missing Skills:</b> {", ".join(item['missing_skills']) or "None"}
        """

        card = Table([[Paragraph(content, normal_style)]], colWidths=[500])

        card.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("PAD", (0, 0), (-1, -1), 14),
        ]))

        elements.append(card)
        elements.append(Spacer(1, 15))

    # =========================
    # BUILD PDF
    # =========================
    doc.build(elements)

    return file_path