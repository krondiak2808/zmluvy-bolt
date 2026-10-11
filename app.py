import io
import os
import json
import base64
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime

import streamlit as st
import numpy as np
from PIL import Image, ImageDraw

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Zmluvy TRANSOCEANIC", page_icon="📄", layout="centered")

@st.cache_resource
def setup_fonts():
    linux_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    linux_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    mac_reg = "/System/Library/Fonts/Supplemental/Arial.ttf"
    mac_bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

    if os.path.exists(linux_reg) and os.path.exists(linux_bold):
        pdfmetrics.registerFont(TTFont("CustomFont", linux_reg))
        pdfmetrics.registerFont(TTFont("CustomFont-Bold", linux_bold))
        return "CustomFont", "CustomFont-Bold"
    elif os.path.exists(mac_reg) and os.path.exists(mac_bold):
        pdfmetrics.registerFont(TTFont("CustomFont", mac_reg))
        pdfmetrics.registerFont(TTFont("CustomFont-Bold", mac_bold))
        return "CustomFont", "CustomFont-Bold"
    else:
        return "Helvetica", "Helvetica-Bold"

def get_valid_stamp_image():
    candidates = [
        "peciatka.png", "peciatka.PNG", "peciatka.jpg", 
        "peciatka.jpeg", "pečiatka.png", "podpis.png"
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with Image.open(path) as img:
                    img.verify()
                with Image.open(path) as img:
                    img_bytes = io.BytesIO()
                    img.convert("RGBA").save(img_bytes, format="PNG")
                    img_bytes.seek(0)
                    return img_bytes
            except Exception:
                continue
    return None

def extract_signature_image(canvas_result, width=340, height=140):
    if canvas_result is None:
        return None

    if canvas_result.json_data and "objects" in canvas_result.json_data:
        objects = canvas_result.json_data["objects"]
        if len(objects) > 0:
            img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            has_strokes = False

            for obj in objects:
                path = obj.get("path", [])
                points = []
                for cmd in path:
                    if len(cmd) >= 3 and cmd[0] == "M":
                        if len(points) > 1:
                            draw.line(points, fill=(0, 0, 0, 255), width=3, joint="curve")
                        points = [(cmd[1], cmd[2])]
                    elif len(cmd) >= 5 and cmd[0] == "Q":
                        points.append((cmd[3], cmd[4]))
                    elif len(cmd) >= 3 and cmd[0] == "L":
                        points.append((cmd[1], cmd[2]))

                if len(points) > 1:
                    draw.line(points, fill=(0, 0, 0, 255), width=3, joint="curve")
                    has_strokes = True
                elif len(points) == 1:
                    x, y = points[0]
                    draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(0, 0, 0, 255))
                    has_strokes = True

            if has_strokes:
                return img

    if getattr(canvas_result, "raw_image_data", None) is not None:
        try:
            raw_rgba = canvas_result.image_data.astype('uint8')
            pil_image = Image.fromarray(raw_rgba, 'RGBA')
            datas = pil_image.getdata()
            new_data = []
            has_pixels = False
            for item in datas:
                if item[0] < 120 and item[1] < 120 and item[2] < 120 and item[3] > 50:
                    new_data.append((0, 0, 0, 255))
                    has_pixels = True
                else:
                    new_data.append((255, 255, 255, 0))
            if has_pixels:
                pil_image.putdata(new_data)
                return pil_image
        except Exception:
            pass

    return None

def send_signed_pdf_email(pdf_bytes, kurier_data, file_name):
    if "email" not in st.secrets:
        return False, "E-mailové nastavenia (secrets) nie sú zadané."

    try:
        cfg = st.secrets["email"]
        smtp_server = cfg.get("smtp_server", "smtp.websupport.sk").strip()
        sender_email = cfg["sender_email"].strip()
        sender_password = cfg["sender_password"].strip()
        receiver_email = cfg.get("receiver_email", sender_email).strip()

        msg = MIMEMultipart()
        msg["From"] = f"Zmluvy TRANSOCEANIC <{sender_email}>"
        msg["To"] = receiver_email
        msg["Subject"] = f"✅ Podpísaná zmluva – {kurier_data['meno']}"

        body = f"""Dobrý deň,

kuriér úspešne podpísal Príkaznú zmluvu cez mobilný odkaz.

Údaje kuriéra:
- Meno a priezvisko: {kurier_data['meno']}
- Dátum narodenia: {kurier_data['datum_narodenia']}
- Bydlisko: {kurier_data['bydlisko']}
- Telefón: {kurier_data['telefon']}
- E-mail: {kurier_data['email']}
- IBAN: {kurier_data['iban']}

V prílohe nájdete hotovú obojstranne podpísanú zmluvu vo formáte PDF.
"""
        msg.attach(MIMEText(body, "plain", "utf-8"))

        part = MIMEBase("application", "pdf")
        pdf_bytes.seek(0)
        part.set_payload(pdf_bytes.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{file_name}"')
        msg.attach(part)

        try:
            with smtplib.SMTP(smtp_server, 587, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, [receiver_email], msg.as_string())
                return True, "E-mail bol úspešne odoslaný."
        except Exception as e587:
            try:
                with smtplib.SMTP_SSL(smtp_server, 465, timeout=15) as server:
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, [receiver_email], msg.as_string())
                    return True, "E-mail bol úspešne odoslaný."
            except Exception:
                raise e587

    except Exception as e:
        return False, str(e)

