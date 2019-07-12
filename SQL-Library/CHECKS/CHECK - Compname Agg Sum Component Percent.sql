DROP TABLE IF EXISTS #comp2
DROP TABLE IF EXISTS #comp

SELECT  areasymbol, areaname,  mapunit.muname, mapunit.mukey, compname, localphase, component.cokey,
comppct_r, majcompflag , nationalmusym, musym
INTO #comp2
FROM (legend INNER JOIN (mapunit   INNER JOIN component ON mapunit.mukey = component.mukey AND majcompflag = 'Yes' ) ON legend.lkey = mapunit.lkey AND areasymbol <> 'US')
ORDER BY areasymbol ASC, musym ASC, muname ASC,  component.cokey;

---with — recursive common table expression - Organize Complex Queries
WITH #comp AS (Select areasymbol, areaname, nationalmusym, musym, muname, mukey, compname, cokey, majcompflag, localphase,  SUM (comppct_r) over(partition by mukey) AS  mu_sum_pct, 
SUM (comppct_r) over(partition by mukey, compname) AS  sum_compname_pct  From #comp2)


Select areasymbol, areaname, nationalmusym, musym, muname, mukey, compname, localphase, cokey,  majcompflag,  mu_sum_pct, sum_compname_pct
From #comp
Where sum_compname_pct < 10
ORDER BY areasymbol ASC, musym ASC, muname ASC


-- Cleanup all temporary tables 
IF OBJECT_ID('temp_db..#comp2', 'U') IS NOT NULL
  DROP TABLE #comp2;
IF OBJECT_ID('temp_db..#comp', 'U') IS NOT NULL
  DROP TABLE #comp;
