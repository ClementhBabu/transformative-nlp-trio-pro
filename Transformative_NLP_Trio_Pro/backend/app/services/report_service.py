import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)


def generate_report_filename(user_id) -> str:
    uid = str(user_id).replace("-", "")[:8]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"report_{uid}_{timestamp}_{unique_id}.pdf"


def _register_fonts():
    import reportlab

    font_dir = os.path.join(os.path.dirname(reportlab.__file__), "fonts")
    search_paths = [font_dir]

    for path in ["/usr/share/fonts", "/Library/Fonts", "/System/Library/Fonts"]:
        if os.path.isdir(path):
            search_paths.append(path)

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font_files = {
        "DejaVuSans": "DejaVuSans.ttf",
        "DejaVuSans-Bold": "DejaVuSans-Bold.ttf",
        "DejaVuSans-Oblique": "DejaVuSans-Oblique.ttf",
        "DejaVuSans-BoldOblique": "DejaVuSans-BoldOblique.ttf",
        "NotoSansCJK": "NotoSansCJK-Regular.ttc",
    }

    for font_name, font_file in font_files.items():
        if font_name in pdfmetrics._fonts:
            continue
        for base_dir in search_paths:
            for root, _, files in os.walk(base_dir):
                if font_file in files:
                    full_path = os.path.join(root, font_file)
                    try:
                        if font_name == "NotoSansCJK":
                            pdfmetrics.registerFont(TTFont("NotoSansCJK-Regular", full_path, subfontIndex=0))
                            pdfmetrics.registerFont(TTFont("NotoSansCJK-Bold", full_path, subfontIndex=1))
                        else:
                            pdfmetrics.registerFont(TTFont(font_name, full_path))
                        logger.info("Registered font: %s from %s", font_name, full_path)
                    except Exception as e:
                        logger.warning("Failed to register font %s: %s", font_name, str(e))
                    break


