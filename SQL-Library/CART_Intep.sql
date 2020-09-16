--
SET STATISTICS IO ON 

USE sdmONLINE
go

DROP TABLE IF EXISTS #map_main;
DROP TABLE IF EXISTS #map_main2;
DROP TABLE IF EXISTS #map_main5;
DROP TABLE IF EXISTS #interp;

--Define the area
DECLARE @area VARCHAR(20);
DECLARE @area_type INT ;
DECLARE @domc INT ;

-- Soil Data Access
--~DeclareChar(@area,20)~  -- Used for Soil Data Access
--~DeclareINT(@area_type)~ 
--~DeclareINT(@area_type)~ 
-- End soil data access
SELECT @area= 'WI025'; --Enter State Abbreviation or Soil Survey Area i.e. WI or WI025


SELECT @area_type = LEN (@area); --determines number of characters of area 2-State, 5- Soil Survey Area


CREATE TABLE #map_main
   ( areaname VARCHAR (255), 
    areasymbol VARCHAR (20),
    musym VARCHAR (20), 
	mukey INT, 
	muname VARCHAR (250), 
	compname VARCHAR (250), 
	comppct_r INT,
	cokey INT, 
	
	[mrulename] VARCHAR (255), 
	interphrc VARCHAR (255),
		major_mu_pct_sum INT, 
	datestamp VARCHAR(32), 
	)



/* 
Surface Salt Concentration
Soil Susceptibility to Compaction
Organic Matter Depletion
Agricultural Organic Soil Subsidence
Suitability for Aerobic Soil Organisms
---
SOH - Soil Susceptibility to Compaction
SOH - Concentration of Salts- Soil Surface
SOH - Agricultural Organic Soil Subsidence
SOH -  Suitability for Aerobic Soil Organisms
SOH - Organic Matter Depletion
*/
--Queries the map unit and legend
--Link Main
INSERT INTO #map_main (areaname, areasymbol, musym, mukey, muname, compname, comppct_r, cokey, [mrulename], interphrc,  major_mu_pct_sum,  datestamp )
 SELECT l.areaname, l.areasymbol, musym, mu.mukey, muname, compname, comppct_r, c.cokey, 
[mrulename], interphrc,

(SELECT SUM (CCO.comppct_r) 
FROM mapunit AS MM2
INNER JOIN component AS CCO ON CCO.mukey = MM2.mukey AND mu.mukey = MM2.mukey AND majcompflag = 'Yes') AS  major_mu_pct_sum,
CONCAT ([SC].[areasymbol] , ' ' , FORMAT ( [SC].[saverest], 'dd-MM-yy')) AS datestamp


 FROM sacatalog SC 
 INNER JOIN legend  AS l ON l.areasymbol = SC.areasymbol AND SC.areasymbol <> 'US'
 INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey  --CASE WHEN @area_type = 2 THEN LEFT (l.areasymbol, 2) ELSE l.areasymbol END = @area
 INNER JOIN  component AS c ON c.mukey = mu.mukey AND majcompflag = 'yes'
 INNER JOIN cointerp ON c.cokey = cointerp.cokey AND ruledepth = 0 AND mrulename IN 
 ('SOH - Soil Susceptibility to Compaction', 'SOH - Soil Susceptibility to Compaction',
'SOH - Concentration of Salts- Soil Surface',
'SOH - Agricultural Organic Soil Subsidence',
'SOH -  Suitability for Aerobic Soil Organisms',
'SOH - Organic Matter Depletion')
 ORDER BY l.areasymbol, musym, muname, mu.mukey



CREATE TABLE #map_main2
   ( areaname VARCHAR (255), 
    areasymbol VARCHAR (20),
    musym VARCHAR (20), 
	mukey INT, 
	muname VARCHAR (250), 
	compname VARCHAR (250), 
	comppct_r INT,
	cokey INT, 
	major_mu_pct_sum INT, 
	adj_comp_pct REAL,
	[mrulename] VARCHAR (255), 
	interphrc VARCHAR (255),
	
	datestamp VARCHAR(32)
	)


--Table 2
INSERT INTO #map_main2 (areaname, areasymbol, musym, mukey, muname, compname, comppct_r, cokey, major_mu_pct_sum, adj_comp_pct, [mrulename], interphrc,  datestamp )

SELECT areaname, areasymbol, musym, mukey, muname, compname, comppct_r,  #map_main.cokey, major_mu_pct_sum,  LEFT (ROUND ((1.0 * comppct_r / NULLIF(major_mu_pct_sum, 0)),2),4) AS adj_comp_pct, [mrulename], interphrc, datestamp
FROM #map_main


CREATE TABLE #map_main5
   ( areaname VARCHAR (255), 
    areasymbol VARCHAR (20),
    musym VARCHAR (20), 
	mukey INT, 
	muname VARCHAR (250), 
	compname VARCHAR (250), 
	comppct_r INT,
	cokey INT, 
	major_mu_pct_sum INT, 
	adj_comp_pct REAL,
	[mrulename_interphrc] VARCHAR (555), 
	datestamp VARCHAR(32) 
	)


