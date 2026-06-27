import os
import sys
from fpdf import FPDF
from fpdf.enums import XPos, YPos


class FeasibilityReport(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.in_cover = True

    def header(self):
        if self.page_no() == 1:
            return
        
        # Navy blue banner at the top
        self.set_fill_color(27, 54, 93)  # Navy Blue #1B365D
        self.rect(0, 0, 210, 16, "F")
        
        # Title in the banner
        self.set_text_color(255, 255, 255)
        self.set_font("helvetica", "B", 10)
        self.set_xy(15, 4)
        self.cell(0, 8, "INDIA ENGINEERING EXPORT FEASIBILITY REPORT", align="L")
        
        # Subtitle / Date on the right
        self.set_font("helvetica", "", 8)
        self.set_xy(-65, 4)
        self.cell(50, 8, "FY 2024-2025 Study", align="R")
        
        # Draw a thin grey separator line below banner
        self.set_fill_color(74, 144, 226) # Accent Blue
        self.rect(0, 16, 210, 1, "F")
        
        # Set Y cursor below the header
        self.set_y(25)

    def footer(self):
        if self.page_no() == 1:
            return
            
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        
        # Draw a thin grey line above the footer
        self.set_draw_color(220, 220, 220)
        self.line(15, 282, 195, 282)
        
        # Footer text: Left side confidential, Right side Page X of Y
        self.set_x(15)
        self.cell(90, 10, "Confidential - India Engineering Export Study", align="L")
        
        self.set_x(-105)
        self.cell(90, 10, f"Page {self.page_no()}/{{nb}}", align="R")

def section_header(pdf, title):
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(27, 54, 93) # Navy blue
    x, y = pdf.get_x(), pdf.get_y()
    pdf.set_fill_color(27, 54, 93)
    pdf.rect(x, y + 1.5, 3.5, 5, "F")
    pdf.set_xy(x + 7, y)
    if title.startswith("###"):
        pdf.set_text_color(255, 255, 255)
        pdf.write(7, "### ")
        pdf.set_text_color(27, 54, 93)
        clean_title = title.replace("###", "").strip()
        pdf.cell(0, 7, clean_title, new_x="LMARGIN", new_y="NEXT")
    elif title.startswith("##"):
        pdf.set_text_color(255, 255, 255)
        pdf.write(7, "## ")
        pdf.set_text_color(27, 54, 93)
        clean_title = title.replace("##", "").strip()
        pdf.cell(0, 7, clean_title, new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    # Draw a thin grey separator line below section title
    pdf.set_draw_color(230, 230, 230)
    pdf.set_line_width(0.3)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)

def write_profile(pdf, title, origin, markets, demand, sectors, companies):
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(27, 54, 93)
    pdf.cell(0, 6, f"Profile: {title}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    
    pdf.set_font("helvetica", "", 9.5)
    pdf.set_text_color(51, 51, 51)
    
    # Sourcing Origin
    pdf.set_font("helvetica", "B", 9.5)
    pdf.write(5, "Sourcing Origin: ")
    pdf.set_font("helvetica", "", 9.5)
    pdf.write(5, origin + "\n")
    
    # Target Export Ports & Markets
    pdf.set_font("helvetica", "B", 9.5)
    pdf.write(5, "Target Export Ports and Markets: ")
    pdf.set_font("helvetica", "", 9.5)
    pdf.write(5, markets + "\n")
    
    # Demand Statistics
    pdf.set_font("helvetica", "B", 9.5)
    pdf.write(5, "Demand Statistics: ")
    pdf.set_font("helvetica", "", 9.5)
    pdf.write(5, demand + "\n")
    
    # Target Sectors
    pdf.set_font("helvetica", "B", 9.5)
    pdf.write(5, "Target Sectors: ")
    pdf.set_font("helvetica", "", 9.5)
    pdf.write(5, sectors + "\n")
    
    # Active Indian Companies
    pdf.set_font("helvetica", "B", 9.5)
    pdf.write(5, "Active Indian Companies:\n")
    pdf.set_font("helvetica", "", 9.5)
    for name, desc in companies:
        pdf.write(5, f"- {name}: ")
        pdf.write(5, desc + "\n")
    pdf.ln(3)

def main():
    pdf = FeasibilityReport()
    pdf.alias_nb_pages()
    pdf.set_margins(15, 25, 15)
    pdf.set_auto_page_break(True, margin=20)

    # ------------------ PAGE 1: COVER PAGE ------------------
    pdf.add_page()
    pdf.set_fill_color(27, 54, 93) # Navy blue
    pdf.rect(0, 0, 210, 120, "F") # Cover top half

    # Golden/Accent separator line
    pdf.set_fill_color(74, 144, 226) # Accent blue
    pdf.rect(0, 120, 210, 4, "F")

    # Title inside navy blue area
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 22)
    pdf.set_xy(15, 35)
    pdf.multi_cell(180, 12, "INDIA ENGINEERING EXPORT\nFEASIBILITY STUDY")

    # Subtitle
    pdf.set_font("helvetica", "", 11)
    pdf.set_xy(15, 65)
    pdf.multi_cell(180, 6, "A Strategic Assessment of Engineering Product Exports to Australia, Europe, New Zealand, and China under Active FTAs & Regulatory Regimes")

    # Metadata in cover page (white area)
    pdf.set_text_color(51, 51, 51)
    pdf.set_font("helvetica", "B", 13)
    pdf.set_xy(15, 145)
    pdf.cell(0, 8, "PREPARED BY:")
    pdf.set_font("helvetica", "", 11)
    pdf.set_xy(15, 153)
    pdf.cell(0, 6, "Market Research & Export Strategy Division")

    pdf.set_font("helvetica", "B", 13)
    pdf.set_xy(15, 175)
    pdf.cell(0, 8, "FOCUS MARKETS:")
    pdf.set_font("helvetica", "", 11)
    pdf.set_xy(15, 183)
    pdf.cell(0, 6, "Australia (AI-ECTA), Europe (CBAM), New Zealand, China")

    pdf.set_font("helvetica", "B", 13)
    pdf.set_xy(15, 205)
    pdf.cell(0, 8, "DATE OF ISSUE:")
    pdf.set_font("helvetica", "", 11)
    pdf.set_xy(15, 213)
    pdf.cell(0, 6, "June 2026")

    pdf.set_font("helvetica", "B", 13)
    pdf.set_xy(15, 235)
    pdf.cell(0, 8, "DOCUMENT STATUS:")
    pdf.set_font("helvetica", "", 11)
    pdf.set_xy(15, 243)
    pdf.cell(0, 6, "Final Feasibility Report (Milestone 3)")

    # ------------------ PAGE 2: EXEC SUMMARY & SCORING MATRIX ------------------
    pdf.in_cover = False
    pdf.add_page()

    section_header(pdf, "### 1. Executive Summary")
    exec_summary_text = (
        "This feasibility study analyzes the export potential of Indian engineering products to target markets including Australia, "
        "Europe, New Zealand, and China. In response to global supply chain diversification strategies ('China+1'), Indian engineering "
        "exporters are presented with significant trade opportunities. These prospects are further enhanced by the implementation "
        "of active trade agreements, such as the Australia-India Economic Cooperation and Trade Agreement (AI-ECTA), which offers zero-tariff access. "
        "This study evaluates ten candidate products across four core feasibility criteria. The top three highest-rated products - Centrifugal "
        "Pumps, Industrial Valves, and Automotive Parts - have been selected for detailed profiling. The remaining seven candidate products "
        "are rejected due to carbon adjustment mechanisms (CBAM), compliance barriers, high logistics costs, or raw material import dependencies."
    )
    pdf.set_font("helvetica", "", 9.5)
    pdf.set_text_color(51, 51, 51)
    pdf.multi_cell(180, 4.5, exec_summary_text)
    pdf.ln(3)

    section_header(pdf, "### 2. Feasibility Scoring Matrix")
    pdf.set_font("helvetica", "", 9.5)
    pdf.cell(0, 5, "Feasibility scoring matrix comparing ten candidate products based on four criteria:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    # Let's draw the grey box and print the Courier text table inside it
    y_start = pdf.get_y()
    pdf.set_fill_color(248, 249, 250)
    pdf.rect(15, y_start, 180, 64, "F")
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.rect(15, y_start, 180, 64, "D")

    pdf.set_xy(20, y_start + 4)
    pdf.set_font("courier", "B", 8.5)
    pdf.set_text_color(27, 54, 93)
    pdf.cell(0, 4.6, "| Product Name         | HS Code | Sourcing | FTA Adv | Reg Comp | Demand | Total | Status   |", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(20)
    pdf.cell(0, 4.6, "|----------------------|---------|----------|---------|----------|--------|-------|----------|", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    rows = [
        ("| Centrifugal Pumps    | 8413.70 | 9        | 8       | 8        | 8      | 33/40 | Selected |", True),
        ("| Industrial Valves    | 8481.80 | 9        | 8       | 8        | 8      | 33/40 | Selected |", True),
        ("| Automotive Parts     | 8708.29 | 9        | 8       | 7        | 8      | 32/40 | Selected |", True),
        ("| Fasteners            | 7318.15 | 8        | 7       | 8        | 7      | 30/40 | Rejected |", False),
        ("| Castings & Forgings  | 7325.10 | 8        | 7       | 8        | 7      | 30/40 | Rejected |", False),
        ("| Electric Motors      | 8501.52 | 7        | 8       | 6        | 9      | 30/40 | Rejected |", False),
        ("|Agricultural Machinery| 8432.29 | 7        | 7       | 6        | 6      | 26/40 | Rejected |", False),
        ("| CNC Machine Tools    | 8458.11 | 6        | 7       | 6        | 7      | 26/40 | Rejected |", False),
        ("| Power Transformers   | 8504.22 | 5        | 7       | 4        | 9      | 25/40 | Rejected |", False),
        ("| Solar PV Modules     | 8541.43 | 4        | 5       | 5        | 9      | 23/40 | Rejected |", False),
    ]

    for row_text, is_selected in rows:
        pdf.set_x(20)
        if is_selected:
            pdf.set_font("courier", "B", 8.5)
            pdf.set_text_color(27, 94, 32) # Green for selected
        else:
            pdf.set_font("courier", "", 8.5)
            pdf.set_text_color(183, 28, 28) # Red for rejected
        pdf.cell(0, 4.6, row_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Restore default text style
    pdf.set_font("helvetica", "", 9.5)
    pdf.set_text_color(51, 51, 51)
    pdf.set_xy(15, y_start + 64 + 4)

    section_header(pdf, "### 3. Selection & Tie-Breaking Rationale")
    rationale_text = (
        "The scoring matrix evaluated exactly ten candidate products. A tie occurred at the top between Centrifugal Pumps (33/40) "
        "and Industrial Valves (33/40), with Automotive Parts (32/40) securing the third spot. Both pumps and valves demonstrate "
        "exceptional sourcing feasibility in India due to highly developed clusters in Tamil Nadu and Maharashtra, along with highly localized foundry operations.\n\n"
        "To break the tie and establish export priority: Centrifugal Pumps are designated as Top 1 due to immediate zero-tariff benefits under AI-ECTA and substantial agricultural irrigation demand in Australia. Industrial Valves are designated as Top 2, supported by deep domestic manufacturing clusters and rising international demand in LNG processing and municipal desalination plants.\n\n"
        "At the cutoff threshold, Fasteners, Castings & Forgings, and Electric Motors all tied with a score of 30/40. These candidate products were rejected from the top 3 selection due to critical constraints: Fasteners and Castings & Forgings are heavily exposed to the EU's Carbon Border Adjustment Mechanism (CBAM), creating significant carbon reporting costs and administrative barriers. Electric Motors are restricted by high raw material import dependencies for CRNGO electrical steel cores, which limits local value addition and margin growth."
    )
    pdf.multi_cell(180, 4.5, rationale_text)

    # ------------------ PAGE 3: SELECTED PRODUCT PROFILES 1 & 2 ------------------
    pdf.add_page()

    section_header(pdf, "### 4. Selected Product Profiles")

    # Product 1: Centrifugal Pumps
    pumps_companies = [
        ("Kirloskar Brothers Limited (KBL)", "Headquartered in Pune, Maharashtra. India's largest manufacturer of centrifugal pumps. Operates large foundries in Kirloskarvadi and produces split-case, multi-stage, and canned motor pumps. CE and ISO compliant."),
        ("C.R.I. Pumps Private Limited", "Headquartered in Coimbatore, Tamil Nadu. Exporter of agricultural, residential, and industrial pumps. Highly customized slurry and chemical pumps complying with European CE and international ISO standards."),
        ("Texmo Industries (Taro Pumps)", "Based in Coimbatore, Tamil Nadu. Operates integrated automated foundries for high-dimensional accuracy of impellers and casings. Major exporter of agricultural submersibles.")
    ]
    write_profile(
        pdf=pdf,
        title="Centrifugal Pumps (HS 8413.70)",
        origin="Sourced from Coimbatore (Tamil Nadu) - the 'Pump City of India' which manufactures over 50% of the country's pumps - along with Ahmedabad and Rajkot (Gujarat), and Kolhapur (Maharashtra). Foundries provide high-grade castings (grades FG 200, FG 260, SS304, SS316).",
        markets="Australia (Melbourne, Sydney, Brisbane) under AI-ECTA 0% duty; Europe (Rotterdam, Hamburg, Antwerp) under EU MFN Tariff of 1.7%; New Zealand (Auckland, Tauranga) under MFN Tariff of 5% or duty concessions.",
        demand="India's exports of centrifugal pumps reached USD 812.0 million / INR 6,700.0 Crores in FY 2024-2025. The European centrifugal pump market is projected to reach USD 5.8 billion by 2026, exhibiting a CAGR of 5.2%. In Australia, municipal water treatment and mining dewatering represent a USD 900.0 million market.",
        sectors="Agricultural irrigation in Australia and New Zealand, municipal utility plants (wastewater treatment) in Europe, mining and minerals dewatering (slurry applications) in Western Australia.",
        companies=pumps_companies
    )
    
    pdf.ln(2)

    # Product 2: Industrial Valves
    valves_companies = [
        ("L&T Valves Limited", "Wholly-owned subsidiary of Larsen & Toubro, headquartered in Chennai, Tamil Nadu, with plants in Coimbatore and Kanchipuram. Produces gates, globes, checks, balls, butterflies, and control valves. Fully certified under API 6D, CE/PED, and ISO 15848-1."),
        ("Microfinish Valves Private Limited", "Headquartered in Hubli, Karnataka. Specialist manufacturer of ball valves, gates, globes, checks, and chemical pumps. Certified under CE/PED and API 6D."),
        ("Dembla Valves Limited", "Headquartered in Thane, Maharashtra. Specializes in control valves and butterfly valves, exporting heavily to Europe and Australia.")
    ]
    write_profile(
        pdf=pdf,
        title="Industrial Valves (HS 8481.80)",
        origin="Concentrated in Coimbatore and Trichy (Tamil Nadu), Ahmedabad and Vadodara (Gujarat), and Mumbai-Pune (Maharashtra). Steel casting (ASTM A216 WCB, ASTM A351 CF8/CF8M) is fully localized.",
        markets="Australia (Dampier, Gladstone, Fremantle) under AI-ECTA 0% duty (down from 5% MFN); Europe (Genoa, Le Havre, Rotterdam) under EU MFN Tariff of 2.2%; New Zealand (New Plymouth regional energy hub) under MFN Tariff of 5% or concession exemptions.",
        demand="India's industrial valves exports represented USD 920.0 million / INR 7,600.0 Crores in FY 2024-2025. The European market is growing at a CAGR of 4.5% due to green hydrogen infrastructure and chemical plant retrofits. The Australian valves market is expanding at 5.4% annually, driven by natural gas extraction and desalination.",
        sectors="Oil & gas LNG processing and transport pipelines, municipal desalination and waterworks, chemical and petrochemical processing plants (low-fugitive emissions) in Germany/Belgium.",
        companies=valves_companies
    )

    # ------------------ PAGE 4: PROFILE 3 & REJECTED PRODUCTS ------------------
    pdf.add_page()

    # Product 3: Automotive Parts
    auto_companies = [
        ("Bharat Forge Limited", "Part of the Kalyani Group, headquartered in Pune, Maharashtra. The world's largest forging company, exporting crankshafts, camshafts, steering knuckles, and chassis parts to global OEMs (e.g., in Germany, Sweden)."),
        ("Sundram Fasteners Limited", "Part of the TVS Group, headquartered in Chennai, Tamil Nadu. Manufactures high-tensile fasteners, powder metallurgy parts, radiator caps, and hot-forged components for automotive OEMs."),
        ("Uno Minda Limited", "Headquartered in Gurugram, Haryana. Tier-1 supplier of switching, lighting, and acoustic systems, holding global certifications (IATF 16949, European E-Mark safety approvals).")
    ]
    write_profile(
        pdf=pdf,
        title="Automotive Parts (HS 8708.29)",
        origin="Major manufacturing hubs are Chennai (Tamil Nadu) - representing 35% of India's auto component production - Pune-Chakan (Maharashtra) for forging/stamping, and Gurugram-Manesar (Haryana).",
        markets="Australia (Melbourne, Adelaide) under AI-ECTA 0% duty (down from 5%); Europe (Bremerhaven, Zeebrugge, Gothenburg) under EU MFN Tariff of 3.0% to 4.5%; New Zealand (Auckland) under MFN Tariff of 5%.",
        demand="India's exports of automotive parts and accessories (HS 8708) reached USD 12.4 billion / INR 1,03,000.0 Crores in FY 2024-2025. European imports of Indian auto parts were valued at USD 3.6 billion (~INR 30,000.0 Crores). Exports of steering and braking systems to Australia/NZ reached USD 120.0 million (~INR 1,000.0 Crores).",
        sectors="Passenger vehicle original equipment manufacturers (OEMs) in Germany and France, commercial vehicle assembly units, and automotive aftermarket parts distribution networks.",
        companies=auto_companies
    )

    pdf.ln(2)

    section_header(pdf, "### 5. Rejected Candidate Products")

    rejections = [
        ("Fasteners", "Rejected due to EU CBAM carbon border taxes and low profit margins."),
        ("Castings & Forgings", "Covered under EU CBAM, energy-intensive foundries, and high freight costs."),
        ("Electric Motors", "Import dependency on CRNGO electrical steel and strict AS/NZS standards."),
        ("Power Transformers", "Import dependency on CRGO steel cores and high grid-testing costs."),
        ("Agricultural Machinery", "Non-road Stage V emission rules and high shipping logistics costs."),
        ("Solar PV Modules", "Sourcing dependency on China cells and low-cost Chinese imports."),
        ("CNC Machine Tools", "Import dependency for controllers and low domestic value addition.")
    ]

    pdf.set_font("helvetica", "", 9.5)
    for name, reason in rejections:
        pdf.cell(0, 5.2, f"- {name}: {reason}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    section_header(pdf, "### 6. Export Strategic Recommendations")
    recommendations_text = (
        "1. Leverage AI-ECTA Zero-Tariff Access: Focus marketing campaigns on Australian mining, municipal water, and agricultural sectors for immediate tariff gains on pumps and valves.\n"
        "2. Prepare for European CBAM Expansion: Assist Indian foundries and auto component manufacturers in establishing carbon auditing frameworks to mitigate future CBAM tariff impacts.\n"
        "3. Mitigate Raw Material Risk: Form long-term supply agreements for CRGO/CRNGO electrical steel and semiconductor controllers to reduce import dependencies for complex electrical machinery."
    )
    pdf.multi_cell(180, 4.5, recommendations_text)

    # Output PDF
    os.makedirs(os.path.dirname(os.path.abspath("C:/Users/HP/Desktop/Coding Playground/Antigravity/market research/india_engineering_export_feasibility.pdf")), exist_ok=True)
    pdf.output("C:/Users/HP/Desktop/Coding Playground/Antigravity/market research/india_engineering_export_feasibility.pdf")
    print("Report compiled successfully at market research/india_engineering_export_feasibility.pdf")

if __name__ == "__main__":
    main()