def generate_pdf_report(
    processing_data: Dict[str, Any],
    user_info: Optional[Dict[str, Any]] = None,
) -> str:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    )
    from reportlab.pdfbase import pdfmetrics

    _register_fonts()

    os.makedirs(settings.REPORTS_DIR, exist_ok=True)

    user_id = user_info.get("id", "unknown") if user_info else "unknown"
    filename = generate_report_filename(user_id)
    output_path = os.path.join(settings.REPORTS_DIR, filename)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="NLP Trio Pro - Processing Report",
    )

    available_fonts = [f for f in ["DejaVuSans", "Helvetica"] if f in pdfmetrics._fonts]
    body_font = available_fonts[0] if available_fonts else "Helvetica"
    bold_font = "DejaVuSans-Bold" if "DejaVuSans-Bold" in pdfmetrics._fonts else "Helvetica-Bold"
    code_font = "DejaVuSans-Oblique" if "DejaVuSans-Oblique" in pdfmetrics._fonts else "Helvetica-Oblique"

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontName=bold_font,
        fontSize=24,
        textColor=colors.HexColor("#1a237e"),
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontName=body_font,
        fontSize=11,
        textColor=colors.HexColor("#546e7a"),
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontName=bold_font,
        fontSize=14,
        textColor=colors.HexColor("#283593"),
        spaceBefore=14,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontName=body_font,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#212121"),
        spaceAfter=6,
    )

    code_style = ParagraphStyle(
        "CodeBlock",
        parent=styles["Normal"],
        fontName=code_font,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#37474f"),
        backColor=colors.HexColor("#f5f5f5"),
        borderWidth=0.5,
        borderColor=colors.HexColor("#e0e0e0"),
        borderPadding=8,
        spaceAfter=10,
    )

    bold_body_style = ParagraphStyle(
        "BoldBody",
        parent=body_style,
        fontName=bold_font,
    )

    story = []

    story.append(Paragraph("NLP Trio Pro", title_style))
    story.append(Paragraph("AI Processing Report", subtitle_style))

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    story.append(Paragraph(f"Generated: {now}", body_style))

    if user_info:
        user_text = f"User: {user_info.get('name', 'N/A')} ({user_info.get('email', 'N/A')})"
        story.append(Paragraph(user_text, body_style))

    story.append(Spacer(1, 6 * mm))

    header_data = [["Report Summary"]]
    header_table = Table(header_data, colWidths=[doc.width * 0.9])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1a237e")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), bold_font),
        ("FONTSIZE", (0, 0), (-1, -1), 13),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [3, 3, 3, 3]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 5 * mm))

    info_data = [
        [Paragraph("<b>Field</b>", bold_body_style),
         Paragraph("<b>Value</b>", bold_body_style)],
        [Paragraph("Date", body_style),
         Paragraph(now, body_style)],
        [Paragraph("Original Text Length", body_style),
         Paragraph(f"{len(processing_data.get('original_text', ''))} chars", body_style)],
    ]

    if processing_data.get("source_language"):
        info_data.append([
            Paragraph("Source Language", body_style),
            Paragraph(str(processing_data["source_language"]), body_style),
        ])
    if processing_data.get("target_language"):
        info_data.append([
            Paragraph("Target Language", body_style),
            Paragraph(str(processing_data["target_language"]), body_style),
        ])

    info_table = Table(info_data, colWidths=[doc.width * 0.3, doc.width * 0.55])
    info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdbdbd")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eaf6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 5 * mm))

    original_text = processing_data.get("original_text", "")
    if original_text:
        story.append(Paragraph("Original Text", heading_style))
        cleaned = original_text.replace("<", "&lt;").replace(">", "&gt;")
        truncated = cleaned[:3000] + ("..." if len(cleaned) > 3000 else "")
        story.append(Paragraph(truncated, code_style))

    summary_text = processing_data.get("summary", "")
    if summary_text:
        story.append(Paragraph("Summary", heading_style))
        cleaned = summary_text.replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(cleaned, body_style))

    translation = processing_data.get("translation", "")
    if translation:
        story.append(Paragraph("Translation", heading_style))
        cleaned = translation.replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(cleaned, body_style))

    sentiment = processing_data.get("sentiment")
    if sentiment:
        story.append(Paragraph("Sentiment Analysis", heading_style))
        if isinstance(sentiment, dict):
            label = sentiment.get("label", "N/A")
            score = sentiment.get("score", 0)
            polarity = sentiment.get("polarity")
            subjectivity = sentiment.get("subjectivity")

            sentiment_data = [
                [Paragraph("Sentiment", bold_body_style), Paragraph(str(label), body_style)],
                [Paragraph("Confidence", bold_body_style), Paragraph(f"{score:.2%}", body_style)],
            ]
            if polarity is not None:
                sentiment_data.append([Paragraph("Polarity", bold_body_style),
                                       Paragraph(f"{polarity:.3f}", body_style)])
            if subjectivity is not None:
                sentiment_data.append([Paragraph("Subjectivity", bold_body_style),
                                       Paragraph(f"{subjectivity:.3f}", body_style)])

            sent_table = Table(sentiment_data, colWidths=[doc.width * 0.25, doc.width * 0.55])
            sent_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdbdbd")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fce4ec")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(sent_table)

    keywords = processing_data.get("keywords")
    if keywords:
        story.append(Paragraph("Keywords", heading_style))
        if isinstance(keywords, list):
            kw_text = ", ".join(
                k["keyword"] if isinstance(k, dict) else str(k)
                for k in keywords[:20]
            )
        else:
            kw_text = str(keywords)
        story.append(Paragraph(kw_text, body_style))

    meeting_minutes = processing_data.get("meeting_minutes")
    if meeting_minutes and isinstance(meeting_minutes, dict):
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph("Meeting Minutes", heading_style))

        minutes = meeting_minutes.get("meeting_minutes", meeting_minutes)
        title = minutes.get("title", "Untitled")
        story.append(Paragraph(f"Title: {title}", bold_body_style))

        actions = minutes.get("action_items", [])
        if actions:
            story.append(Paragraph("Action Items:", bold_body_style))
            for item in actions[:10]:
                assignee = item.get("assignee", "Unassigned")
                task = item.get("task", "")
                story.append(Paragraph(f"• <b>{assignee}</b>: {task}", body_style))

        deadlines = minutes.get("deadlines", [])
        if deadlines:
            story.append(Paragraph("Deadlines:", bold_body_style))
            for d in deadlines[:5]:
                story.append(Paragraph(f"• {d.get('description', d.get('deadline', ''))}", body_style))

        discussions = minutes.get("key_discussions", [])
        if discussions:
            story.append(Paragraph("Key Discussions:", bold_body_style))
            for d in discussions[:5]:
                story.append(Paragraph(f"• {d.get('topic', str(d))}", body_style))

    story.append(Spacer(1, 10 * mm))
    footer_text = f"Generated by {settings.APP_NAME} v{settings.APP_VERSION}"
    story.append(Paragraph(footer_text,
                           ParagraphStyle("Footer", parent=body_style, fontSize=8,
                                          textColor=colors.HexColor("#9e9e9e"), alignment=1)))

    doc.build(story)
    logger.info("PDF report generated: %s", output_path)
    return output_path
