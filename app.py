import io
import streamlit as st
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="Generátor zmluvy TRANSOCEANIC", page_icon="📄", layout="centered")

def generate_pdf(data):
    font_regular = "Helvetica"
    font_bold = "Helvetica-Bold"

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

    parties_table = Table(
        [[Paragraph(prikazca_text, party_style), Paragraph(prikaznik_text, party_style)]],
        colWidths=[260, 260]
    )
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
            "5.4 Splatnosť: Zúčtovacím obdobím je spravidla jeden kalendárny týždeň (pondelok až nedeľa). Odmena po odpočítaní 15 % provízie je splatná prevodom na bankový účet Príkazníka najneskôr do 5 (piatich) pracovných dní odo dňa doručenia zúčtovania a finančných prostriedkov od BOLT FOOD Príkazcovi.",
            "5.5 Príkazníkovi nevzniká nárok na odmenu za čas, počas ktorého nie je aktívny alebo nevykonáva konkrétny prijatý príkaz. Nemá garantovaný minimálny príjem ani minimálny počet objednávok.",
            "5.6 Odmena podľa tejto zmluvy predstavuje odmenu za vykonanie zákaziek a nie mzdu, plat ani odmenu za odpracovaný čas.",
            "5.7 Pokiaľ nie je písomne dohodnuté inak, vyplatená odmena zahŕňa všetky bežné náklady Príkazníka spojené s výkonom činnosti."
        ]),
        ("Článok VI. – Daňové a odvodové povinnosti", [
            "6.1 Príkazník berie na vedomie, že odmena podľa tejto zmluvy predstavuje príjem z činnosti vykonávanej na základe občianskoprávneho zmluvného vzťahu.",
            "6.2 Príkazník je povinný splniť svoje daňové a prípadné odvodové povinnosti vyplývajúce z platných právnych predpisov SR v závislosti od svojej daňovej a odvodovej rezidencie a právneho postavenia.",
            "6.3 Príkazník je povinný poskytnúť Príkazcovi bezodkladne všetku súčinnosť, doklady a pravdivé vyhlásenia potrebné na splnenie prípadných zákonných povinností.",
            "6.4 Ustanovenia tohto článku nemenia právnu povahu tejto zmluvy ani nezakladajú pracovnoprávny vzťah medzi zmluvnými stranami."
        ]),
        ("Článok VII. – Ochrana osobných údajov (GDPR)", [
            "7.1 Zmluvné strany sa zaväzujú postupovať v súlade s Nariadením GDPR a zákonom č. 18/2018 Z. z.",
            "7.2 Príkazník pri plnení príkazu prichádza do styku s osobnými údajmi zákazníkov a partnerov platformy. Zaväzuje sa ich spracúvať výlučne v nevyhnutnom rozsahu za účelom doručenia danej objednávky.",
            "7.3 Príkazník je povinný osobné údaje použiť len na splnenie príkazu, neposkytovať ich tretím stranám, nevytvárať databázy a po doručení ich ďalej neuchovávať.",
            "7.4 Príkazník plne zodpovedá za akúkoľvek škodu alebo pokuty uložené dozornými orgánmi v dôsledku jeho neoprávneného nakladania s osobnými údajmi."
        ]),
        ("Článok VIII. – Zodpovednosť za škodu a započítanie pohľadávok", [
            "8.1 Príkazník zodpovedá za škodu spôsobenú zavineným porušením svojich povinností vyplývajúcich z tejto zmluvy, pravidiel platformy alebo právnych predpisov.",
            "8.2 Príkazník zodpovedá za škodu na tovare a škody na majetku tretích osôb spôsobené prevádzkou svojho dopravného prostriedku.",
            "8.3 Príkazca nezodpovedá za úraz ani škodu vzniknutú pri výkone činnosti Príkazníka.",
            "8.4 Príkazník je povinný bezodkladne oznámiť každú škodovú udalosť, nehodu alebo poškodenie tovaru.",
            "8.5 Jednostranné započítanie: Príkazník výslovne a neodvolateľne udeľuje Príkazcovi súhlas na jednostranné započítanie finančnej škody, strhnutých platieb, sankcií platformy z dôvodu zavinenia Príkazníka a neuhradených záväzkov priamo voči odmene Príkazníka."
        ]),
        ("Článok IX. – Pravidlá digitálnej pracovnej platformy", [
            "9.1 Výkon platformovej práce je technicky zabezpečovaný prostredníctvom digitálnej platformy BOLT FOOD.",
            "9.2 Príkazník sa zaväzuje dodržiavať obchodné podmienky, zásady používania aplikácie a kódex správania kuriéra BOLT FOOD.",
            "9.3 Príkazca nie je oprávnený meniť pravidlá platformy ani určovať pracovný čas. Algoritmické prideľovanie sa nepovažuje za pokyn Príkazcu.",
            "9.4 Prístup k aplikácii môže podliehať technickým a bezpečnostným podmienkam platformy."
        ]),
        ("Článok X. – Doba trvania a ukončenie zmluvy", [
            "10.1 Táto zmluva nadobúda platnosť a účinnosť dňom podpisu oboma zmluvnými stranami.",
            "10.2 Zmluva sa uzatvára na dobu určitú do 31. 12. 2026, pokiaľ sa zmluvné strany nedohodnú inak.",
            "10.3 Výpovedná lehota je 15 (pätnásť) kalendárnych dní a začína plynúť dňom nasledujúcim po doručení písomnej výpovede (aj e-mailom).",
            "10.4 Zmluvné strany môžu zmluvu ukončiť kedykoľvek dohodou.",
            "10.5 Príkazca môže od zmluvy odstúpiť okamžite pri zablokovaní profilu kuriéra zo strany BOLT FOOD, závažnom porušení predpisov alebo poškodení dobrého mena.",
            "10.6 Zánikom zmluvy nie sú dotknuté vzájomné finančné nároky vzniknuté pred jej zánikom."
        ]),
        ("Článok XI. – Osobitné ustanovenia o samostatnom charaktere činnosti", [
            "11.1 Príkazník vykonáva činnosť samostatne a na vlastné podnikateľské alebo ekonomické riziko.",
            "11.2 Príkazník si sám organizuje činnosť, Príkazca neurčuje pracovné zmeny, čas ani trasovanie.",
            "11.3 Príkazník nemá nárok na minimálny počet objednávok ani minimálny príjem.",
            "11.4 Príkazník nevystupuje vo vzťahu k tretím stranám ako zamestnanec Príkazcu.",
            "11.5 Príkazník je oprávnený vykonávať inú zárobkovú činnosť bez obmedzenia.",
            "11.6 Pre právne posúdenie vzťahu je rozhodujúci skutočný výkon platformovej práce."
        ]),
        ("Článok XII. – Záverečné ustanovenia", [
            "12.1 Právne vzťahy neupravené touto zmluvou sa spravujú Občianskym zákonníkom SR.",
            "12.2 Zmeny a doplnenia je možné vykonať len vo forme písomných dodatkov.",
            "12.3 Neplatnosť jednotlivého ustanovenia nemá vplyv na platnosť ostatných ustanovení.",
            "12.4 Zmluvné strany zmluvu pred podpisom prečítali a na znak súhlasu ju slobodne podpisujú.",
            "12.5 Zmluva je vyhotovená v dvoch rovnopisoch. Za rovnopis sa považuje aj elektronické vyhotovenie."
        ])
    ]

    for title, pars in articles:
        story.append(Paragraph(title, heading_style))
        for p in pars:
            story.append(Paragraph(p, body_style))

    story.append(Spacer(1, 8))
    datum_podpisu = data.get("datum_podpisu") or datetime.now().strftime("%d. %m. %Y")
    story.append(Paragraph(f"V Trnave, dňa {datum_podpisu}", body_style))
    story.append(Spacer(1, 8))

    podpisy_table = Table(
        [
            [
                Paragraph("<b>Príkazca:</b><br/>TRANSOCEANIC s. r. o.<br/><br/><br/>____________________________________<br/>Denis Beňa – konateľ", party_style),
                Paragraph(f"<b>Príkazník:</b><br/>{data['meno']}<br/><br/><br/>____________________________________<br/>{data['meno']}", party_style)
            ]
        ],
        colWidths=[260, 260]
    )
    podpisy_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(KeepTogether(podpisy_table))

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer

