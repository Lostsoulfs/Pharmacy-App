"""Clinical reference data — carried verbatim from v13 per ADR-C05.

NOT externally verified. Any UI panel that renders an entry from these
structures MUST show the UNVERIFIED warning (config.CLINICAL_DATA_UNVERIFIED).
"""

RED_FLAGS = [
    {"q": "Patient picking up Warfarin and Advil (Ibuprofen)?",
     "a": "Bleeding Risk",
     "rationale": "NSAIDs increase blood-thinning effects."},
    {"q": "C-II Codeine syrup from out-of-state dentist?",
     "a": "Diversion Risk",
     "rationale": "Common red flag for forged scripts."},
    {"q": "Cash price for 90-day supply of Oxycodone?",
     "a": "Pharmacist Review",
     "rationale": "High volume C-II cash payments require pharmacist override."},
    {"q": "Methotrexate written for once-daily dosing?",
     "a": "Dosing Error",
     "rationale": "Methotrexate for most indications is dosed WEEKLY; "
                  "daily dosing is a known fatal error."},
    {"q": "Patient with a documented penicillin allergy handed "
          "Amoxicillin?",
     "a": "Allergy Check",
     "rationale": "Amoxicillin is a penicillin — verify the allergy "
                  "with the pharmacist before dispensing."},
    {"q": "Patient on Sildenafil also picking up Nitroglycerin?",
     "a": "Drug Interaction",
     "rationale": "PDE5 inhibitors with nitrates can cause severe, "
                  "life-threatening hypotension."},
    {"q": "Controlled-substance scripts from several different "
          "prescribers in a short window?",
     "a": "Diversion Risk",
     "rationale": "Prescriber shopping is a classic diversion pattern."},
    {"q": "SSRI antidepressant filled alongside Tramadol?",
     "a": "Drug Interaction",
     "rationale": "Both raise serotonin — combined use risks "
                  "serotonin syndrome and lowers the seizure "
                  "threshold."},
    {"q": "Adult-strength dose on a prescription for a small child?",
     "a": "Dosing Error",
     "rationale": "Pediatric doses are weight-based — confirm the "
                  "dose against the child's weight."},
    {"q": "Patient buying large or repeated quantities of "
          "pseudoephedrine?",
     "a": "Diversion Risk",
     "rationale": "Pseudoephedrine is a meth precursor; logbook, ID "
                  "and quantity limits apply."},
    {"q": "ACE inhibitor (e.g. Lisinopril) with a potassium "
          "supplement?",
     "a": "Drug Interaction",
     "rationale": "ACE inhibitors raise serum potassium — combined "
                  "use risks hyperkalemia."},
    {"q": "Isotretinoin presented by a patient who may be pregnant?",
     "a": "Pharmacist Review",
     "rationale": "Isotretinoin is a known teratogen; iPLEDGE "
                  "pregnancy requirements must be met."},
    {"q": "Opioid prescription presented well before the previous "
          "fill should have run out?",
     "a": "Pharmacist Review",
     "rationale": "Early controlled-substance refills need "
                  "pharmacist review and a PDMP check."},
    {"q": "Aspirin on a prescription for a child with a viral "
          "illness?",
     "a": "Pharmacist Review",
     "rationale": "Aspirin in children with viral illness is linked "
                  "to Reye's syndrome."},
]