--Table 3
INSERT INTO #map_main5 (areaname, areasymbol, musym, mukey, muname, compname, comppct_r, cokey, major_mu_pct_sum, adj_comp_pct, mrulename_interphrc, datestamp )
SELECT areaname, areasymbol, musym, mukey, muname, compname, comppct_r, #map_main2.cokey, major_mu_pct_sum, adj_comp_pct, 
 REPLACE(REPLACE (CONCAT ([mrulename], '-', interphrc), 'SOH -  ', ''), 'SOH - ', '')  AS [mrulename_interphrc] , [datestamp]
FROM #map_main2


CREATE TABLE #interp ( areaname VARCHAR (255), 
    areasymbol VARCHAR (20),
    musym VARCHAR (20), 
	mukey INT, 
	muname VARCHAR (250),  
	[datestamp] VARCHAR(32),
[Agricultural Organic Soil Subsidence-Severe subsidence] SMALLINT,
[Agricultural Organic Soil Subsidence-Moderate subsidence] SMALLINT,
[Organic Matter Depletion-OM depletion high] SMALLINT,
[Organic Matter Depletion-OM depletion moderately high] SMALLINT,
[Organic Matter Depletion-OM depletion moderate] SMALLINT,
[Soil Susceptibility to Compaction-High] SMALLINT,
[Soil Susceptibility to Compaction-Medium] SMALLINT,
[Suitability for Aerobic Soil Organisms-Not favorable] SMALLINT,
[Suitability for Aerobic Soil Organisms-Somewhat favorable] SMALLINT,
[Surface Salt Concentration-High surface salinization risk or already saline] SMALLINT,
[Surface Salt Concentration-Surface salinization risk] SMALLINT 
)
 INSERT INTO #interp  (
areaname, areasymbol, musym, mukey, muname, [datestamp],
[Agricultural Organic Soil Subsidence-Severe subsidence],
[Agricultural Organic Soil Subsidence-Moderate subsidence],
[Organic Matter Depletion-OM depletion high],
[Organic Matter Depletion-OM depletion moderately high],
[Organic Matter Depletion-OM depletion moderate],
[Soil Susceptibility to Compaction-High],
[Soil Susceptibility to Compaction-Medium],
[Suitability for Aerobic Soil Organisms-Not favorable],
[Suitability for Aerobic Soil Organisms-Somewhat favorable],
[Surface Salt Concentration-High surface salinization risk or already saline],
[Surface Salt Concentration-Surface salinization risk]
 )
 

 SELECT * FROM 
 (
 SELECT   areaname, areasymbol, musym, mukey, muname, [datestamp], [mrulename_interphrc] 

 FROM #map_main5

 ) #r
 PIVOT (
 COUNT (mrulename_interphrc)

   FOR [mrulename_interphrc] IN (
[Agricultural Organic Soil Subsidence-Severe subsidence],
[Agricultural Organic Soil Subsidence-Moderate subsidence],
[Organic Matter Depletion-OM depletion high],
[Organic Matter Depletion-OM depletion moderately high],
[Organic Matter Depletion-OM depletion moderate],
[Soil Susceptibility to Compaction-High],
[Soil Susceptibility to Compaction-Medium],
[Suitability for Aerobic Soil Organisms-Not favorable],
[Suitability for Aerobic Soil Organisms-Somewhat favorable],
[Surface Salt Concentration-High surface salinization risk or already saline],
[Surface Salt Concentration-Surface salinization risk]
)

) AS #interp_pivot_table GROUP BY areaname, areasymbol, musym, mukey, muname, [datestamp], [Agricultural Organic Soil Subsidence-Severe subsidence],
[Agricultural Organic Soil Subsidence-Moderate subsidence],
[Organic Matter Depletion-OM depletion high],
[Organic Matter Depletion-OM depletion moderately high],
[Organic Matter Depletion-OM depletion moderate],
[Soil Susceptibility to Compaction-High],
[Soil Susceptibility to Compaction-Medium],
[Suitability for Aerobic Soil Organisms-Not favorable],
[Suitability for Aerobic Soil Organisms-Somewhat favorable],
[Surface Salt Concentration-High surface salinization risk or already saline],
[Surface Salt Concentration-Surface salinization risk];


SELECT areaname, areasymbol, musym, mukey, muname, [datestamp], 
[Agricultural Organic Soil Subsidence-Severe subsidence],
[Agricultural Organic Soil Subsidence-Moderate subsidence],
[Organic Matter Depletion-OM depletion high],
[Organic Matter Depletion-OM depletion moderately high],
[Organic Matter Depletion-OM depletion moderate],
[Soil Susceptibility to Compaction-High],
[Soil Susceptibility to Compaction-Medium],
[Suitability for Aerobic Soil Organisms-Not favorable],
[Suitability for Aerobic Soil Organisms-Somewhat favorable],
[Surface Salt Concentration-High surface salinization risk or already saline],
[Surface Salt Concentration-Surface salinization risk]
FROM #interp


DROP TABLE IF EXISTS #map_main;
DROP TABLE IF EXISTS #map_main2;
DROP TABLE IF EXISTS #map_main5;
DROP TABLE IF EXISTS #map_main6;
DROP TABLE IF EXISTS #interp;