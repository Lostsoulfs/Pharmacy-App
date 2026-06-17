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
# Automated audit recorded 2026-05-20, but pharmacist signoff is still
# pending; see docs/audits/brand_generic_audit_2026-05-20.md.
# `config.DATA_VERIFIED["brand_generic"]` stays False. brand fields list
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
# Automated audit recorded 2026-05-20, but pharmacist signoff is still
# pending; see docs/audits/clinical_datasets_audit_2026-05-20.md.
# `config.DATA_VERIFIED["vaccines"]` stays False. Schedules change
# annually - re-verify each season. Pharmacist scope of practice varies
# by state and patient age: what a pharmacist may administer, and to
# whom, is set by state law and is NOT captured here.
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
     "ages": "Adults 75 and older; adults 50-74 at increased risk; "
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

# LAW_BULLETS — Mississippi pharmacy law quick-reference for
# technicians.
#
# Automated audit recorded 2026-05-20, but pharmacist signoff is still
# pending; see docs/audits/law_tpr_audit_2026-05-20.md.
# `config.DATA_VERIFIED["law"]` stays False. These bullets are a
# Mississippi-specific training reference. State law moves - re-verify
# against the current Board regulations before any content correction or
# state-track claim.
LAW_BULLETS = [
    {"category": "Technician Registration & Scope",
     "rule": "Every pharmacy technician in Mississippi must register "
             "with the MS Board of Pharmacy. Applicants must be 18 or "
             "older and a high-school graduate or hold a GED."},
    {"category": "Technician Registration & Scope",
     "rule": "Technician registration renews annually. If it is not "
             "renewed by March 31 it goes inactive, and the technician "
             "may perform no technician duties until it is active "
             "again (a $50 late penalty applies)."},
    {"category": "Technician Registration & Scope",
     "rule": "While on duty a technician must wear a visible name tag "
             "identifying them as a technician, and must identify "
             "themselves as a technician on the telephone."},
    {"category": "Technician Registration & Scope",
     "rule": "Technicians work only under the direct supervision of a "
             "registered pharmacist who is physically present."},
    {"category": "Technician Registration & Scope",
     "rule": "Technicians MAY: package and label, pour or place drugs "
             "in containers, reconstitute oral antibiotic liquids, and "
             "enter prescription data — all subject to final "
             "pharmacist verification."},
    {"category": "Technician Registration & Scope",
     "rule": "Technicians MAY NOT: accept new verbal prescriptions, "
             "transfer prescriptions, counsel patients, perform drug "
             "utilization review, give clinical or therapeutic "
             "information, or release medication without final "
             "pharmacist verification."},
    {"category": "Technician Registration & Scope",
     "rule": "Staffing ratio: a pharmacist may supervise up to 3 "
             "technicians doing dispensing tasks (clerical staff, "
             "interns and externs are not counted). Pending HB1675, "
             "effective July 1 2026, raises this to 5:1 for community "
             "pharmacies and 12:1 for closed-door pharmacies, with a "
             "national-certification exception."},
    {"category": "Controlled Substances",
     "rule": "Schedule II prescriptions cannot be refilled — ever."},
    {"category": "Controlled Substances",
     "rule": "Schedule III-V prescriptions allow a maximum of 5 "
             "refills and expire 6 months from the date written, "
             "whichever comes first."},
    {"category": "Controlled Substances",
     "rule": "Mississippi prohibits transferring controlled-substance "
             "prescriptions (C-II through C-V) between pharmacies. "
             "Only non-controlled prescriptions may be transferred, "
             "pharmacist to pharmacist (a shared real-time database "
             "allows one transfer). This is stricter than federal "
             "law."},
    {"category": "Controlled Substances",
     "rule": "A Schedule II prescription may be partially filled; the "
             "balance must be filled within 30 days of the date "
             "written (60 days for long-term-care or terminally-ill "
             "patients)."},
    {"category": "Controlled Substances",
     "rule": "Controlled-substance prescriptions must be transmitted "
             "electronically. Limited exceptions include veterinary "
             "prescriptions, technology failures, out-of-state "
             "pharmacies, and FDA-mandated attachments."},
    {"category": "Controlled Substances",
     "rule": "In a bona fide emergency a prescriber may orally "
             "authorize a Schedule II drug (normally a 48-hour "
             "supply); the written, signed prescription must reach "
             "the pharmacy within 7 days."},
    {"category": "Controlled Substances",
     "rule": "In Mississippi, ephedrine and pseudoephedrine are "
             "Schedule III controlled substances, exempt only when "
             "sold over the counter within state quantity and "
             "tracking limits."},
    {"category": "Controlled Substances",
     "rule": "Pseudoephedrine/ephedrine OTC sales: kept behind the "
             "counter, photo ID required, and logged in NPLEx before "
             "the sale. Limits are 3.6 g per day and 7.2 g per 30 "
             "days per purchaser."},
    {"category": "Prescription Monitoring Program",
     "rule": "Any entity dispensing controlled substances in or into "
             "Mississippi must report to the PMP within 24 hours or "
             "the next business day; a 'zero report' is required on "
             "days with no controlled dispensing."},
    {"category": "Prescription Monitoring Program",
     "rule": "Gabapentin is a specified non-controlled substance in "
             "Mississippi — every gabapentin dispensing to a "
             "Mississippi resident must be reported to the PMP."},
    {"category": "Prescription Monitoring Program",
     "rule": "All controlled-substance records sent to the PMP must "
             "include the prescriber's valid DEA number."},
    {"category": "Valid Prescriptions",
     "rule": "A valid prescription needs: patient name and address; "
             "prescriber name, address, and (for controlled "
             "substances) DEA number; date of issuance; drug name, "
             "strength, dosage form, and quantity; directions and "
             "refills authorized; and the prescriber's manual "
             "signature (stamps are invalid) or a digital signature."},
    {"category": "Valid Prescriptions",
     "rule": "A prescription becomes invalid 30 days after the "
             "prescriber-patient relationship ends. A "
             "controlled-substance prescription based only on an "
             "online questionnaire is not valid."},
    {"category": "Emergency Dispensing & Counseling",
     "rule": "A pharmacist may dispense a one-time emergency supply "
             "of up to 72 hours of a non-controlled maintenance "
             "medication when the prescriber cannot be reached, and "
             "must notify the prescriber within 7 working days."},
    {"category": "Emergency Dispensing & Counseling",
     "rule": "Before dispensing, the pharmacist reviews the patient "
             "profile for interactions and appropriateness and must "
             "offer to counsel the patient (in writing, with a "
             "toll-free number, for mailed prescriptions). A "
             "documented refusal ends the obligation."},
    {"category": "Records & Inventory",
     "rule": "Retention: controlled-substance acquisition records "
             "(DEA Form 222, invoices) 2 years; disposition records "
             "(filled prescriptions, DEA Form 41) 6 years; "
             "non-controlled prescriptions 12 months. Schedule II "
             "records are filed completely separately."},
    {"category": "Records & Inventory",
     "rule": "A complete physical controlled-substance inventory is "
             "required annually on or about May 1 (no later than "
             "May 15), and at any change of ownership, change of "
             "pharmacist-in-charge, or closure."},
    {"category": "Records & Inventory",
     "rule": "A suspected loss or theft of controlled substances must "
             "be reported to the Board immediately by phone, with a "
             "written report and a 48-hour physical inventory within "
             "15 days."},
]