LASA_PAIRS = [
    {"q": "Look-Alike: Hydroxyzine vs Hydralazine. Which is for Itching?",
     "a": "Hydroxyzine",
     "rationale": "Hydralazine is for blood pressure."},
    {"q": "Sound-Alike: Humalog vs Humulin. Which is rapid-acting?",
     "a": "Humalog",
     "rationale": "Humulin is intermediate-acting."},
    {"q": "Look-Alike: Zyrtec vs Zyprexa. Which is for allergies?",
     "a": "Zyrtec",
     "rationale": "Zyprexa is an antipsychotic."},
    {"q": "Look-Alike: Celebrex vs Celexa. Which treats "
          "arthritis pain?",
     "a": "Celebrex",
     "rationale": "Celexa (citalopram) is an antidepressant."},
    {"q": "Sound-Alike: Klonopin vs Clonidine. Which treats "
          "seizures and anxiety?",
     "a": "Klonopin",
     "rationale": "Clonidine is used for high blood pressure."},
    {"q": "Look-Alike: Lamictal vs Lamisil. Which treats seizures?",
     "a": "Lamictal",
     "rationale": "Lamisil (terbinafine) is an antifungal."},
    {"q": "Sound-Alike: Tramadol vs Trazodone. Which is a pain "
          "reliever?",
     "a": "Tramadol",
     "rationale": "Trazodone is used for depression and sleep."},
    {"q": "Sound-Alike: Bupropion vs Buspirone. Which is used for "
          "smoking cessation?",
     "a": "Bupropion",
     "rationale": "Buspirone is used for anxiety."},
    {"q": "Sound-Alike: Novolog vs Novolin. Which is rapid-acting?",
     "a": "Novolog",
     "rationale": "Novolin is intermediate-acting."},
    {"q": "Look-Alike: Lantus vs Latuda. Which is a long-acting "
          "insulin?",
     "a": "Lantus",
     "rationale": "Latuda (lurasidone) is an antipsychotic."},
    {"q": "Look-Alike: Plavix vs Paxil. Which is a blood thinner?",
     "a": "Plavix",
     "rationale": "Paxil (paroxetine) is an antidepressant."},
    {"q": "Sound-Alike: Zantac vs Xanax. Which treats heartburn?",
     "a": "Zantac",
     "rationale": "Xanax (alprazolam) is used for anxiety."},
    {"q": "Look-Alike: Diflucan vs Diprivan. Which is an "
          "antifungal?",
     "a": "Diflucan",
     "rationale": "Diprivan (propofol) is an anesthetic."},
    {"q": "Sound-Alike: Cyclobenzaprine vs Cyproheptadine. Which is "
          "a muscle relaxant?",
     "a": "Cyclobenzaprine",
     "rationale": "Cyproheptadine is an antihistamine."},
]

SIG_ABBREVIATIONS = {
    "QD": "once daily", "QDAY": "once daily",
    "BID": "twice daily", "TID": "three times daily",
    "QID": "four times daily", "QHS": "at bedtime",
    "QAM": "every morning", "QPM": "every evening",
    "PRN": "as needed", "PO": "by mouth",
    "SL": "under the tongue", "TOP": "apply topically",
    "OU": "both eyes", "OD": "right eye", "OS": "left eye",
    "AU": "both ears", "AD": "right ear", "AS": "left ear",
    "AC": "before meals", "PC": "after meals",
    "Q4H": "every 4 hours", "Q6H": "every 6 hours",
    "Q8H": "every 8 hours", "Q12H": "every 12 hours",
    "UD": "as directed", "AAA": "apply to affected area",
    "NTE": "not to exceed",
}

COMMON_RX_FLAGS = [
    ("warfarin",       "NSAID / aspirin / antibiotic interactions: pharmacist review."),
    ("methotrexate",   "Weekly dosing risk. Verify not accidentally entered daily."),
    ("insulin",        "Confirm type, concentration, max daily dose, and days supply."),
    ("levothyroxine",  "Separate from calcium/iron; consistency matters."),
    ("tramadol",       "Controlled-substance workflow; serotonin/seizure-risk screen."),
    ("alprazolam",     "Controlled-substance workflow; sedation/duplicate benzo screen."),
    ("amoxicillin",    "Confirm allergy history and pediatric weight-based dosing when applicable."),
]

