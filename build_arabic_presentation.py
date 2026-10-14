import os
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register TrueType Arabic fonts
pdfmetrics.registerFont(TTFont("Arabic", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("ArabicBold", "C:/Windows/Fonts/arialbd.ttf"))

def ar(text: str) -> str:
    """Helper to reshape and reorder Arabic text for ReportLab without breaking tags."""
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def create_presentation_pdf(output_pdf="Pocket_Option_Dashboard_Presentation_AR.pdf"):
    # Landscape Letter: 11 x 8.5 inches (792 x 612 pt)
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=28,
        bottomMargin=28,
    )

    # Color Palette
    c_navy = colors.HexColor("#0F172A")
    c_blue = colors.HexColor("#2563EB")
    c_blue_light = colors.HexColor("#EFF6FF")
    c_emerald = colors.HexColor("#059669")
    c_card = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#CBD5E1")
    c_text = colors.HexColor("#1E293B")
    c_muted = colors.HexColor("#64748B")

    # Typography Styles
    title_style = ParagraphStyle(
        "SlideTitle",
        fontName="ArabicBold",
        fontSize=18,
        leading=24,
        textColor=c_navy,
        alignment=2, # Right aligned
    )

    slide_num_style = ParagraphStyle(
        "SlideNum",
        fontName="ArabicBold",
        fontSize=11,
        leading=15,
        textColor=c_blue,
        alignment=0, # Left aligned
    )

    h2_style = ParagraphStyle(
        "SlideH2",
        fontName="ArabicBold",
        fontSize=12,
        leading=16,
        textColor=c_blue,
        alignment=2,
    )

    body_ar = ParagraphStyle(
        "BodyAR",
        fontName="Arabic",
        fontSize=10,
        leading=15,
        textColor=c_text,
        alignment=2,
    )

    body_ar_bold = ParagraphStyle(
        "BodyARBold",
        fontName="ArabicBold",
        fontSize=10,
        leading=15,
        textColor=c_navy,
        alignment=2,
    )

    bullet_ar = ParagraphStyle(
        "BulletAR",
        fontName="Arabic",
        fontSize=9.5,
        leading=14,
        textColor=c_text,
        alignment=2,
    )

    table_header_ar = ParagraphStyle(
        "TableHeaderAR",
        fontName="ArabicBold",
        fontSize=10,
        leading=13,
        textColor=colors.white,
        alignment=1, # Center
    )

    table_cell_ar = ParagraphStyle(
        "TableCellAR",
        fontName="Arabic",
        fontSize=9,
        leading=13,
        textColor=c_text,
        alignment=2,
    )

    table_cell_bold_ar = ParagraphStyle(
        "TableCellBoldAR",
        fontName="ArabicBold",
        fontSize=9.5,
        leading=13.5,
        textColor=c_navy,
        alignment=2,
    )

    def make_header(slide_number: int, slide_title_ar: str):
        """Standard slide header."""
        header_data = [
            [
                Paragraph(ar(f"الشريحة {slide_number} من 12"), slide_num_style),
                Paragraph(ar(slide_title_ar), title_style),
            ]
        ]
        t = Table(header_data, colWidths=[180, 540])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', (0,0), (-1,-1), 1.5, c_blue),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        return t

    story = []

    # ═════════════════════════════════════════════════════════════════════════════
    # SLIDE 1: COVER
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 40))
    cover_title = ParagraphStyle("CoverTitle", fontName="ArabicBold", fontSize=25, leading=33, textColor=c_navy, alignment=1)
    cover_sub = ParagraphStyle("CoverSub", fontName="Arabic", fontSize=14, leading=20, textColor=c_blue, alignment=1)

    story.append(Paragraph(ar("منظومة حصد وتسجيل بيانات السوق اللحظية — Pocket Option Harvester"), cover_title))
    story.append(Spacer(1, 10))
    story.append(Paragraph(ar("دليل لوحة التحكم التشغيلية ومنظومة الذكاء الاصطناعي (AI/ML Pipeline)"), cover_sub))
    story.append(Spacer(1, 30))

    cover_box = [
        [Paragraph(ar("الإصدار: Enterprise v2.0  |  تسجيل متواصل 24/7 لأسواق OTC والأسواق العالمية المفتوحة"), ParagraphStyle("C1", fontName="ArabicBold", fontSize=11, leading=16, textColor=c_navy, alignment=1))],
        [Paragraph(ar("قواعد البيانات: التخزين المزدوج السحابي (Neon PostgreSQL) والمحلي الاحتياطي (SQLite)"), ParagraphStyle("C2", fontName="Arabic", fontSize=10, leading=15, textColor=c_text, alignment=1))],
        [Paragraph(ar("المراقبة والتنبيهات: بوت تيليجرام فوري للأحداث  |  لوحة ويب لحظية تفاعلية بكامل أدوات التحكم"), ParagraphStyle("C3", fontName="Arabic", fontSize=10, leading=15, textColor=c_text, alignment=1))],
        [Paragraph(ar("تم إعداد هذا العرض التقديمي الشامل لشرح كافة خصائص المنظومة وطريقة تشغيلها للعميل"), ParagraphStyle("C4", fontName="Arabic", fontSize=9.5, leading=14, textColor=c_muted, alignment=1))],
    ]
    t_cover = Table(cover_box, colWidths=[700])
    t_cover.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card),
        ('BOX', (0,0), (-1,-1), 1.5, c_blue),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_cover)
    story.append(PageBreak())

    # ═════════════════════════════════════════════════════════════════════════════
    # SLIDE 2: OBJECTIVES & SCOPE
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(make_header(2, "نظرة عامة على المشروع وأهداف العميل"))
    story.append(Spacer(1, 14))

    obj_rows = [
        [Paragraph(ar("المتطلب الأساسي للعميل"), table_header_ar), Paragraph(ar("الحل التقني المنفذ في المنظومة"), table_header_ar)],
        [
            Paragraph(ar("تسجيل حركة الأسعار والشموع 24/7 دون توقف"), table_cell_bold_ar),
            Paragraph(ar("محرك غير متزامن (AsyncIO) متصل بـ WebSocket آمن مع خوادم Pocket Option، يضمن تسجيل التدفقات اللحظية على مدار الساعة."), table_cell_ar),
        ],
        [
            Paragraph(ar("تغطية أزواج العملات خاصة أسواق OTC"), table_cell_bold_ar),
            Paragraph(ar("دعم كامل لجميع أزواج OTC في عطلات نهاية الأسبوع (مثل USDARS_otc, EURUSD_otc) والأسواق العالمية المفتوحة بدقة فائقة."), table_cell_ar),
        ],
        [
            Paragraph(ar("معالجة انقطاع الاتصال وفجوات الأسعار تلقائياً"), table_cell_bold_ar),
            Paragraph(ar("بروتوكول الاسترجاع الذاتي (Automated Gap Recovery) الذي يرصد الفارق الزمني فور عودة الاتصال ويجلب الشموع المفقودة في أقل من نصف ثانية."), table_cell_ar),
        ],
        [
            Paragraph(ar("واجهة مستخدم سهلة ومراقبة عبر التيليجرام"), table_cell_bold_ar),
            Paragraph(ar("لوحة تحكم ويب تفاعلية مزودة بأزرار البدء والإيقاف ومؤشرات السرعة، مع بوت تيليجرام يرسل إشعارات تشغيلية لحظية للهاتف."), table_cell_ar),
        ],
    ]
    t_obj = Table(obj_rows, colWidths=[240, 480])
    t_obj.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_obj)
    story.append(PageBreak())

    # ═════════════════════════════════════════════════════════════════════════════
    # SLIDE 3: SYSTEM ARCHITECTURE
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(make_header(3, "البنية المعمارية ومسار تدفق البيانات"))
    story.append(Spacer(1, 14))

    arch_rows = [
        [Paragraph(ar("المرحلة"), table_header_ar), Paragraph(ar("المكون البرمجي"), table_header_ar), Paragraph(ar("الدور التشغيلي والضمانات"), table_header_ar)],
        [
            Paragraph(ar("1. الاتصال اللحظي"), table_cell_bold_ar),
            Paragraph(ar("Pocket Option WebSocket API"), table_cell_bold_ar),
            Paragraph(ar("استقبال التكات اللحظية وتدفقات الشموع عبر اتصال WSS مشفر مع إرسال نبضات دورية (Ping) كل 20 ثانية لمنع انقطاع السيرفر."), table_cell_ar),
        ],
        [
            Paragraph(ar("2. المعالجة والتنقية"), table_cell_bold_ar),
            Paragraph(ar("Candle Normalizer & Validator"), table_cell_bold_ar),
            Paragraph(ar("تصفية الشموع قيد التكوين لضمان عدم حفظ سوى الشموع المغلقة نهائياً (Closed Bars)، وتصحيح حدود الهاي واللو لمنع أي أخطاء حسابية."), table_cell_ar),
        ],
        [
            Paragraph(ar("3. التخزين المزدوج"), table_cell_bold_ar),
            Paragraph(ar("Neon PostgreSQL + SQLite"), table_cell_bold_ar),
            Paragraph(ar("حفظ البيانات في قاعدة Neon السحابية كهدف أساسي، مع وجود خيار SQLite المحلي الاحتياطي التلقائي في حال انقطاع السحابة."), table_cell_ar),
        ],
        [
            Paragraph(ar("4. واجهات الإدارة"), table_cell_bold_ar),
            Paragraph(ar("FastAPI Dashboard + Telegram Bot"), table_cell_bold_ar),
            Paragraph(ar("توفير لوحة ويب لحظية وبث السجلات عبر WebSocket، بالتوازي مع تنبيهات البوت الفورية للأحداث الهامة."), table_cell_ar),
        ],
    ]
    t_arch = Table(arch_rows, colWidths=[130, 200, 390])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_blue),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_arch)
    story.append(PageBreak())

    # ═════════════════════════════════════════════════════════════════════════════
    # SLIDE 4: DASHBOARD OVERVIEW
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(make_header(4, "لوحة التحكم المركزية — نظرة شاملة على الواجهة"))
    story.append(Spacer(1, 14))

    dash_intro = "تم تصميم لوحة التحكم لتعمل على المتصفح عبر الرابط http://localhost:8000 بواجهة عصرية داكنة (Dark Mode) تجمع بين سهولة الاستخدام للمستخدم العادي والاحترافية للمتداولين ومطوري الذكاء الاصطناعي."
    story.append(Paragraph(ar(dash_intro), body_ar))
    story.append(Spacer(1, 10))

    dash_parts = [
        [Paragraph(ar("القسم في لوحة التحكم"), table_header_ar), Paragraph(ar("الوظيفة والأهمية"), table_header_ar)],
        [
            Paragraph(ar("1. شريط التحكم العلوي (Master Controls)"), table_cell_bold_ar),
            Paragraph(ar("يحتوي على أزرار التشغيل، الإيقاف المؤقت، الاستئناف، والإيقاف النهائي، مع مؤشر لحالة الجلسة والاتصال."), table_cell_ar),
        ],
        [
            Paragraph(ar("2. بطاقات القياس الرقمية (HUD Cards)"), table_cell_bold_ar),
            Paragraph(ar("تعرض إجمالي الشموع المسجلة، سرعة الحفظ بالدقيقة، زمن استجابة السيرفر، ونوع قاعدة البيانات المتصلة."), table_cell_ar),
        ],
        [
            Paragraph(ar("3. محدد الأزواج والفريم الزمني (Config)"), table_cell_bold_ar),
            Paragraph(ar("يتيح للمستخدم كتابة وتعديل أزواج العملات المستهدفة واختيار فريم الشموع (60s أو 300s) وتطبيقها فوراً."), table_cell_ar),
        ],
        [
            Paragraph(ar("4. شاشة السجلات الحية (Live Terminal)"), table_cell_bold_ar),
            Paragraph(ar("نافذة تعرض الأحداث اللحظية مثل نجاح المصادقة، نبضات الأمان، واسترجاع الشموع المفقودة بشكل فوري."), table_cell_ar),
        ],
        [
            Paragraph(ar("5. جدول تدقيق الشموع (Candles Table)"), table_cell_bold_ar),
            Paragraph(ar("يستعرض أحدث الشموع المحفوظة مع أسعار الافتتاح، القمة، القاع، الإغلاق، وحجم التداول مع زر تصدير CSV."), table_cell_ar),
        ],
    ]
    t_dash = Table(dash_parts, colWidths=[240, 480])
    t_dash.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_dash)
    story.append(PageBreak())

    # ═════════════════════════════════════════════════════════════════════════════
    # SLIDE 5: CONTROL BUTTONS
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(make_header(5, "أزرار التحكم والتشغيل اللحظي (Control Panel)"))
    story.append(Spacer(1, 14))

    ctrl_rows = [
        [Paragraph(ar("الزر الإجرائي"), table_header_ar), Paragraph(ar("الحالة والتأثير"), table_header_ar), Paragraph(ar("الإجراء البرمجي في الخلفية"), table_header_ar)],
        [
            Paragraph(ar("بدء التسجيل (Start)"), table_cell_bold_ar),
            Paragraph(ar("تفعيل المنظومة وبدء الحفظ"), table_cell_ar),
            Paragraph(ar("يقوم بتهيئة المحرك، فتح مقبس WebSocket المشفر، إرسال حزم التوثيق والاشتراك في جميع الأزواج المختارة، وإطلاق مهمة الاسترجاع التلقائي لأي شموع سابقة."), table_cell_ar),
        ],
        [
            Paragraph(ar("إيقاف مؤقت (Pause)"), table_cell_bold_ar),
            Paragraph(ar("تعليق استقبال الشموع مؤقتاً"), table_cell_ar),
            Paragraph(ar("يوقف حفظ الشموع في قاعدة البيانات دون قطع مقبس الاتصال مع السيرفر، مما يتيح التوقف السريع دون الحاجة لإعادة التوثيق والمصافحة."), table_cell_ar),
        ],
        [
            Paragraph(ar("استئناف (Resume)"), table_cell_bold_ar),
            Paragraph(ar("مواصلة التسجيل الفوري"), table_cell_ar),
            Paragraph(ar("يعيد تفعيل تدفق البيانات مباشرة دون أي تأخير، ويقوم بردم أي فارق زمني حدث أثناء فترة الإيقاف المؤقت."), table_cell_ar),
        ],
        [
            Paragraph(ar("إيقاف نهائي (Stop)"), table_cell_bold_ar),
            Paragraph(ar("إنهاء الجلسة وإغلاق الاتصال"), table_cell_ar),
            Paragraph(ar("يقوم بتسجيل خروج آمن، تفريغ الشموع المتبقية في الذاكرة إلى قاعدة البيانات، وإغلاق قنوات WebSocket مع إرسال إشعار للمشرف عبر التيليجرام."), table_cell_ar),
        ],
    ]
    t_ctrl = Table(ctrl_rows, colWidths=[150, 190, 380])
    t_ctrl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_emerald),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_ctrl)
    story.append(PageBreak())

    # ═════════════════════════════════════════════════════════════════════════════
    # SLIDE 6: LIVE TELEMETRY
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(make_header(6, "بطاقات القياس والمؤشرات اللحظية (Live Telemetry)"))
    story.append(Spacer(1, 14))

    hud_rows = [
        [Paragraph(ar("البطاقة القياسية"), table_header_ar), Paragraph(ar("القيمة المعروضة"), table_header_ar), Paragraph(ar("الأهمية للمتداول ونماذج الذكاء الاصطناعي"), table_header_ar)],
        [
            Paragraph(ar("حالة المحرك (Engine Status)"), table_cell_bold_ar),
            Paragraph(ar("RUNNING / PAUSED / STOPPED"), table_cell_ar),
            Paragraph(ar("توضح الوضع الحقيقي للمنظومة بلون تفاعلي (أخضر للتشغيل، أصفر للإيقاف المؤقت، أحمر للتوقف أو انقطاع الاتصال)."), table_cell_ar),
        ],
        [
            Paragraph(ar("إجمالي الشموع (Candles Total)"), table_cell_bold_ar),
            Paragraph(ar("مثلاً: 7,324 شمعة"), table_cell_ar),
            Paragraph(ar("العداد التراكمي للشموع المخزنة فعلياً في قاعدة البيانات، ويتم تحديثه لحظة بلحظة مع كل إغلاق شمعة جديدة."), table_cell_ar),
        ],
        [
            Paragraph(ar("سرعة السحب (Ingestion Rate)"), table_cell_bold_ar),
            Paragraph(ar("مثلاً: 240 شمعة / دقيقة"), table_cell_ar),
            Paragraph(ar("مقياس أداء لمعرفة حجم البيانات المجمعة في الدقيقة الواحدة عبر كافة أزواج العملات النشطة."), table_cell_ar),
        ],
        [
            Paragraph(ar("زمن الاستجابة (WebSocket Latency)"), table_cell_bold_ar),
            Paragraph(ar("مثلاً: 22ms"), table_cell_ar),
            Paragraph(ar("يقيس سرعة البينغ المباشر مع سيرفرات Pocket Option لضمان عدم وجود أي بطء أو عنق زجاجة في الإنترنت."), table_cell_ar),
        ],
        [
            Paragraph(ar("نوع قاعدة البيانات (Database Target)"), table_cell_bold_ar),
            Paragraph(ar("PostgreSQL (Neon Cloud)"), table_cell_ar),
            Paragraph(ar("يؤكد للمستخدم أن التخزين موصول بالسحابة المركزية مباشرة ومحمي من الفقدان في حال تعطل الجهاز المحلي."), table_cell_ar),
        ],
    ]
    t_hud = Table(hud_rows, colWidths=[180, 180, 360])
    t_hud.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_hud)
    story.append(PageBreak())

    # ═════════════════════════════════════════════════════════════════════════════
    # SLIDE 7: DYNAMIC CONFIG
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(make_header(7, "إدارة أزواج العملات والفريم الزمني ديناميكياً"))
    story.append(Spacer(1, 14))

    sym_intro = "تتميز المنظومة بمرونة كاملة تتيح للمستخدم ضبط الأصول والفريمات الزمنية دون الحاجة لتعديل الكود البرمجي، مع إمكانية تطبيق التعديلات فوراً على سيرفرات Pocket Option أثناء التشغيل."
    story.append(Paragraph(ar(sym_intro), body_ar))
    story.append(Spacer(1, 10))

    sym_rows = [
        [Paragraph(ar("الميزة"), table_header_ar), Paragraph(ar("طريقة العمل في لوحة التحكم"), table_header_ar), Paragraph(ar("سلوك قاعدة البيانات والبيانات السابقة"), table_header_ar)],
        [
            Paragraph(ar("تحديد أزواج العملات (Symbols List)"), table_cell_bold_ar),
            Paragraph(ar("حقل نصي يقبل أي عدد من الأزواج مفصولة بفاصلة مثل: EURUSD_otc, USDARS_otc, GBPUSD_otc, EURUSD."), table_cell_ar),
            Paragraph(ar("يقوم المحرك فوراً بإلغاء اشتراك الأزواج المحذوفة وبدء الاشتراك بالأزواج الجديدة واستدعاء تاريخها المفقود."), table_cell_ar),
        ],
        [
            Paragraph(ar("تغيير الفريم الزمني (Timeframe)"), table_cell_bold_ar),
            Paragraph(ar("حقل إدخال للثواني: 60 ثانية (فريم دقيقة M1) أو 300 ثانية (فريم 5 دقائق M5)."), table_cell_ar),
            Paragraph(ar("لا يتم مسح بيانات الفريم السابق أبداً! بفضل المفتاح المركب (symbol, timeframe, timestamp) تعيش شموع فريم الدقيقة وفريم 5 دقائق معاً في نفس الجدول."), table_cell_ar),
        ],
        [
            Paragraph(ar("تحديث الجلسة (Session Update)"), table_cell_bold_ar),
            Paragraph(ar("نافذة لتحديث كوكيز الجلسة وUID عند انتهاء صلاحيتها مع التحويل التلقائي بين الحساب التجريبي والحقيقي."), table_cell_ar),
            Paragraph(ar("عند إدخال رمز الجلسة الجديد، يعيد المحرك مصافحة السيرفر فوراً دون الحاجة لإعادة تشغيل خادم الويب."), table_cell_ar),
        ],
    ]
    t_sym = Table(sym_rows, colWidths=[180, 260, 280])
    t_sym.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_blue),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sym)
    story.append(PageBreak())

    # ═════════════════════════════════════════════════════════════════════════════
    # SLIDE 8: AUTOMATED GAP RECOVERY
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(make_header(8, "الاسترجاع التلقائي للفجوات الزمنية (Gap Recovery)"))
    story.append(Spacer(1, 14))

    gap_intro = "المطلب الأكثر أهمية لدى العميل: كيف يضمن النظام عدم وجود فجوات في حركة الشموع عند حدوث انقطاع في الإنترنت أو إعادة تشغيل الخادم؟ المنظومة مزودة بخوارزمية ذاتية التصحيح تعمل كما يلي:"
    story.append(Paragraph(ar(gap_intro), body_ar))
    story.append(Spacer(1, 10))

    gap_steps = [
        [Paragraph(ar("المرحلة"), table_header_ar), Paragraph(ar("الإجراء الذاتي للمحرك"), table_header_ar), Paragraph(ar("المخرجات والسرعة"), table_header_ar)],
        [
            Paragraph(ar("1. رصد الفارق الزمني (Gap Detection)"), table_cell_bold_ar),
            Paragraph(ar("عند الاتصال، يستعلم المحرك عن آخر شمعة مسجلة لكل زوج في قاعدة البيانات: MAX(timestamp). يحسب الفارق: gap = current_time - last_timestamp."), table_cell_ar),
            Paragraph(ar("يتم الحساب في 5 مللي ثانية فقط فور اكتمال المصافحة."), table_cell_ar),
        ],
        [
            Paragraph(ar("2. طلب التاريخ المفقود (History Fetch)"), table_cell_bold_ar),
            Paragraph(ar("إذا كان الفارق أكبر من فريم الشمعة (60s)، يرسل أمر loadHistoryPeriod محملاً بالإزاحة المطلوبة لجلب كل الشموع المفقودة بدقة."), table_cell_ar),
            Paragraph(ar("يستجيب سيرفر Pocket Option بحزم مضغوطة مسبقاً تضم حتى 1,440 شمعة (24 ساعة كاملة)."), table_cell_ar),
        ],
        [
            Paragraph(ar("3. الحفظ المانع للتكرار (Idempotent Insert)"), table_cell_bold_ar),
            Paragraph(ar("تُدرج جميع الشموع المفقودة في قاعدة البيانات باستخدام قاعدة ON CONFLICT DO NOTHING، بحيث لا يتكرر أي سجل حتى لو تداخلت مع البث اللحظي."), table_cell_ar),
            Paragraph(ar("تستغرق عملية استرجاع وحفظ يوم كامل أقل من 500 مللي ثانية لكل أصل!"), table_cell_ar),
        ],
    ]
    t_gap = Table(gap_steps, colWidths=[180, 360, 180])
    t_gap.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_emerald),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_gap)
    story.append(PageBreak())

    # ═════════════════════════════════════════════════════════════════════════════
    # SLIDE 9: LIVE TERMINAL & CSV EXPORT
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(make_header(9, "تيرمينال السجلات المباشر وتصدير البيانات"))
    story.append(Spacer(1, 14))

    term_rows = [
        [Paragraph(ar("المكون في لوحة الويب"), table_header_ar), Paragraph(ar("ما يراه العميل وكيفية الاستفادة منه"), table_header_ar)],
        [
            Paragraph(ar("تيرمينال السجلات الحي (Live Terminal)"), table_cell_bold_ar),
            [
                Paragraph(ar("• نافذة تفاعلية سوداء مدمجة في لوحة التحكم تعرض تدفق السجلات الحية فور وقوعها."), bullet_ar),
                Paragraph(ar("• يستقبل المتصفح الرسائل عبر مقبس ويب داخلي يعرض توقيت الرسالة ونوعها ومحتواها."), bullet_ar),
                Paragraph(ar("• يرى المشغل تأكيدات التوثيق، أسماء السيرفرات المتصلة، وتفاصيل عمليات ردم الفجوات اللحظية."), bullet_ar),
            ],
        ],
        [
            Paragraph(ar("جدول الشموع اللحظية (Verified Candles Audit)"), table_cell_bold_ar),
            [
                Paragraph(ar("• يعرض أحدث 15 إلى 50 شمعة مسجلة في قاعدة البيانات بصورة حية."), bullet_ar),
                Paragraph(ar("• يحتوي على الأعمدة الأساسية: الرمز، التوقيت، الافتتاح، القمة، القاع، الإغلاق، وحجم التداول."), bullet_ar),
                Paragraph(ar("• يتيح للمشغل التحقق البصري المباشر من تطابق الأسعار مع شاشة المنصة."), bullet_ar),
            ],
        ],
        [
            Paragraph(ar("تصدير البيانات بضغطة زر (One-Click CSV Export)"), table_cell_bold_ar),
            [
                Paragraph(ar("• زر مباشر في لوحة التحكم يقوم بتنزيل ملف CSV كامل لبيانات الشموع المخزنة."), bullet_ar),
                Paragraph(ar("• الملف مهيأ ومصفى مباشرة للاستخدام في مكتبات بايثون مثل Pandas وPyTorch وBacktrader."), bullet_ar),
                Paragraph(ar("• يمكن تصفية التصدير لزوج معين أو لكافة الأزواج المسجلة."), bullet_ar),
            ],
        ],
    ]
    t_term = Table(term_rows, colWidths=[240, 480])
    t_term.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_term)
    story.append(PageBreak())

    # ═════════════════════════════════════════════════════════════════════════════
    # SLIDE 10: TELEGRAM NOTIFICATIONS
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(make_header(10, "نظام تنبيهات تيليجرام التلقائي (Telegram Bot)"))
    story.append(Spacer(1, 14))

    tg_intro = "يتكامل المحرك مباشرة مع بوت تيليجرام خاص يرسل رسائل تنبيهية فورية لهاتف العميل بحيث يكون على اطلاع دائم بحالة التشغيل دون الحاجة للبقاء أمام شاشة الكمبيوتر."
    story.append(Paragraph(ar(tg_intro), body_ar))
    story.append(Spacer(1, 10))

    tg_cases = [
        [Paragraph(ar("الحدث"), table_header_ar), Paragraph(ar("شروط الإرسال"), table_header_ar), Paragraph(ar("نموذج الرسالة المستلمة على الهاتف"), table_header_ar)],
        [
            Paragraph(ar("بدء التشغيل (Started)"), table_cell_bold_ar),
            Paragraph(ar("عند الضغط على زر Start أو إعادة تشغيل الخادم"), table_cell_ar),
            Paragraph(ar("Pocket Option Harvester STARTED  -  Database: PostgreSQL (Neon)  -  Symbols: 4  -  Timeframe: 60s"), table_cell_ar),
        ],
        [
            Paragraph(ar("انقطاع الشبكة (Dropped)"), table_cell_bold_ar),
            Paragraph(ar("عند حدوث فصل غير متوقع في خط الإنترنت"), table_cell_ar),
            Paragraph(ar("Harvester Disconnected  -  Attempting reconnect #1 in 2.0s..."), table_cell_ar),
        ],
        [
            Paragraph(ar("استرجاع الفجوة (Recovered)"), table_cell_bold_ar),
            Paragraph(ar("فور نجاح ردم الشموع التي فقدت أثناء الانقطاع"), table_cell_ar),
            Paragraph(ar("Reconnected & Recovered  -  Symbol: USDARS_otc  -  Backfilled Candles: 180 bars"), table_cell_ar),
        ],
        [
            Paragraph(ar("تنبيه أمني (Auth Expired)"), table_cell_bold_ar),
            Paragraph(ar("عند انتهاء صلاحية كوكيز الجلسة في المنصة"), table_cell_ar),
            Paragraph(ar("Session Expired (41 Unauthorized)  -  Please update session token in Web Dashboard."), table_cell_ar),
        ],
    ]
    t_tg = Table(tg_cases, colWidths=[160, 240, 320])
    t_tg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_blue),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_tg)
    story.append(PageBreak())

    # ═════════════════════════════════════════════════════════════════════════════
    # SLIDE 11: VALUE-ADD ROADMAP
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(make_header(11, "ميزات إضافية مقترحة لإبهار العميل وتوسيع المنظومة"))
    story.append(Spacer(1, 14))

    roadmap_intro = "مجموعة من المقترحات التقنية الذكية التي يمكن إضافتها بسهولة لتعزيز القيمة الاستثمارية للنظام دون التأثير على البنية الأساسية:"
    story.append(Paragraph(ar(roadmap_intro), body_ar))
    story.append(Spacer(1, 8))

    rm_cards = [
        [Paragraph(ar("الميزة الإضافية المقترحة"), table_header_ar), Paragraph(ar("الفائدة التشغيلية للمتداول"), table_header_ar)],
        [
            Paragraph(ar("1. رسم بياني تفاعلي حي (TradingView Chart)"), table_cell_bold_ar),
            Paragraph(ar("دمج شارت تفاعلي بتقنية HTML5 Canvas في لوحة التحكم يعرض حركة الشموع الحية وتدرج الألوان مع إمكانية التكبير والتصغير والمقارنة البصرية الفورية مع منصة التداول."), table_cell_ar),
        ],
        [
            Paragraph(ar("2. مقياس اكتمال وجودة البيانات (Quality Scorecard)"), table_cell_bold_ar),
            Paragraph(ar("بطاقة إحصائية تعرض نسبة اكتمال البيانات المحفوظة (مثلاً 99.99%) وخلوها من أي فجوات مفقودة، مما يمنح العميل ثقة مطلقة عند استخدام البيانات في تدريب نماذج الذكاء الاصطناعي."), table_cell_ar),
        ],
        [
            Paragraph(ar("3. التقرير اليومي التلقائي عبر التيليجرام (Midnight Digest)"), table_cell_bold_ar),
            Paragraph(ar("رسالة يومية مجدولة في تمام الساعة 00:00 بتوقيت UTC تلخص إجمالي حجم الشموع المسجلة، أكثر الأزواج تذبذباً، نسبة استقرار الشبكة، وحجم نمو قاعدة البيانات السحابية."), table_cell_ar),
        ],
        [
            Paragraph(ar("4. مُجمّع الفريمات الافتراضية (Multi-Timeframe Resampler)"), table_cell_bold_ar),
            Paragraph(ar("خوارزمية ذكية تحول شموع فريم الدقيقة المحفوظة إلى فريمات أكبر (5 دقائق، 15 دقيقة، ساعة) تلقائياً داخل قاعدة البيانات دون الحاجة لفتح اتصالات إضافية مع المنصة."), table_cell_ar),
        ],
    ]
    t_rm = Table(rm_cards, colWidths=[240, 480])
    t_rm.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_rm)
    story.append(PageBreak())

    # ═════════════════════════════════════════════════════════════════════════════
    # SLIDE 12: QUESTIONS & CLIENT DISCUSSION
    # ═════════════════════════════════════════════════════════════════════════════
    story.append(make_header(12, "جلسة الأسئلة والنقاش واستقبال المقترحات"))
    story.append(Spacer(1, 20))

    q_title = ParagraphStyle("QTitle", fontName="ArabicBold", fontSize=18, leading=24, textColor=c_blue, alignment=1)
    story.append(Paragraph(ar("هل لديك أي أسئلة أو اقتراحات تفضل إضافتها للمنظومة؟"), q_title))
    story.append(Spacer(1, 15))

    q_cards = [
        [Paragraph(ar("محاور مقترحة للنقاش وتبادل الآراء مع العميل:"), ParagraphStyle("QH", fontName="ArabicBold", fontSize=11, leading=16, textColor=c_navy, alignment=2))],
        [Paragraph(ar("• أزواج وأصول إضافية: هل ترغب في تضمين أزواج عملات إضافية أو سلع (كالذهب والنفط) أو مؤشرات أسهم معينة؟"), body_ar)],
        [Paragraph(ar("• تنسيقات تصدير البيانات: ما هو الامتداد المفضل لنماذج الذكاء الاصطناعي لديك (ملفات CSV قياسية، ملفات Parquet سريعة، أو الوصول المباشر لقاعدة SQL)؟"), body_ar)],
        [Paragraph(ar("• تخصيص التنبيهات: هل ترغب في إضافة أعضاء إضافيين من فريقك إلى قناة تنبيهات التيليجرام أو تخصيص تنبيهات عند تخطي مستويات سعرية معينة؟"), body_ar)],
        [Paragraph(ar("• بيئة الاستضافة: جاهزية النظام للتشغيل الفوري سواء على جهازكم المحلي أو عبر خادم سحابي دائم (VPS / Cloud Server)."), body_ar)],
        [Paragraph(ar("نشكركم على اهتمامكم، وفريق التطوير جاهز لتنفيذ أي تخصيصات مطلوبة على الفور وبأعلى معايير الجودة."), ParagraphStyle("QC", fontName="ArabicBold", fontSize=10, leading=15, textColor=c_emerald, alignment=1))],
    ]
    t_q = Table(q_cards, colWidths=[700])
    t_q.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card),
        ('BOX', (0,0), (-1,-1), 1.5, c_blue),
        ('TOPPADDING', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 9),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_q)

    # Build PDF
    doc.build(story)
    file_size = os.path.getsize(output_pdf)
    print(f"[SUCCESS] Created presentation: {output_pdf} ({file_size} bytes, 12 slides)")

if __name__ == "__main__":
    create_presentation_pdf()
