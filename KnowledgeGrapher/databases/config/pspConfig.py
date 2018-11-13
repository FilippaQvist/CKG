###### PhosphoSitePlus Database ########
#Registration necessary to download files, automatic download not possible

modifications = {"ac":"MOD:00394",
                 "m1":"MOD:00599",
                 "m2":"MOD:00429",
                 "m3":"MOD:00430",
                 "me":"MOD:00427",
                 "ga":"MOD:00563",
                 "gl":"MOD:00448",
                 "sm":"MOD:01149",
                 "ub":"MOD:01148",
                 "p":"MOD:00696",
                 "ox":"MOD:00256",
                 "gly":"MOD:00767"}

annotation_files = {("disease", "associated_with"):"Disease-associated_sites.gz",
         ("substrate", "is_substrate_of"):"Kinase_Substrate_Dataset.gz",
         ("biological_process", "associated_with"):"Regulatory_sites.gz"}

site_files = ["Acetylation_site_dataset.gz",
              "Methylation_site_dataset.gz",
              "Phosphorylation_site_dataset.gz",
              "Sumoylation_site_dataset.gz",
              "Ubiquitination_site_dataset.gz",
              "O-GalNAc_site_dataset.gz",
              "O-GlcNAc_site_dataset.gz"
              ]

entities_header = ["ID", "type", "protein", "sequence_window", "position", "residue"]
rel_headers = {"disease":['START_ID', 'END_ID', 'TYPE', 'evidence_type','score','source', 'publications'],
         "substrate":['START_ID', 'END_ID', 'TYPE', 'evidence_type','score','source'],
         "biological_process":['START_ID', 'END_ID', 'TYPE', 'evidence_type','score','source', 'publications', 'action']}