st.title("📄 Generátor Príkaznej zmluvy")
st.caption("TRANSOCEANIC s. r. o. / BOLT FOOD")

with st.form("contract_form"):
    st.subheader("Údaje kuriéra (Príkazníka)")
    meno = st.text_input("Meno a priezvisko *", placeholder="napr. Ján Novák")
    
    col1, col2 = st.columns(2)
    with col1:
        datum_narodenia = st.text_input("Dátum narodenia *", placeholder="DD. MM. RRRR")
    with col2:
        rc = st.text_input("Rodné číslo (voliteľné)", placeholder="napr. 950515/1234")

    bydlisko = st.text_input("Trvalé bydlisko (Ulica, PSČ, Mesto) *", placeholder="napr. Hlavná 12, 917 01 Trnava")

    col3, col4 = st.columns(2)
    with col3:
        telefon = st.text_input("Telefónne číslo *", placeholder="+421 900 000 000")
    with col4:
        email = st.text_input("E-mail *", placeholder="kurier@email.sk")

    col5, col6 = st.columns(2)
    with col5:
        iban = st.text_input("IBAN (Číslo účtu) *", placeholder="SK00 0000 0000 0000 0000 0000")
    with col6:
        ico = st.text_input("IČO / DIČ (ak existuje)", placeholder="napr. 12345678")

    datum_dnes = datetime.now().strftime("%d. %m. %Y")
    datum_podpisu = st.text_input("Dátum podpisu zmluvy", value=datum_dnes)

    submitted = st.form_submit_button("🚀 Vygenerovať PDF zmluvu", use_container_width=True)

if submitted:
    if not (meno and datum_narodenia and bydlisko and telefon and email and iban):
        st.error("⚠️ Prosím, vyplňte všetky povinné polia označené hviezdičkou (*).")
    else:
        data = {
            "meno": meno,
            "datum_narodenia": datum_narodenia,
            "rc": rc,
            "bydlisko": bydlisko,
            "telefon": telefon,
            "email": email,
            "iban": iban,
            "ico": ico,
            "datum_podpisu": datum_podpisu
        }
        
        pdf_bytes = generate_pdf(data)
        safe_name = meno.strip().replace(" ", "_")
        subor_nazov = f"Prikazna_zmluva_{safe_name}.pdf"

        st.success(f"✅ Zmluva pre kuriéra **{meno}** je pripravená!")
        st.download_button(
            label="📥 Stiahnuť vygenerovanú PDF zmluvu",
            data=pdf_bytes,
            file_name=subor_nazov,
            mime="application/pdf",
            use_container_width=True
        )