def send_link_to_courier_email(kurier_email, kurier_meno, link):
    if "email" not in st.secrets:
        return False, "E-mailové nastavenia (secrets) nie sú zadané."

    try:
        cfg = st.secrets["email"]
        smtp_server = cfg.get("smtp_server", "smtp.websupport.sk").strip()
        sender_email = cfg["sender_email"].strip()
        sender_password = cfg["sender_password"].strip()

        msg = MIMEMultipart()
        msg["From"] = f"TRANSOCEANIC s. r. o. <{sender_email}>"
        msg["To"] = kurier_email.strip()
        msg["Subject"] = "Príkazná zmluva na podpis – TRANSOCEANIC s. r. o."

        body = f"""Dobrý deň {kurier_meno},

posielame Vám na podpis Príkaznú zmluvu o výkone platformovej práce so spoločnosťou TRANSOCEANIC s. r. o.

Zmluvu si môžete otvoriť priamo na Vašom mobilnom telefóne, skontrolovať údaje a podpísať prstom na displeji kliknutím na tento odkaz:
{link}

Po podpísaní zmluvy si budete môcť hotový dokument ihneď stiahnuť a jeho kópia sa automaticky odošle do kancelárie.

S pozdravom,
TRANSOCEANIC s. r. o.
flotila@transoceanic.sk
"""
        msg.attach(MIMEText(body, "plain", "utf-8"))

        try:
            with smtplib.SMTP(smtp_server, 587, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, [kurier_email.strip()], msg.as_string())
                return True, "E-mail s odkazom bol kuriérovi odoslaný."
        except Exception as e587:
            try:
                with smtplib.SMTP_SSL(smtp_server, 465, timeout=15) as server:
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, [kurier_email.strip()], msg.as_string())
                    return True, "E-mail s odkazom bol kuriérovi odoslaný."
            except Exception:
                raise e587

    except Exception as e:
        return False, str(e)

