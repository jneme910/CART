# Soil Organic Carbon Stock Weighted Mean
[SQL Script Soil Organic Carbon Stock (Soil Data Access SQL Script)](https://github.com/ncss-tech/sda-lib/blob/master/SQL-Library/SDA_SOC_Weighted_Mean_Soil_Organic_Carbon_Stock.sql) Soil organic carbon stock estimate (SOC) in total soil profile (0 cm to the any predetermined depth up to the depth  of the soil profile). The concentration of organic carbon present in the soil expressed in metric tons (Mg) per hectare for the total reported soil profile depth. NULL values are presented where data are incomplete or not available.

list:
   * Uses all components with horizon data.
   * Does not calculate component SOC below the following component restrictions:
   * Lithic bedrock, Paralithic bedrock, Densic bedrock, Fragipan, Duripan, Sulfuric
   * soc =  ( (hzT * ( ( om / 1.724 ) * db3 )) / 100.0 ) * ((100.0 - fragvol) / 100.0)
   * Areasymbol listed twice in the script for Entire SSURGO use "areasymbol  <> 'US'" OR STATSGO use "areasymbol = 'US'"
   
   
   ### Main Table
   ```SQL 
   SELECT areasymbol, areaname, mapunit.mukey, mapunit.mukey AS mulink, mapunit.musym, 
   nationalmusym, mapunit.muname, mukind, muacres
INTO #main
FROM legend
INNER JOIN mapunit on legend.lkey=mapunit.lkey AND mapunit.mukey = 2809839
INNER JOIN muaggatt AS mt1 on mapunit.mukey=mt1.mukey
--AND legend.areasymbol = 'WI025'
```

|areasymbol|	areaname|	mukey|	mulink|	musym|	nationalmusym|	muname|	mukind	|muacres|
| ----- | --------- | --------- | --------- | --------- |--------- |--------- |--------- |--------- |
|WI025|	Dane County, Wisconsin|	2809839|	2809839|	161B2|	1q9nn|	Fivepoints silt loam, 2 to 6 percent slopes, moderately eroded|	Consociation|	113|


### acpf Table
```SQL
SELECT
-- grab survey area data
LEFT((areasymbol), 2) AS state,
 l.areasymbol,
 l.areaname,
(SELECT SUM (DISTINCT comppct_r) FROM mapunit  AS mui3  INNER JOIN component AS cint3 ON cint3.mukey=mui3.mukey INNER JOIN chorizon AS chint3 ON chint3.cokey=cint3.cokey AND cint3.cokey = c.cokey GROUP BY chint3.cokey) AS sum_comp,
--grab map unit level information

 mu.mukey,
 mu.musym,

--grab component level information

 c.majcompflag,
 c.comppct_r,
 c.compname,
 compkind,
 localphase,
 slope_l,
 slope_r,
 slope_h,
(SELECT CAST(MIN(resdept_r) AS INTEGER) FROM component LEFT OUTER JOIN corestrictions ON component.cokey = corestrictions.cokey WHERE component.cokey = c.cokey AND reskind  IS NOT NULL) AS restrictiondepth,
(SELECT CASE WHEN MIN (resdept_r) IS NULL THEN 200 ELSE CAST (MIN (resdept_r) AS INT) END FROM component LEFT OUTER JOIN corestrictions ON component.cokey = corestrictions.cokey WHERE component.cokey = c.cokey AND reskind IS NOT NULL) AS restrictiodepth,
(SELECT TOP 1  reskind  FROM component LEFT OUTER JOIN corestrictions ON component.cokey = corestrictions.cokey WHERE component.cokey = c.cokey AND corestrictions.reskind IN ('Lithic bedrock','Duripan', 'Densic bedrock', 'Paralithic bedrock', 'Fragipan', 'Natric', 'Ortstein', 'Permafrost', 'Petrocalcic', 'Petrogypsic')
AND reskind IS NOT NULL ORDER BY resdept_r) AS TOPrestriction, c.cokey,

---begin selection of horizon properties
 hzname,
 hzdept_r,
 hzdepb_r,
 CASE WHEN (hzdepb_r-hzdept_r) IS NULL THEN 0 ELSE CAST((hzdepb_r-hzdept_r) AS INT) END AS thickness,  

  om_r, dbthirdbar_r, 
  (SELECT CASE WHEN SUM (cf.fragvol_r) IS NULL THEN 0 ELSE CAST (SUM(cf.fragvol_r) AS INT) END FROM chfrags cf WHERE cf.chkey = ch.chkey) as fragvol,
brockdepmin,
  texture,
  ch.chkey
INTO #acpf
FROM legend  AS l
INNER JOIN mapunit AS mu ON mu.lkey = l.lkey 
--AND l.areasymbol like 'WI025'
AND mu.mukey = 2809839
INNER JOIN muaggatt AS  mt on mu.mukey=mt.mukey
INNER JOIN component AS  c ON c.mukey = mu.mukey 
INNER JOIN chorizon AS ch ON ch.cokey = c.cokey and CASE WHEN hzdept_r IS NULL THEN 2 
WHEN om_r IS NULL THEN 2 
WHEN om_r = 0 THEN 2 
WHEN dbthirdbar_r IS NULL THEN 2
WHEN dbthirdbar_r = 0 THEN 2
ELSE 1 END = 1
INNER JOIN chtexturegrp ct ON ch.chkey=ct.chkey and ct.rvindicator = 'yes'
ORDER by l.areasymbol, mu.musym, hzdept_r 
```

|state|areasymbol|areaname|sum_comp|mukey|musym|majcompflag|comppct_r|compname|compkind|localphase|slope_l|slope_r|slope_h|restrictiondepth|restrictiodepth|TOPrestriction|cokey|hzname|hzdept_r|hzdepb_r|thickness|om_r|dbthirdbar_r|fragvol|brockdepmin|texture|chkey|
|-----|----------|--------|--------|-----|-----|-----------|---------|--------|--------|----------|-------|-------|-------|----------------|---------------|--------------|-----|------|--------|--------|---------|----|------------|-------|-----------|-------|-----|
|WI|WI025|Dane County, Wisconsin|90|2809839|161B2|Yes|90|Fivepoints|Series||2|4|6|89|89|Lithic bedrock|13906974|Ap|0|18|18|1.5|1.4|5|89|SIL|39904473|
|WI|WI025|Dane County, Wisconsin|10|2809839|161B2|No|10|NewGlarus|Series||2|4|6|114|114|Lithic bedrock|13906975|Ap|0|23|23|1.5|1.4|3|89|SIL|39904478|
|WI|WI025|Dane County, Wisconsin|90|2809839|161B2|Yes|90|Fivepoints|Series||2|4|6|89|89|Lithic bedrock|13906974|Bt1|18|25|7|0.5|1.5|5|89|SICL|39904470|
|WI|WI025|Dane County, Wisconsin|10|2809839|161B2|No|10|NewGlarus|Series||2|4|6|114|114|Lithic bedrock|13906975|BE|23|33|10|0.25|1.4|3|89|SIL|39904479|
|WI|WI025|Dane County, Wisconsin|90|2809839|161B2|Yes|90|Fivepoints|Series||2|4|6|89|89|Lithic bedrock|13906974|2Bt2|25|48|23|0.25|1.4|11|89|C|39904471|
|WI|WI025|Dane County, Wisconsin|10|2809839|161B2|No|10|NewGlarus|Series||2|4|6|114|114|Lithic bedrock|13906975|Bt1|33|58|25|0.25|1.5|5|89|SICL|39904480|
|WI|WI025|Dane County, Wisconsin|90|2809839|161B2|Yes|90|Fivepoints|Series||2|4|6|89|89|Lithic bedrock|13906974|3Bt3|48|89|41|0.25|1.5|45|89|CNV-L|39904472|
|WI|WI025|Dane County, Wisconsin|10|2809839|161B2|No|10|NewGlarus|Series||2|4|6|114|114|Lithic bedrock|13906975|2Bt2|58|89|31|0.25|1.4|11|89|C|39904475|
|WI|WI025|Dane County, Wisconsin|10|2809839|161B2|No|10|NewGlarus|Series||2|4|6|114|114|Lithic bedrock|13906975|3Bt3|89|114|25|0.25|1.5|45|89|CNV-L|39904476|



### MUACPF Table
```SQL
---Sums the Component Percent and eliminate duplicate values by cokey
SELECT mukey, cokey,  SUM (DISTINCT sum_comp) AS sum_comp2
INTO #muacpf
FROM #acpf AS acpf2
WHERE acpf2.cokey=cokey
GROUP BY mukey, cokey
```
|mukey|cokey|sum_comp2|
|-----|-----|---------|
|2809839|13906974|90|
|2809839|13906975|10|



### MUACPF2 Table
```SQL
---Sums the component percent in a map unit
SELECT mukey, cokey, sum_comp2,  SUM (sum_comp2) over(partition by #muacpf.mukey ) AS sum_comp3 --, SUM (sum_comp2) AS sum_comp3
INTO #muacpf2
FROM #muacpf
GROUP BY mukey, cokey, sum_comp2
```
|mukey|cokey|sum_comp2|sum_comp3|
|-----|-----|---------|---------|
|2809839|13906974|90|100|
|2809839|13906975|10|100|




### hortopdepth Table
```SQL
---grab top depth for the mineral soil and will use it later to get mineral surface properties
SELECT compname, cokey, MIN(hzdept_r) AS min_t
INTO #hortopdepth
FROM #acpf
WHERE texture NOT LIKE '%PM%' and texture NOT LIKE '%DOM' and texture NOT LIKE '%MPT%' AND texture NOT LIKE '%MUCK' AND texture NOT LIKE '%PEAT%'
GROUP BY compname, cokey
```
|mpname|cokey|min_t|
|------|-----|-----|
|Fivepoints|13906974|0|
|NewGlarus|13906975|0|



### acpf2 Table
```SQL 
---combine the mineral surface to grab surface mineral properties

SELECT #hortopdepth.cokey,
hzname,
hzdept_r,
hzdepb_r,
thickness,
texture AS texture_surf,
om_r AS om_surf,
dbthirdbar_r AS db_surf, 
fragvol AS frag_surf, 
chkey
INTO #acpf2
FROM #hortopdepth
INNER JOIN #acpf on #hortopdepth.cokey=#acpf.cokey AND #hortopdepth.min_t = #acpf.hzdept_r
ORDER BY #hortopdepth.cokey, hzname
```
|cokey|hzname|hzdept_r|hzdepb_r|thickness|texture_surf|om_surf|db_surf|frag_surf|chkey|
|-----|------|--------|--------|---------|------------|-------|-------|---------|-----|
|13906974|	Ap|	0|	18|	18|	SIL|	1.5|	1.4	|5|	39904473|
13906975|	Ap|	0|	23|	23|	SIL|	1.5|	1.4|	3|	39904478|



### acpfhzn Table
```SQL
SELECT
mukey,
cokey,
hzname,
restrictiodepth, 
hzdept_r,
hzdepb_r,
CASE WHEN (hzdepb_r-hzdept_r) IS NULL THEN 0 ELSE CAST ((hzdepb_r-hzdept_r) AS INT) END AS thickness,
texture,
CASE WHEN dbthirdbar_r IS NULL THEN 0 ELSE dbthirdbar_r  END AS dbthirdbar_r, 
CASE WHEN fragvol IS NULL THEN 0 ELSE fragvol  END AS fragvol, 
CASE when om_r IS NULL THEN 0 ELSE om_r END AS om_r,
chkey
INTO #acpfhzn
FROM #acpf
```
|mukey|cokey|hzname|restrictiodepth|hzdept_r|hzdepb_r|thickness|texture|dbthirdbar_r|fragvol|om_r|chkey|
|-----|-----|------|---------------|--------|--------|---------|-------|------------|-------|----|-----|
|2809839|13906974|Bt1|89|18|25|7|SICL|1.5|5|0.5|39904470|
|2809839|13906974|2Bt2|89|25|48|23|C|1.4|11|0.25|39904471|
|2809839|13906974|3Bt3|89|48|89|41|CNV-L|1.5|45|0.25|39904472|
|2809839|13906974|Ap|89|0|18|18|SIL|1.4|5|1.5|39904473|
|2809839|13906975|2Bt2|114|58|89|31|C|1.4|11|0.25|39904475|
|2809839|13906975|3Bt3|114|89|114|25|CNV-L|1.5|45|0.25|39904476|
|2809839|13906975|Ap|114|0|23|23|SIL|1.4|3|1.5|39904478|
|2809839|13906975|BE|114|23|33|10|SIL|1.4|3|0.25|39904479|
|2809839|13906975|Bt1|114|33|58|25|SICL|1.5|5|0.25|39904480|


### SOC Table
```SQL
--- depth ranges for SOC ----
SELECT hzname, chkey, comppct_r, hzdept_r, hzdepb_r, thickness,
CASE  WHEN hzdept_r < 150 then hzdept_r ELSE 0 END AS InRangeTop, 
CASE  WHEN hzdepb_r <= 150 THEN hzdepb_r WHEN hzdepb_r > 150 and hzdept_r < 150 THEN 150 ELSE 0 END AS InRangeBot,

CASE  WHEN hzdept_r < 30 then hzdept_r ELSE 0 END AS InRangeTop_0_30, 
CASE  WHEN hzdepb_r <= 30  THEN hzdepb_r WHEN hzdepb_r > 30  and hzdept_r < 30 THEN 30  ELSE 0 END AS InRangeBot_0_30,


-------CASE  WHEN hzdept_r < 50 then hzdept_r ELSE 20 END AS InRangeTop_20_50, 
--------CASE  WHEN hzdepb_r <= 50  THEN hzdepb_r WHEN hzdepb_r > 50  and hzdept_r < 50 THEN 50  ELSE 20 END AS InRangeBot_20_50,

--CASE    WHEN hzdept_r < 20 THEN 20
--		WHEN hzdept_r < 50 then hzdept_r ELSE 20 END AS InRangeTop_20_50,
		
--CASE    WHEN hzdepb_r < 20 THEN 20
--WHEN hzdepb_r <= 50 THEN hzdepb_r  WHEN hzdepb_r > 50 and hzdept_r < 50 THEN 50 ELSE 20 END AS InRangeBot_20_50,

CASE    WHEN hzdepb_r < 20 THEN 0
WHEN hzdept_r >50 THEN 0 
WHEN hzdepb_r >= 20 AND hzdept_r < 20 THEN 20 
WHEN hzdept_r < 20 THEN 0
		WHEN hzdept_r < 50 then hzdept_r ELSE 20 END AS InRangeTop_20_50 ,
		
	
CASE   WHEN hzdept_r > 50 THEN 0
WHEN hzdepb_r < 20 THEN 0
WHEN hzdepb_r <= 50 THEN hzdepb_r  WHEN hzdepb_r > 50 and hzdept_r < 50 THEN 50 ELSE 20 END AS InRangeBot_20_50,



CASE    WHEN hzdepb_r < 50 THEN 0
WHEN hzdept_r >100 THEN 0 
WHEN hzdepb_r >= 50 AND hzdept_r < 50 THEN 50 
WHEN hzdept_r < 50 THEN 0
		WHEN hzdept_r < 100 then hzdept_r ELSE 50 END AS InRangeTop_50_100 ,
		
	
CASE   WHEN hzdept_r > 100 THEN 0
WHEN hzdepb_r < 50 THEN 0
WHEN hzdepb_r <= 100 THEN hzdepb_r  WHEN hzdepb_r > 100 and hzdept_r < 100 THEN 100 ELSE 50 END AS InRangeBot_50_100,
--CASE    WHEN hzdept_r < 50 THEN 50
--		WHEN hzdept_r < 100 then hzdept_r ELSE 50 END AS InRangeTop_50_100,
		
--CASE    WHEN hzdepb_r < 50 THEN 50
--WHEN hzdepb_r <= 100 THEN hzdepb_r  WHEN hzdepb_r > 100 and hzdept_r < 100 THEN 100 ELSE 50 END AS InRangeBot_50_100,

om_r, fragvol, dbthirdbar_r, cokey, mukey, 100.0 - fragvol AS frag_main
INTO #SOC
FROM #acpf
ORDER BY cokey, hzdept_r ASC, hzdepb_r ASC, chkey
```
|hzname|chkey|comppct_r|hzdept_r|hzdepb_r|thickness|InRangeTop|InRangeBot|InRangeTop_0_30|InRangeBot_0_30|InRangeTop_20_50|InRangeBot_20_50|InRangeTop_50_100|InRangeBot_50_100|om_r|fragvol|dbthirdbar_r|cokey|mukey|frag_main|
|------|-----|---------|--------|--------|---------|----------|----------|---------------|--------------|-----------------|-----------------|----------------|-----------------|-----|--------------|------------|-----------|---------|---------|
|Ap|39904473|90|0|18|18|0|18|0|18|0|0|0|0|1.5|5|1.4|13906974|2809839|95|
|Bt1|39904470|90|18|25|7|18|25|18|25|20|25|0|0|0.5|5|1.5|13906974|2809839|95|
|2Bt2|39904471|90|25|48|23|25|48|25|30|25|48|0|0|0.25|11|1.4|13906974|2809839|89|
|3Bt3|39904472|90|48|89|41|48|89|0|0|48|50|50|89|0.25|45|1.5|13906974|2809839|55|
|Ap|39904478|10|0|23|23|0|23|0|23|20|23|0|0|1.5|3|1.4|13906975|2809839|97|
|BE|39904479|10|23|33|10|23|33|23|30|23|33|0|0|0.25|3|1.4|13906975|2809839|97|
|Bt1|39904480|10|33|58|25|33|58|0|0|33|50|50|58|0.25|5|1.5|13906975|2809839|95|
|2Bt2|39904475|10|58|89|31|58|89|0|0|0|0|58|89|0.25|11|1.4|13906975|2809839|89|
|3Bt3|39904476|10|89|114|25|89|114|0|0|0|0|89|100|0.25|45|1.5|13906975|2809839|55|


### SOC2 Table
```SQL
SELECT mukey, cokey, hzname, chkey, comppct_r, hzdept_r, hzdepb_r, thickness, 
InRangeTop_0_30, 
InRangeBot_0_30, 

InRangeTop_20_50, 
InRangeBot_20_50, 

InRangeTop_50_100 ,
InRangeBot_50_100,
(( ((InRangeBot_0_30 - InRangeTop_0_30) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_0_30,
---Removed * ( comppct_r * 100 ) 
((((InRangeBot_20_50 - InRangeTop_20_50) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_20_50,
---Removed * ( comppct_r * 100 ) 
((((InRangeBot_50_100 - InRangeTop_50_100) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_50_100
---Removed * ( comppct_r * 100 ) 
INTO #SOC2
FROM #SOC
ORDER BY  mukey ,cokey, comppct_r DESC, hzdept_r ASC, hzdepb_r ASC, chkey
```
|mukey|cokey|hzname|chkey|comppct_r|hzdept_r|hzdepb_r|thickness|InRangeTop_0_30|InRangeBot_0_30|InRangeTop_20_50|InRangeBot_20_50|InRangeTop_50_100|InRangeBot_50_100|HZ_SOC_0_30|HZ_SOC_20_50|HZ_SOC_50_100|
|-----|-----|------|------|------|------|------|------|------|------|------|------|------|------|------|------|------|
|2809839|13906974|Ap|39904473|90|0|18|18|0|18|0|0|0|0|0.2082947|0|0|
|2809839|13906974|Bt1|39904470|90|18|25|7|18|25|20|25|0|0|0.02892981|0.02066415|0|
|2809839|13906974|2Bt2|39904471|90|25|48|23|25|30|25|48|0|0|0.009034222|0.04155742|0|
|2809839|13906974|3Bt3|39904472|90|48|89|41|0|0|48|50|50|89|0|0.002392691|0.04665748|
|2809839|13906975|Ap|39904478|10|0|23|23|0|23|20|23|0|0|0.2717576|0.03544664|0|
|2809839|13906975|BE|39904479|10|23|33|10|23|30|23|33|0|0|0.0137848|0.01969258|0|
|2809839|13906975|Bt1|39904480|10|33|58|25|0|0|33|50|50|58|0|0.03512906|0.01653132|
|2809839|13906975|2Bt2|39904475|10|58|89|31|0|0|0|0|58|89|0|0|0.05601218|
|2809839|13906975|3Bt3|39904476|10|89|114|25|0|0|0|0|89|100|0|0|0.0131598|

### SOC3 Table
```SQL
---Aggregates and sum it by component. 
SELECT DISTINCT cokey, mukey,  
ROUND (SUM (HZ_SOC_0_30) over(PARTITION BY cokey) ,3) AS CO_SOC_0_30, 
ROUND (SUM (HZ_SOC_20_50) over(PARTITION BY cokey),3) AS CO_SOC_20_50, 
ROUND (SUM (HZ_SOC_50_100) over(PARTITION BY cokey),3)  AS CO_SOC_50_100 
INTO #SOC3
FROM #SOC2
```
|cokey|mukey|CO_SOC_0_30|CO_SOC_20_50|CO_SOC_50_100|
|-----|-----|-----------|------------|-------------|
|13906974|	2809839|	0.246|	0.065|	0.047|
|13906975|	2809839|	0.286|	0.09|	0.086|


### SOC4 Table
```SQL
SELECT DISTINCT #SOC3.cokey, #SOC3.mukey,  WEIGHTED_COMP_PCT, CO_SOC_0_30, CO_SOC_0_30 * WEIGHTED_COMP_PCT AS WEIGHTED_CO_SOC_0_30
INTO #SOC4
FROM #SOC3
INNER JOIN #muacpf3 ON #muacpf3.cokey=#SOC3.cokey
```


|cokey|mukey|WEIGHTED_COMP_PCT|CO_SOC_0_30|WEIGHTED_CO_SOC_0_30|
|-----|-----|-----------------|----------|--------------------|
|13906974|2809839|0.90|0.246|0.2214|
|13906975|2809839|0.10|0.286|0.0286|

### End Table
```SQL 
SELECT DISTINCT #main.mukey, ROUND (SUM (WEIGHTED_CO_SOC_0_30) over(PARTITION BY #SOC4.mukey) ,3)* 100 AS SOCSTOCK_0_30 --, 
--Unit Conversion
---ROUND (SUM (CO_SOC_20_50) over(PARTITION BY #SOC3.mukey),3) AS SOC_20_50, 
---ROUND(SUM (CO_SOC_50_100) over(PARTITION BY #SOC3.mukey),3)  AS SOC_50_100 
FROM #SOC4
RIGHT OUTER JOIN #main ON #main.mukey=#SOC4.mukey
```
|mukey|	SOCSTOCK_0_30|
|-----|---------|
|2809839|25|