BRAND_GENERIC = [
    {"brand": "Lipitor",    "generic": "Atorvastatin"},
    {"brand": "Synthroid",  "generic": "Levothyroxine"},
    {"brand": "Prinivil",   "generic": "Lisinopril"},
    {"brand": "Glucophage", "generic": "Metformin"},
    {"brand": "Zocor",      "generic": "Simvastatin"},
    {"brand": "Cozaar",     "generic": "Losartan"},
    {"brand": "Prilosec",   "generic": "Omeprazole"},
    {"brand": "Neurontin",  "generic": "Gabapentin"},
    {"brand": "Norvasc",    "generic": "Amlodipine"},
    {"brand": "Vicodin",    "generic": "Hydrocodone/APAP"},
    {"brand": "Zoloft",     "generic": "Sertraline"},
    {"brand": "ProAir",     "generic": "Albuterol"},
    {"brand": "Flonase",    "generic": "Fluticasone"},
    {"brand": "Singulair",  "generic": "Montelukast"},
    {"brand": "Amoxil",     "generic": "Amoxicillin"},
    {"brand": "Mobic",      "generic": "Meloxicam"},
    {"brand": "Plavix",     "generic": "Clopidogrel"},
    {"brand": "Lexapro",    "generic": "Escitalopram"},
    {"brand": "Crestor",    "generic": "Rosuvastatin"},
    {"brand": "Advil",      "generic": "Ibuprofen"},
    {"brand": "Tylenol",    "generic": "Acetaminophen"},
    {"brand": "Lasix",      "generic": "Furosemide"},
    {"brand": "Desyrel",    "generic": "Trazodone"},
    {"brand": "Cymbalta",   "generic": "Duloxetine"},
    {"brand": "Klor-Con",   "generic": "Potassium Chloride"},
    {"brand": "Toprol XL",  "generic": "Metoprolol Succinate"},
    {"brand": "Lopressor",  "generic": "Metoprolol Tartrate"},
    {"brand": "Zantac",     "generic": "Ranitidine"},
    {"brand": "Pravachol",  "generic": "Pravastatin"},
    {"brand": "Coreg",      "generic": "Carvedilol"},
    {"brand": "Ultram",     "generic": "Tramadol"},
    {"brand": "Valium",     "generic": "Diazepam"},
    {"brand": "Xanax",      "generic": "Alprazolam"},
    {"brand": "Klonopin",   "generic": "Clonazepam"},
    {"brand": "Ativan",     "generic": "Lorazepam"},
    {"brand": "Coumadin",   "generic": "Warfarin"},
    {"brand": "Flomax",     "generic": "Tamsulosin"},
    {"brand": "Tenormin",   "generic": "Atenolol"},
    {"brand": "Effexor",    "generic": "Venlafaxine"},
    {"brand": "Seroquel",   "generic": "Quetiapine"},
    {"brand": "Risperdal",  "generic": "Risperidone"},
    {"brand": "Paxil",      "generic": "Paroxetine"},
    {"brand": "Prozac",     "generic": "Fluoxetine"},
    {"brand": "Wellbutrin", "generic": "Bupropion"},
    {"brand": "Adderall",   "generic": "Amphetamine/Dextroamphetamine"},
    {"brand": "Concerta",   "generic": "Methylphenidate"},
    {"brand": "Flexeril",   "generic": "Cyclobenzaprine"},
    {"brand": "Zanaflex",   "generic": "Tizanidine"},
]

