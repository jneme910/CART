/****** Script for SelectTopNRows command from SSMS  ******/
SELECT   Y2019.[areaname]
      ,Y2019.[areasymbol]
      ,Y2019.[musym]
      ,Y2019.[mukey]
      ,Y2019.[muname]
     -- ,Y2019.[datestamp]
      ,CASE WHEN Y2019.[Agricultural_Organic_Soil_Subsidence_Severe_subsidence] !=Y2020.[Agricultural_Organic_Soil_Subsidence_Severe_subsidence] THEN 'diff' END AS severe_subsidence
      ,CASE WHEN Y2019.[Agricultural_Organic_Soil_Subsidence_Moderate_subsidence] != Y2020.[Agricultural_Organic_Soil_Subsidence_Moderate_subsidence]THEN 'diff' END AS  subsidence_mod
      ,CASE WHEN Y2019.[Organic_Matter_Depletion_OM_depletion_high]!= Y2020.[Organic_Matter_Depletion_OM_depletion_high] THEN 'diff' END AS OM_dep_high
      ,CASE WHEN Y2019.[Organic_Matter_Depletion_OM_depletion_moderately_high]!= Y2020.[Organic_Matter_Depletion_OM_depletion_moderately_high] THEN 'diff' END AS OM_dep_mod_high
      ,CASE WHEN Y2019.[Organic_Matter_Depletion_OM_depletion_moderate]!=Y2020.[Organic_Matter_Depletion_OM_depletion_moderate] THEN 'diff' END AS OM_dep_mod
      ,CASE WHEN Y2019.[Soil_Susceptibility_to_Compaction_High]!=Y2020.[Soil_Susceptibility_to_Compaction_High] THEN 'diff' END AS compact_high
      ,CASE WHEN Y2019.[Soil_Susceptibility_to_Compaction_Medium]!= Y2020.[Soil_Susceptibility_to_Compaction_Medium] THEN 'diff' END AS compact_med
     , CASE WHEN Y2019.[Suitability_for_Aerobic_Soil_Organisms_Not_favorable]!= Y2020.[Suitability_for_Aerobic_Soil_Organisms_Not_favorable] THEN 'diff' END AS organism_not_fav
      ,CASE WHEN Y2019.[Suitability_for_Aerobic_Soil_Organisms_Somewhat_favorable]!=Y2020.[Suitability_for_Aerobic_Soil_Organisms_Somewhat_favorable] THEN 'diff' END AS
      organism_som_fav
	  ,CASE WHEN Y2019.[Surface_Salt_Concentration_High_surface_salinization_risk_or_already_saline]!=Y2020.[Surface_Salt_Concentration_High_surface_salinization_risk_or_already_saline]THEN 'diff' END AS salt_high 
      ,CASE WHEN Y2019.[Surface_Salt_Concentration_Surface_salinization_risk]!=Y2020.[Surface_Salt_Concentration_Surface_salinization_risk]THEN 'diff' END AS salt_risk

  FROM [Jason_nemecek_email].[dbo].[2019_SSURGO_SH_INTERP_CLASS_DATA] AS Y2019
  INNER JOIN [Jason_nemecek_email].[dbo].[2020_SSURGO_SH_INTERP_CLASS_DATA] AS Y2020 ON Y2020.mukey=Y2019.mukey

  AND CASE WHEN Y2019.[Agricultural_Organic_Soil_Subsidence_Severe_subsidence] !=Y2020.[Agricultural_Organic_Soil_Subsidence_Severe_subsidence] THEN 1
      WHEN Y2019.[Agricultural_Organic_Soil_Subsidence_Moderate_subsidence]!= Y2020.[Agricultural_Organic_Soil_Subsidence_Moderate_subsidence] THEN 1
      WHEN Y2019.[Organic_Matter_Depletion_OM_depletion_high] !=Y2020.[Organic_Matter_Depletion_OM_depletion_high]THEN 1
      WHEN Y2019.[Organic_Matter_Depletion_OM_depletion_moderately_high]!=Y2020.[Organic_Matter_Depletion_OM_depletion_moderately_high]THEN 1
      WHEN Y2019.[Organic_Matter_Depletion_OM_depletion_moderate]!=Y2020.[Organic_Matter_Depletion_OM_depletion_moderate]THEN 1
      WHEN Y2019.[Soil_Susceptibility_to_Compaction_High]!=Y2020.[Soil_Susceptibility_to_Compaction_High]THEN 1
      WHEN Y2019.[Soil_Susceptibility_to_Compaction_Medium]!=Y2020.[Soil_Susceptibility_to_Compaction_Medium]THEN 1
       WHEN Y2019.[Suitability_for_Aerobic_Soil_Organisms_Not_favorable]!=Y2020.[Suitability_for_Aerobic_Soil_Organisms_Not_favorable]THEN 1
      WHEN Y2019.[Suitability_for_Aerobic_Soil_Organisms_Somewhat_favorable]!=Y2020.[Suitability_for_Aerobic_Soil_Organisms_Somewhat_favorable]THEN 1
      WHEN Y2019.[Surface_Salt_Concentration_High_surface_salinization_risk_or_already_saline]!=Y2020.[Surface_Salt_Concentration_High_surface_salinization_risk_or_already_saline] THEN 1 
      WHEN Y2019.[Surface_Salt_Concentration_Surface_salinization_risk]!=Y2020.[Surface_Salt_Concentration_Surface_salinization_risk] THEN 1  ELSE 2 END = 1