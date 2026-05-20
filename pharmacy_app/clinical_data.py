"""Clinical reference data — carried verbatim from v13 per ADR-C05.

NOT externally verified. Any UI panel that renders an entry from these
structures MUST show the UNVERIFIED warning until the dataset's key in
config.DATA_VERIFIED is flipped True.
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

# BRAND_GENERIC — the PTCB "Top 200" drug set (210 entries).
# VERIFIED 2026-05-20: brand/generic pairs cross-checked against
# FDA/DailyMed-class references; see
# docs/audits/brand_generic_audit_2026-05-20.md. brand fields list
# common trade names (slash-separated where several apply);
# drug_class is a coarse therapeutic category for display only, not a
# clinical reference.
BRAND_GENERIC = [
    {"brand": "Lexapro", "generic": "Escitalopram", "drug_class": "SSRI antidepressant"},
    {"brand": "Roxicodone", "generic": "Oxycodone", "drug_class": "Opioid analgesic"},
    {"brand": "Prinivil/Qbrelis/Zestril", "generic": "Lisinopril", "drug_class": "ACE inhibitor"},
    {"brand": "Zocor", "generic": "Simvastatin", "drug_class": "Statin"},
    {"brand": "Synthroid", "generic": "Levothyroxine", "drug_class": "Thyroid hormone"},
    {"brand": "Amoxil/Trimox", "generic": "Amoxicillin", "drug_class": "Antibacterial"},
    {"brand": "Zithromax", "generic": "Azithromycin", "drug_class": "Macrolide antibacterial"},
    {"brand": "Microzide/Aquazide H", "generic": "Hydrochlorothiazide", "drug_class": "Thiazide diuretic"},
    {"brand": "Norvasc", "generic": "Amlodipine", "drug_class": "Calcium channel blocker"},
    {"brand": "Xanax", "generic": "Alprazolam", "drug_class": "Benzodiazepine"},
    {"brand": "Glumetza/Riomet/Glucophage/Fortamet", "generic": "Metformin", "drug_class": "Oral antidiabetic"},
    {"brand": "Lipitor", "generic": "Atorvastatin", "drug_class": "Statin"},
    {"brand": "Prilosec", "generic": "Omeprazole", "drug_class": "Proton-pump inhibitor"},
    {"brand": "Cipro/Cipro XR/Proquin", "generic": "Ciprofloxacin", "drug_class": "Fluoroquinolone"},
    {"brand": "Zofran", "generic": "Ondansetron", "drug_class": "Antiemetic"},
    {"brand": "Clozaril", "generic": "Clozapine", "drug_class": "Antipsychotic"},
    {"brand": "Lasix", "generic": "Furosemide", "drug_class": "Loop diuretic"},
    {"brand": "Levitra", "generic": "Vardenafil", "drug_class": "PDE5 inhibitor"},
    {"brand": "Sumycin/Ala-Tet/Brodspec", "generic": "Tetracycline", "drug_class": "Tetracycline antibacterial"},
    {"brand": "Heparin Sodium", "generic": "Heparin", "drug_class": "Anticoagulant"},
    {"brand": "Valcyte", "generic": "Valganciclovir", "drug_class": "Antiviral"},
    {"brand": "Lamictal", "generic": "Lamotrigine", "drug_class": "Anticonvulsant"},
    {"brand": "Diflucan", "generic": "Fluconazole", "drug_class": "Antifungal"},
    {"brand": "Tenormin", "generic": "Atenolol", "drug_class": "Beta-blocker"},
    {"brand": "Singulair", "generic": "Montelukast", "drug_class": "Leukotriene receptor blocker"},
    {"brand": "Flonase Nasal Spray", "generic": "Fluticasone propionate", "drug_class": "Corticosteroid"},
    {"brand": "Zyloprim", "generic": "Allopurinol", "drug_class": "Anti-gout"},
    {"brand": "Fosamax", "generic": "Alendronate", "drug_class": "Bisphosphonate"},
    {"brand": "Pepcid", "generic": "Famotidine", "drug_class": "H2 antagonist"},
    {"brand": "Omnicef", "generic": "Cefdinir", "drug_class": "Cephalosporin antibacterial"},
    {"brand": "Yaz", "generic": "Ethinyl estradiol/Drospirenone", "drug_class": "Birth control"},
    {"brand": "Apresoline", "generic": "Hydralazine", "drug_class": "Antihypertensive"},
    {"brand": "Cogentin", "generic": "Benztropine", "drug_class": "Antiparkinsonian"},
    {"brand": "Aller-Chlor", "generic": "Chlorpheniramine", "drug_class": "Antihistamine"},
    {"brand": "Paxil", "generic": "Paroxetine", "drug_class": "SSRI antidepressant"},
    {"brand": "Ativan", "generic": "Lorazepam", "drug_class": "Benzodiazepine"},
    {"brand": "Pyridium", "generic": "Phenazopyridine", "drug_class": "UTI analgesic"},
    {"brand": "Plaquenil", "generic": "Hydroxychloroquine", "drug_class": "Anti-malarial"},
    {"brand": "Lidoderm", "generic": "Lidocaine", "drug_class": "Local anesthetic"},
    {"brand": "Cataflam/Voltaren", "generic": "Diclofenac", "drug_class": "NSAID"},
    {"brand": "Rayos/Deltasone", "generic": "Prednisone", "drug_class": "Corticosteroid"},
    {"brand": "Zetia", "generic": "Ezetimibe", "drug_class": "Antihyperlipidemic"},
    {"brand": "Evista", "generic": "Raloxifene", "drug_class": "SERM"},
    {"brand": "Dilantin", "generic": "Phenytoin", "drug_class": "Anticonvulsant"},
    {"brand": "Lovaza", "generic": "Omega-3 fatty acids", "drug_class": "Anti-triglyceride"},
    {"brand": "Zanaflex", "generic": "Tizanidine", "drug_class": "Muscle relaxant"},
    {"brand": "Tezruly/Hytrin", "generic": "Terazosin", "drug_class": "Alpha-1 blocker"},
    {"brand": "Dyrenium", "generic": "Triamterene", "drug_class": "Potassium-sparing diuretic"},
    {"brand": "Altace", "generic": "Ramipril", "drug_class": "ACE inhibitor"},
    {"brand": "Pravachol", "generic": "Pravastatin", "drug_class": "Statin"},
    {"brand": "Risperdal", "generic": "Risperidone", "drug_class": "Antipsychotic"},
    {"brand": "Lunesta", "generic": "Eszopiclone", "drug_class": "Z-drug/hypnotic"},
    {"brand": "Celebrex", "generic": "Celecoxib", "drug_class": "COX-2 selective NSAID"},
    {"brand": "Premarin", "generic": "Conjugated estrogens", "drug_class": "Estrogen replacement"},
    {"brand": "Avelox/Vigamox", "generic": "Moxifloxacin", "drug_class": "Fluoroquinolone"},
    {"brand": "Aricept", "generic": "Donepezil", "drug_class": "Acetylcholinesterase inhibitor"},
    {"brand": "Macrobid/Macrodantin", "generic": "Nitrofurantoin", "drug_class": "Antibacterial for UTIs"},
    {"brand": "Duragesic Skin Patch", "generic": "Fentanyl", "drug_class": "Opioid narcotic"},
    {"brand": "Imdur", "generic": "Isosorbide mononitrate", "drug_class": "Nitrate"},
    {"brand": "Prozac/Sarafem", "generic": "Fluoxetine", "drug_class": "SSRI antidepressant"},
    {"brand": "Aristocort", "generic": "Triamcinolone", "drug_class": "Corticosteroid"},
    {"brand": "Suboxone", "generic": "Buprenorphine/Naloxone", "drug_class": "Narcotic/Opioid blocker"},
    {"brand": "Vyvanse", "generic": "Lisdexamfetamine", "drug_class": "CNS Stimulant"},
    {"brand": "Pamelor", "generic": "Nortriptyline", "drug_class": "Tricyclic antidepressant"},
    {"brand": "Humalog", "generic": "Insulin lispro", "drug_class": "Rapid-acting insulin"},
    {"brand": "Depacon/Depakote", "generic": "Valproate sodium", "drug_class": "Anticonvulsant"},
    {"brand": "BetaSept/ChloraPrep", "generic": "Chlorhexidine", "drug_class": "Disinfectant/antiseptic"},
    {"brand": "Dibent/Bentyl", "generic": "Dicyclomine", "drug_class": "Anti-spasmodic"},
    {"brand": "Imitrex", "generic": "Sumatriptan", "drug_class": "Anti-migraine"},
    {"brand": "Protonix", "generic": "Pantoprazole", "drug_class": "Proton-pump inhibitor"},
    {"brand": "Lopressor", "generic": "Metoprolol tartrate", "drug_class": "Beta-blocker"},
    {"brand": "Robitussin", "generic": "Dextromethorphan/Guaifenesin", "drug_class": "Antitussive/Expectorant"},
    {"brand": "Valium", "generic": "Diazepam", "drug_class": "Benzodiazepine"},
    {"brand": "Viagra", "generic": "Sildenafil", "drug_class": "PDE5 inhibitor"},
    {"brand": "Bactroban", "generic": "Mupirocin", "drug_class": "Antibacterial"},
    {"brand": "Januvia", "generic": "Sitagliptin", "drug_class": "Antidiabetic"},
    {"brand": "Reglan", "generic": "Metoclopramide", "drug_class": "Dopamine antagonist"},
    {"brand": "Relafen", "generic": "Nabumetone", "drug_class": "NSAID"},
    {"brand": "Keflex", "generic": "Cephalexin", "drug_class": "Cephalosporin"},
    {"brand": "Effexor", "generic": "Venlafaxine", "drug_class": "SNRI"},
    {"brand": "Boniva", "generic": "Ibandronate", "drug_class": "Bisphosphonate"},
    {"brand": "Axid", "generic": "Nizatidine", "drug_class": "H2 receptor antagonist"},
    {"brand": "Ex-Lax/Senna Lax", "generic": "Senna", "drug_class": "Laxative"},
    {"brand": "NovoLog", "generic": "Insulin aspart", "drug_class": "Rapid-acting insulin"},
    {"brand": "Bayer/Ecotrin/Bufferin", "generic": "Aspirin", "drug_class": "Antipyretic/Analgesic"},
    {"brand": "Gablofen/Lioresal", "generic": "Baclofen", "drug_class": "Muscle relaxant"},
    {"brand": "Flagyl", "generic": "Metronidazole", "drug_class": "Antibacterial/Antiprotozoal"},
    {"brand": "Keppra", "generic": "Levetiracetam", "drug_class": "Anticonvulsant"},
    {"brand": "Colcrys/Mitigare", "generic": "Colchicine", "drug_class": "Anti-gout"},
    {"brand": "Zyprexa", "generic": "Olanzapine", "drug_class": "Antipsychotic"},
    {"brand": "Avodart", "generic": "Dutasteride", "drug_class": "5-alpha reductase inhibitor"},
    {"brand": "TriCor/Antara", "generic": "Fenofibrate", "drug_class": "Fibrate"},
    {"brand": "Cardura", "generic": "Doxazosin", "drug_class": "Alpha-1 blocker"},
    {"brand": "Aleve/Naprosyn", "generic": "Naproxen", "drug_class": "NSAID"},
    {"brand": "Aldactone", "generic": "Spironolactone", "drug_class": "Potassium-sparing diuretic"},
    {"brand": "Namenda", "generic": "Memantine", "drug_class": "NMDA antagonist"},
    {"brand": "Methadose", "generic": "Methadone", "drug_class": "Opioid analgesic"},
    {"brand": "Vasotec/Epaned", "generic": "Enalapril", "drug_class": "ACE inhibitor"},
    {"brand": "Tamiflu", "generic": "Oseltamivir", "drug_class": "Antiviral"},
    {"brand": "Requip", "generic": "Ropinirole", "drug_class": "Antiparkinsonian"},
    {"brand": "Veetids", "generic": "Penicillin V potassium", "drug_class": "Beta-lactam antibacterial"},
    {"brand": "Strattera", "generic": "Atomoxetine", "drug_class": "Norepinephrine reuptake inhibitor"},
    {"brand": "Ambien", "generic": "Zolpidem", "drug_class": "Z-drug/hypnotic"},
    {"brand": "Advair", "generic": "Salmeterol/Fluticasone", "drug_class": "Beta-2 agonist/Inhaled corticosteroid"},
    {"brand": "Levaquin", "generic": "Levofloxacin", "drug_class": "Fluoroquinolone antibacterial"},
    {"brand": "Tofranil", "generic": "Imipramine", "drug_class": "Tricyclic antidepressant"},
    {"brand": "Reclast/Zometa", "generic": "Zoledronic acid", "drug_class": "Bisphosphonate"},
    {"brand": "Glucotrol", "generic": "Glipizide", "drug_class": "Antidiabetic"},
    {"brand": "Generlac/Constulose", "generic": "Lactulose", "drug_class": "Laxative"},
    {"brand": "AcipHex", "generic": "Rabeprazole", "drug_class": "Proton-pump inhibitor"},
    {"brand": "Otrexup", "generic": "Methotrexate", "drug_class": "DMARD/Anticancer"},
    {"brand": "Cleocin", "generic": "Clindamycin", "drug_class": "Antibacterial"},
    {"brand": "Tylenol", "generic": "Acetaminophen", "drug_class": "Analgesic/Antipyretic"},
    {"brand": "Feosol", "generic": "Ferrous sulfate", "drug_class": "Iron supplement"},
    {"brand": "Relpax", "generic": "Eletriptan", "drug_class": "Antimigraine"},
    {"brand": "Carbacot/Robaxin", "generic": "Methocarbamol", "drug_class": "Muscle relaxant"},
    {"brand": "DiaBeta", "generic": "Glyburide", "drug_class": "Antidiabetic"},
    {"brand": "Celexa", "generic": "Citalopram", "drug_class": "SSRI antidepressant"},
    {"brand": "Benicar", "generic": "Olmesartan", "drug_class": "Angiotensin II blocker"},
    {"brand": "Coreg", "generic": "Carvedilol", "drug_class": "Beta-blocker"},
    {"brand": "Spiriva", "generic": "Tiotropium", "drug_class": "Anticholinergic"},
    {"brand": "Xolair", "generic": "Omalizumab", "drug_class": "Monoclonal antibody"},
    {"brand": "NitroStat Sublingual", "generic": "Nitroglycerin", "drug_class": "Nitrate"},
    {"brand": "Eliquis", "generic": "Apixaban", "drug_class": "Anticoagulant"},
    {"brand": "Neurontin", "generic": "Gabapentin", "drug_class": "Anticonvulsant"},
    {"brand": "Enbrel", "generic": "Etanercept", "drug_class": "DMARD"},
    {"brand": "Herceptin", "generic": "Trastuzumab", "drug_class": "HER2-positive breast cancer treatment"},
    {"brand": "Atripla", "generic": "Emtricitabine/Tenofovir/Efavirenz", "drug_class": "Antiretroviral"},
    {"brand": "Xarelto", "generic": "Rivaroxaban", "drug_class": "Anticoagulant"},
    {"brand": "Stalevo 50", "generic": "Levodopa/Carbidopa/Entacapone", "drug_class": "Antiparkinsonian"},
    {"brand": "Fioricet", "generic": "Acetaminophen/Butalbital/Caffeine", "drug_class": "Analgesic/Barbiturate"},
    {"brand": "Levemir", "generic": "Insulin detemir", "drug_class": "Long-acting insulin"},
    {"brand": "Lovenox", "generic": "Enoxaparin", "drug_class": "Low-molecular weight heparin"},
    {"brand": "Ritalin/Concerta", "generic": "Methylphenidate", "drug_class": "CNS stimulant"},
    {"brand": "Crestor", "generic": "Rosuvastatin", "drug_class": "Statin"},
    {"brand": "Xgeva/Prolia", "generic": "Denosumab", "drug_class": "Monoclonal antibody"},
    {"brand": "Pradaxa", "generic": "Dabigatran", "drug_class": "Anticoagulant"},
    {"brand": "Clomid", "generic": "Clomiphene", "drug_class": "Infertility treatment/SERM"},
    {"brand": "Vesicare", "generic": "Solifenacin", "drug_class": "Antimuscarinic"},
    {"brand": "Haldol", "generic": "Haloperidol", "drug_class": "Antipsychotic"},
    {"brand": "Ala-Cort", "generic": "Hydrocortisone", "drug_class": "Corticosteroid"},
    {"brand": "Humulin N", "generic": "Insulin isophane (NPH)", "drug_class": "Intermediate-acting insulin"},
    {"brand": "Isentress", "generic": "Raltegravir", "drug_class": "Integrase inhibitor"},
    {"brand": "Stelara", "generic": "Ustekinumab", "drug_class": "Monoclonal antibody"},
    {"brand": "Mobic", "generic": "Meloxicam", "drug_class": "NSAID"},
    {"brand": "Remicade", "generic": "Infliximab", "drug_class": "Monoclonal antibody"},
    {"brand": "Night Time Cold and Flu", "generic": "Acetaminophen/Dextromethorphan/Doxylamine", "drug_class": "Analgesic/Antitussive/Antihistamine"},
    {"brand": "Renvela", "generic": "Sevelamer", "drug_class": "Phosphate binder"},
    {"brand": "Fragmin", "generic": "Dalteparin", "drug_class": "Low-molecular weight heparin"},
    {"brand": "Zoloft", "generic": "Sertraline", "drug_class": "SSRI antidepressant"},
    {"brand": "Klonopin", "generic": "Clonazepam", "drug_class": "Benzodiazepine"},
    {"brand": "Avalide", "generic": "Hydrochlorothiazide/Irbesartan", "drug_class": "Thiazide diuretic/Angiotensin II blocker"},
    {"brand": "Ceftin", "generic": "Cefuroxime", "drug_class": "Cephalosporin antibacterial"},
    {"brand": "Nizoral Topical", "generic": "Ketoconazole", "drug_class": "Antifungal"},
    {"brand": "Lyrica", "generic": "Pregabalin", "drug_class": "Anticonvulsant"},
    {"brand": "Nexium", "generic": "Esomeprazole", "drug_class": "Proton-pump inhibitor"},
    {"brand": "Combivent Respimat", "generic": "Albuterol/Ipratropium", "drug_class": "Beta-2 agonist/Anticholinergic"},
    {"brand": "Niaspan", "generic": "Niacin", "drug_class": "Vitamin B3 / antihyperlipidemic"},
    {"brand": "Uroxatral", "generic": "Alfuzosin", "drug_class": "Alpha-1 blocker"},
    {"brand": "Biaxin", "generic": "Clarithromycin", "drug_class": "Macrolide antibacterial"},
    {"brand": "Zomig", "generic": "Zolmitriptan", "drug_class": "Anti-migraine"},
    {"brand": "Invokana", "generic": "Canagliflozin", "drug_class": "SGLT-2 inhibitor"},
    {"brand": "Saxenda/Victoza", "generic": "Liraglutide", "drug_class": "GLP-1 agonist"},
    {"brand": "Alimta", "generic": "Pemetrexed", "drug_class": "Anticancer"},
    {"brand": "Lotrimin/FungiCURE Pump Spray", "generic": "Clotrimazole", "drug_class": "Antifungal"},
    {"brand": "Avastin", "generic": "Bevacizumab", "drug_class": "Anticancer"},
    {"brand": "Sovaldi", "generic": "Sofosbuvir", "drug_class": "Hepatitis C drug"},
    {"brand": "Gilenya", "generic": "Fingolimod", "drug_class": "Immunomodulator"},
    {"brand": "Epogen", "generic": "Epoetin alfa", "drug_class": "Human erythropoietin"},
    {"brand": "Seroquel", "generic": "Quetiapine", "drug_class": "Antipsychotic"},
    {"brand": "Amaryl", "generic": "Glimepiride", "drug_class": "Antidiabetic"},
    {"brand": "Percocet", "generic": "Acetaminophen/Oxycodone", "drug_class": "Analgesic/Opioid"},
    {"brand": "Sandimmune/Neoral", "generic": "Cyclosporine", "drug_class": "Immunosuppressant"},
    {"brand": "Lantus", "generic": "Insulin glargine", "drug_class": "Long-acting insulin"},
    {"brand": "Cialis", "generic": "Tadalafil", "drug_class": "PDE5 inhibitor"},
    {"brand": "Endep/Elavil/Vanatrip", "generic": "Amitriptyline", "drug_class": "Tricyclic antidepressant"},
    {"brand": "Lopid", "generic": "Gemfibrozil", "drug_class": "Fibrate"},
    {"brand": "Orapred", "generic": "Prednisolone", "drug_class": "Corticosteroid"},
    {"brand": "Advil", "generic": "Ibuprofen", "drug_class": "NSAID"},
    {"brand": "Aceon", "generic": "Perindopril", "drug_class": "ACE inhibitor"},
    {"brand": "Desyrel", "generic": "Trazodone", "drug_class": "Antidepressant/SARI"},
    {"brand": "Actos", "generic": "Pioglitazone", "drug_class": "Thiazolidinedione"},
    {"brand": "Proscar", "generic": "Finasteride", "drug_class": "5-alpha reductase inhibitor"},
    {"brand": "Inbrija/Dopar/Larodopa", "generic": "Levodopa", "drug_class": "Antiparkinsonian"},
    {"brand": "Actonel", "generic": "Risedronate", "drug_class": "Bisphosphonate"},
    {"brand": "Ventolin/ProAir/Proventil", "generic": "Albuterol", "drug_class": "Beta-2 agonist"},
    {"brand": "Ultram", "generic": "Tramadol", "drug_class": "Opioid analgesic"},
    {"brand": "Sonata", "generic": "Zaleplon", "drug_class": "Z-drug/hypnotic"},
    {"brand": "Zebeta", "generic": "Bisoprolol", "drug_class": "Beta-blocker"},
    {"brand": "Zovirax", "generic": "Acyclovir", "drug_class": "Antiviral"},
    {"brand": "Coumadin", "generic": "Warfarin", "drug_class": "Anticoagulant"},
    {"brand": "Luvox", "generic": "Fluvoxamine", "drug_class": "SSRI antidepressant"},
    {"brand": "Plavix", "generic": "Clopidogrel", "drug_class": "Antiplatelet"},
    {"brand": "Vibramycin/Adoxa", "generic": "Doxycycline", "drug_class": "Tetracycline antibacterial"},
    {"brand": "Hyzaar", "generic": "Hydrochlorothiazide/Losartan", "drug_class": "Thiazide diuretic/Angiotensin II blocker"},
    {"brand": "Kytril/Sancuso", "generic": "Granisetron", "drug_class": "Antiemetic"},
    {"brand": "Restoril", "generic": "Temazepam", "drug_class": "Benzodiazepine"},
    {"brand": "Prevacid", "generic": "Lansoprazole", "drug_class": "Proton-pump inhibitor"},
    {"brand": "Augmentin", "generic": "Amoxicillin/Clavulanic acid", "drug_class": "Penicillin/Beta-lactamase inhibitor"},
    {"brand": "Mevacor/Altoprev", "generic": "Lovastatin", "drug_class": "Statin"},
    {"brand": "Cozaar", "generic": "Losartan", "drug_class": "Angiotensin II blocker"},
    {"brand": "Vicodin", "generic": "Hydrocodone/Acetaminophen", "drug_class": "Opioid analgesic combo"},
    {"brand": "Cymbalta", "generic": "Duloxetine", "drug_class": "SNRI antidepressant"},
    {"brand": "Klor-Con", "generic": "Potassium Chloride", "drug_class": "Electrolyte supplement"},
    {"brand": "Toprol XL", "generic": "Metoprolol succinate", "drug_class": "Beta-blocker (ER)"},
    {"brand": "Zantac", "generic": "Ranitidine", "drug_class": "H2 antagonist (withdrawn 2020)"},
    {"brand": "Flomax", "generic": "Tamsulosin", "drug_class": "Alpha-1 blocker"},
    {"brand": "Wellbutrin", "generic": "Bupropion", "drug_class": "Atypical antidepressant"},
    {"brand": "Adderall", "generic": "Amphetamine/Dextroamphetamine", "drug_class": "CNS stimulant"},
    {"brand": "Flexeril", "generic": "Cyclobenzaprine", "drug_class": "Muscle relaxant"},
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