# VACCINES — pharmacy-administered immunization quick-reference.
#
# GENERATED, NOT EXTERNALLY VERIFIED (added 2026-05-20 to resolve the
# empty panel_vaccines placeholder). Every eligibility age, dose count
# and interval below MUST be cross-checked against the current
# CDC/ACIP immunization schedule (cdc.gov/vaccines/schedules) before
# any clinical use — schedules change annually. Pharmacist scope of
# practice also varies by state and patient age: what a pharmacist may
# administer, and to whom, is set by state law and is NOT captured
# here. Handle under the same ADR-C05 UNVERIFIED rule as the rest of
# this module — the UI MUST show the UNVERIFIED banner.
VACCINES = [
    {"vaccine": "Influenza (inactivated, IIV)",
     "ages": "6 months and older",
     "schedule": "1 dose every flu season. Children 6 months "
                 "through 8 years may need 2 doses (4 weeks apart) "
                 "the first season they are vaccinated.",
     "notes": "High-dose or adjuvanted formulations are generally "
              "preferred for adults 65 and older."},
    {"vaccine": "COVID-19",
     "ages": "6 months and older",
     "schedule": "Per the current CDC guidance for the season's "
                 "formulation; number of doses depends on age and "
                 "immune status.",
     "notes": "Formulation and dosing change frequently — always "
              "confirm against the current CDC schedule."},
    {"vaccine": "Pneumococcal conjugate (PCV15 / PCV20 / PCV21)",
     "ages": "Adults 50 and older; younger adults 19-49 with certain "
             "risk conditions; routine infant series under 2.",
     "schedule": "Adult: usually a single dose; if PCV15 is used a "
                 "dose of PPSV23 follows, typically 1 year later.",
     "notes": "Do not give PCV and PPSV23 at the same visit. Check "
              "what the patient has already received."},
    {"vaccine": "Pneumococcal polysaccharide (PPSV23)",
     "ages": "Adults at risk; follows PCV15 when that product is used",
     "schedule": "1 dose; a second dose may apply for certain "
                 "high-risk groups.",
     "notes": "Sequencing with PCV products matters — verify the "
              "patient's pneumococcal history."},
    {"vaccine": "Shingles (RZV, Shingrix)",
     "ages": "Adults 50 and older; immunocompromised adults 19+",
     "schedule": "2 doses, 2 to 6 months apart.",
     "notes": "Recombinant, non-live. Give the 2nd dose even if it "
              "is past the 6-month window — do not restart."},
    {"vaccine": "Tdap / Td",
     "ages": "Tdap from age 7; Td or Tdap booster thereafter",
     "schedule": "1 Tdap dose, then a Td or Tdap booster every "
                 "10 years.",
     "notes": "1 dose of Tdap is recommended in every pregnancy. "
              "Tdap is also given for wound management."},
    {"vaccine": "Hepatitis B",
     "ages": "All ages; routine for adults 19-59, and 60+ with risk",
     "schedule": "2-, 3-, or 4-dose series depending on the product.",
     "notes": "Confirm which product is used so the interval and "
              "dose count match."},
    {"vaccine": "Hepatitis A",
     "ages": "Children from 12 months; adults at risk or who want it",
     "schedule": "2 doses, at least 6 months apart.",
     "notes": "Combination Hep A/Hep B products use a separate "
              "multi-dose schedule."},
    {"vaccine": "HPV (Gardasil 9)",
     "ages": "Routine at 11-12 (can start at 9); through age 26; "
             "shared decision-making for ages 27-45",
     "schedule": "2 doses if started before the 15th birthday; "
                 "3 doses if started at 15 or older, or if "
                 "immunocompromised.",
     "notes": "Dose count depends on age at the first dose."},
    {"vaccine": "MMR (measles, mumps, rubella)",
     "ages": "Children from 12 months; adults without immunity",
     "schedule": "2 doses, at least 4 weeks apart.",
     "notes": "Live vaccine — contraindicated in pregnancy and "
              "significant immunocompromise."},
    {"vaccine": "Varicella (chickenpox)",
     "ages": "Children from 12 months; adults without immunity",
     "schedule": "2 doses, 4 to 8 weeks apart for adults.",
     "notes": "Live vaccine — contraindicated in pregnancy and "
              "significant immunocompromise."},
    {"vaccine": "RSV",
     "ages": "Adults 75 and older; adults 60-74 at increased risk; "
             "maternal dose in pregnancy; infant products separate",
     "schedule": "Single dose for eligible adults.",
     "notes": "Several distinct products exist (older-adult, "
              "maternal, infant) — confirm the correct one."},
    {"vaccine": "Meningococcal (MenACWY / MenB)",
     "ages": "MenACWY routine at 11-12 with a booster at 16; MenB "
             "shared decision-making for ages 16-23",
     "schedule": "MenACWY: 2 doses in adolescence. MenB: 2- or "
                 "3-dose series by product.",
     "notes": "MenACWY and MenB are different vaccines and are not "
              "interchangeable."},
]