def generate_pdf(data, signature_image=None):
    font_regular, font_bold = setup_fonts()
    pdf_buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName=font_bold, fontSize=11, leading=14, alignment=1, spaceAfter=3)
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontName=font_regular, fontSize=8.5, leading=11, alignment=1, spaceAfter=10)
    heading_style = ParagraphStyle('SectionHeading', parent=styles['Normal'], fontName=font_bold, fontSize=9, leading=12, spaceBefore=7, spaceAfter=2)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName=font_regular, fontSize=8, leading=10.8, alignment=4, spaceAfter=2.5)
    party_style = ParagraphStyle('PartyText', parent=styles['Normal'], fontName=font_regular, fontSize=8, leading=10.8)

    story = []

    story.append(Paragraph("PRÍKAZNÁ ZMLUVA O VÝKONE PLATFORMOVEJ PRÁCE", title_style))
    story.append(Paragraph("uzatvorená podľa § 724 a nasl. zákona č. 40/1964 Zb. Občiansky zákonník v znení neskorších predpisov", subtitle_style))
    story.append(Paragraph("Článok I. – Zmluvné strany", heading_style))

    prikazca_text = """<b>Príkazca:</b><br/>
Obchodná firma: TRANSOCEANIC s. r. o.<br/>
Sídlo: Ulica Jozefa Adamca 9983/24, 917 01 Trnava<br/>
IČO: 55 569 790<br/>
DIČ: 2122027336<br/>
IČ DPH: SK2122027336<br/>
Zápis: OR Okresného súdu Trnava, oddiel: Sro, vložka č. 54512/T<br/>
Zastúpený: Denis Beňa – konateľ<br/>
IBAN: SK24 1100 0000 0029 4915 2085<br/>
<i>(ďalej len „Príkazca“)</i>
"""
    rc_text = f"<br/>Rodné číslo: {data['rc']}" if data.get('rc') else ""
    ico_text = f"<br/>IČO / DIČ: {data['ico']}" if data.get('ico') else ""

    prikaznik_text = f"""<b>Príkazník:</b><br/>
Meno a priezvisko: <b>{data['meno']}</b><br/>
Dátum narodenia: {data['datum_narodenia']}{rc_text}<br/>
Bydlisko: {data['bydlisko']}<br/>
Telefón: {data['telefon']}<br/>
E-mail: {data['email']}<br/>
IBAN: <b>{data['iban']}</b>{ico_text}<br/>
<i>(ďalej len „Príkazník“)</i>
"""

    parties_table = Table([[Paragraph(prikazca_text, party_style), Paragraph(prikaznik_text, party_style)]], colWidths=[260, 260])
    parties_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LINEBEFORE', (1,0), (1,-1), 0.5, colors.lightgrey),
    ]))
    story.append(parties_table)
    story.append(Spacer(1, 3))
    story.append(Paragraph("Príkazca a Príkazník ďalej spoločne len „zmluvné strany“ alebo jednotlivo „zmluvná strana“.", body_style))

    articles = [
        ("Článok II. – Predmet zmluvy", [
            "2.1 Príkazca týmto udeľuje Príkazníkovi príkaz spočívajúci v zabezpečovaní a vykonávaní jednotlivých prepravných a doručovacích činností, najmä doručovania jedál, nápojov, potravín a iného tovaru prostredníctvom digitálnej pracovnej platformy BOLT FOOD, prípadne prostredníctvom inej digitálnej pracovnej platformy, ak s tým Príkazník súhlasí.",
            "2.2 Príkazník tento príkaz prijíma a zaväzuje sa jednotlivé prijaté objednávky vykonať riadne, včas a s odbornou starostlivosťou, pričom pri ich vykonávaní rešpektuje pravidlá príslušnej digitálnej pracovnej platformy, platné právne predpisy a bezpečnostné a hygienické požiadavky.",
            "2.3 Zmluvné strany výslovne berú na vedomie, že predmetom tejto zmluvy nie je záväzok Príkazníka vykonávať činnosť v určitom pracovnom čase, v určitých pracovných zmenách alebo v minimálnom rozsahu.",
            "2.4 Príkazník sa samostatne rozhoduje: a) či bude platformovú prácu v konkrétny deň vykonávať, b) kedy začne a kedy ukončí svoju činnosť, c) v akom rozsahu bude činnosť vykonávať, d) či bude v danom čase dostupný prostredníctvom platformy, e) či prijme alebo odmietne konkrétny príkaz alebo objednávku, ak mu pravidlá príslušnej platformy umožňujú jej odmietnutie.",
            "2.5 Príkazca neurčuje Príkazníkovi pracovný čas, pracovné zmeny, povinný počet hodín ani minimálny počet objednávok, pokiaľ takáto podmienka nevyplýva priamo z pravidiel digitálnej pracovnej platformy, s ktorými Príkazník súhlasil.",
            "2.6 Príkazník nie je povinný byť počas trvania tejto zmluvy nepretržite dostupný, aktívny alebo prihlásený do platformy a z neúčasti na výkone platformovej práce mu nevzniká povinnosť požiadať Príkazcu o dovolenku, voľno alebo inú obdobnú formu súhlasu.",
            "2.7 Príkazník vykonáva činnosť samostatne, vo vlastnom mene a na vlastnú zodpovednosť, v rozsahu a za podmienok dohodnutých touto zmluvou a pravidlami príslušnej digitálnej pracovnej platformy.",
            "2.8 Zmluvné strany berú na vedomie, že táto zmluva je uzatvorená ako občianskoprávny vzťah podľa Občianskeho zákonníka a jej účelom nie je zakrytie pracovnoprávneho vzťahu. Právne posúdenie povahy zmluvného vzťahu sa riadi jeho skutočným obsahom a spôsobom výkonu činnosti."
        ]),
        ("Článok III. – Samostatnosť Príkazníka a spôsob výkonu činnosti", [
            "3.1 Príkazník pri vykonávaní jednotlivých príkazov postupuje samostatne a zodpovedá za spôsob ich vykonania v rozsahu, v akom mu tento spôsob umožňujú pravidlá príslušnej digitálnej pracovnej platformy a právne predpisy.",
            "3.2 Príkazca nie je oprávnený určovať Príkazníkovi pracovný čas, miesto začatia alebo ukončenia činnosti, počet odpracovaných hodín ani počet dní, počas ktorých má Príkazník činnosť vykonávať.",
            "3.3 Príkazca poskytuje Príkazníkovi najmä: a) prístup k príslušnej platforme alebo systému (vytvorenie alebo zaradenie profilu kuriéra pod flotilu), b) informácie potrebné na vykonanie konkrétneho príkazu a údaje potrebné na doručenie objednávky, c) informácie o pravidlách a prevádzkových podmienkach platformy, d) administratívnu, zúčtovaciu a technickú podporu.",
            "3.4 Pokyny poskytnuté Príkazcom sa môžu týkať výlučne konkrétneho predmetu príkazu, bezpečnosti, ochrany tovaru, ochrany osobných údajov, právnych predpisov alebo technického fungovania platformy. Takéto pokyny nemožno vykladať ako určovanie pracovného času alebo organizovanie práce spôsobom typickým pre pracovnoprávny vzťah.",
            "3.5 Príkazník si samostatne zabezpečuje dopravný prostriedok, telefón, dátové pripojenie, ochranné vybavenie a ďalšie prostriedky potrebné na vykonávanie činnosti, pokiaľ sa zmluvné strany výslovne nedohodnú inak.",
            "3.6 Náklady súvisiace s výkonom činnosti znáša v plnom rozsahu Príkazník, pričom tieto náklady sú zohľadnené v jeho dohodnutej odmene podľa tejto zmluvy.",
            "3.7 Príkazník nie je povinný vykonávať činnosť výlučne pre Príkazcu a môže vykonávať inú zárobkovú činnosť alebo spolupracovať s inými osobami a platformami, pokiaľ tým neporuší právne predpisy, pravidlá príslušnej digitálnej platformy alebo povinnosť mlčanlivosti.",
            "3.8 Príkazník nie je povinný prijímať ďalšie príkazy nad rámec konkrétnych príkazov, ktoré slobodne prijal.",
            "3.9 Ak pravidlá príslušnej digitálnej platformy umožňujú poverenie tretej osoby alebo substitúciu, Príkazník je oprávnený zabezpečiť vykonanie príkazu prostredníctvom tretej osoby za podmienok ustanovených platformou a právnymi predpismi."
        ]),
        ("Článok IV. – Práva a povinnosti Príkazníka", [
            "4.1 Príkazník je povinný: a) vykonávať prijaté príkazy riadne, včas a s odbornou starostlivosťou, b) dodržiavať právne predpisy vzťahujúce sa na vykonávanú činnosť a pravidlá cestnej premávky, c) chrániť zverený tovar až do jeho úspešného doručenia zákazníkovi, d) dodržiavať hygienické a bezpečnostné požiadavky pri manipulácii s potravinami a nápojmi (vrátane používania predpísanej termotašky), e) používať dopravný prostriedok a vybavenie v riadnom technickom stave, f) bezodkladne oznámiť Príkazcovi skutočnosti brániace riadnemu vykonaniu príkazu, g) zachovávať mlčanlivosť, h) dôsledne chrániť osobné údaje zákazníkov a tretích osôb v súlade s Článkom VII.",
            "4.2 Príkazník zodpovedá za to, že počas výkonu činnosti disponuje všetkými potrebnými oprávneniami (napr. vodičský preukaz, zdravotný preukaz, ak sa vyžaduje).",
            "4.3 Príkazník je povinný bezodkladne informovať Príkazcu o strate, poškodení alebo obmedzení prístupu k platformovému účtu BOLT FOOD.",
            "4.4 Príkazník nie je povinný plniť pokyn v rozpore s právnym predpisom, pravidlami bezpečnosti alebo podmienkami platformy."
        ]),
        ("Článok V. – Odmena, provízia Príkazcu a platobné podmienky", [
            "5.1 Príkazníkovi patrí odmena za riadne vykonané jednotlivé príkazy a doručené objednávky. Výška hrubej odmeny sa určuje podľa skutočne realizovaných objednávok evidovaných platformou BOLT FOOD podľa jej aktuálne platného sadzobníka.",
            "5.2 Výška provízie: Za registráciu, sprostredkovanie prístupu k platforme BOLT FOOD, technickú, prevádzkovú a zúčtovaciu podporu patrí Príkazcovi provízia (servisný poplatok) vo výške 15 % (slovom: pätnásť percent) z celkového zárobku (hrubého obratu) vygenerovaného Príkazníkom na platforme za príslušné zúčtovacie obdobie.",
            "5.3 Výpočet odmeny: Konečná odmena vyplácaná Príkazníkovi predstavuje celkový zárobok vygenerovaný Príkazníkom evidovaný platformou BOLT FOOD, znížený o dohodnutú províziu Príkazcu vo výške 15 % a prípadné oprávnené zápočty škôd alebo zrážok.",
            "5.4 Splatnosť: Zúčtovacím obdobím je spravidla jeden kalendárny týždeň (pondelok až nedeľa). Odmena po odpočítaní 15
