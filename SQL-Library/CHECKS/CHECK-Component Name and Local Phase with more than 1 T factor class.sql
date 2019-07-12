SELECT CASE WHEN localphase IS NULL THEN compname ELSE CONCAT(compname, ', ', localphase)  END AS compname_localphase,  SUBSTRING(  (  SELECT  ( ', ' +  CAST (tfact AS varchar))
FROM component AS co
WHERE CASE WHEN co.localphase IS NULL THEN co.compname ELSE CONCAT(co.compname, ', ', co.localphase)  END = 
CASE WHEN s.localphase IS NULL THEN s.compname ELSE CONCAT(s.compname, ', ', s.localphase)  END

GROUP BY tfact
ORDER BY tfact
FOR XML PATH('') ), 3, 50) as  T
--INTO #temp_hsg
FROM (SELECT   compname, localphase, tfact
FROM legend 
       INNER JOIN mapunit ON mapunit.lkey=legend.lkey 
	   --AND LEFT (areasymbol, 2) IN ('TX') 
	   -AND LEFT (areasymbol, 2) <> 'US'
              INNER JOIN component ON component.mukey=mapunit.mukey 
              AND compkind = 'Series' 
             GROUP BY compname, localphase, tfact HAVING COUNT (tfact) > 1) AS s

              GROUP BY s.compname,  s.localphase
       
       HAVING COUNT (tfact) > 1
	   ORDER BY CASE WHEN localphase IS NULL THEN compname ELSE CONCAT (compname, ', ', localphase) END ASC
--CASE WHEN localphase IS NULL THEN compname ELSE CONCAT (compname, ', ', localphase) END AS compname_localphase