# TPR_CODES — third-party (insurance) claim rejection quick-reference.
#
# Automated audit recorded 2026-05-20, but pharmacist signoff is still
# pending; see docs/audits/law_tpr_audit_2026-05-20.md.
# `config.DATA_VERIFIED["tpr"]` stays False. Codes a technician resolves
# directly unless the action notes a pharmacist.
TPR_CODES = [
    {"code": "01 — Missing/Invalid BIN",
     "meaning": "The 6-digit payer routing number is wrong or "
                "mistyped.",
     "action": "Get the current insurance card, correct the BIN, and "
               "resubmit."},
    {"code": "04 — Missing/Invalid PCN",
     "meaning": "The Processor Control Number is missing or mistyped.",
     "action": "Re-enter the exact PCN from the card and resubmit."},
    {"code": "07 — Missing/Invalid Cardholder ID",
     "meaning": "The member ID is mistyped or changed after a plan "
                "renewal or merger.",
     "action": "Verify the ID against the physical card or an "
               "eligibility check, update it, and resubmit."},
    {"code": "19 — Missing/Invalid Days' Supply",
     "meaning": "The days' supply does not match the sig — common on "
                "eye drops, insulin, inhalers, and topicals.",
     "action": "Recalculate the days' supply from the directions, "
               "correct it, and resubmit."},
    {"code": "21 / 54 — Invalid or Non-Matched NDC",
     "meaning": "The drug code is mistyped, discontinued, or not on "
                "file with the plan.",
     "action": "Verify the NDC on the stock bottle. If discontinued, "
               "dispense and bill a covered equivalent."},
    {"code": "22 — Missing/Invalid DAW Code",
     "meaning": "A brand drug was billed without the correct "
                "product-selection (DAW) code.",
     "action": "Check the prescription for 'brand medically "
               "necessary' and enter the correct DAW code."},
    {"code": "25 / 56 — Missing or Non-Matched Prescriber ID",
     "meaning": "The prescriber NPI is missing, mistyped, or not "
                "enrolled with the plan.",
     "action": "Verify the prescriber's NPI and correct it in the "
               "provider file."},
    {"code": "41 — Submit to Other Processor / Primary",
     "meaning": "The patient has another insurance that must be "
                "billed first.",
     "action": "Bill the primary plan, then submit the secondary "
               "claim with the correct Other Coverage Code."},
    {"code": "65 — Patient Not Covered",
     "meaning": "The policy is inactive or has not yet reached its "
                "effective date.",
     "action": "Verify name and date of birth, run an eligibility "
               "check, update the coverage, and resubmit."},
    {"code": "68 — Filled After Coverage Expired",
     "meaning": "The date of service is after the policy ended.",
     "action": "Get the patient's new insurance information and "
               "rebill."},
    {"code": "70 / MR — Product Not Covered / Not on Formulary",
     "meaning": "The drug is excluded from the plan's formulary.",
     "action": "Find a preferred alternative on the formulary, or "
               "start a prior authorization."},
    {"code": "75 — Prior Authorization Required",
     "meaning": "The plan needs the prescriber to document medical "
                "necessity before it will cover the drug.",
     "action": "Initiate an electronic prior authorization (ePA) and "
               "notify the patient of the delay."},
    {"code": "76 — Plan Limitations Exceeded",
     "meaning": "The quantity or days' supply exceeds the plan's "
                "limit.",
     "action": "Adjust the quantity or days' supply to the limit, or "
               "contact the prescriber."},
    {"code": "79 — Refill Too Soon",
     "meaning": "A refill was requested before enough of the prior "
                "fill is used (about 75%, near 90% for opioids).",
     "action": "Tell the patient the next allowed fill date. A "
               "vacation override uses a submission clarification "
               "code."},
    {"code": "88 — DUR Reject (clinical)",
     "meaning": "A clinical safety alert — drug interaction, "
                "therapeutic duplication, or a dose concern.",
     "action": "PHARMACIST must clinically review and resolve it "
               "with DUR codes before the claim can be resubmitted."},
]
