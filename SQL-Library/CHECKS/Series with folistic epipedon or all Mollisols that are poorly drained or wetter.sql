--Soil Data Access https://sdmdataaccess.nrcs.usda.gov/Query.aspx
--- folistic epipedon, or all Mollisols that are poorly drained or wetter


SELECT DISTINCT compname, taxorder ,
SUBSTRING(  (  SELECT  ( ', ' +  taxsubgrp)
FROM component AS co
WHERE  co.compname = component.compname
GROUP BY  taxsubgrp
ORDER BY  taxsubgrp
FOR XML PATH('') ), 3, 50) as  Subgroup,
SUBSTRING(  (  SELECT  ( ', ' +  drainagecl)
FROM component AS co
WHERE  co.compname = component.compname
GROUP BY  drainagecl
ORDER BY  drainagecl
FOR XML PATH('') ), 3, 50) as  Drainage_Class


 
FROM legend
INNER JOIN mapunit ON mapunit.lkey=legend.lkey AND areasymbol <> 'US'
INNER JOIN component ON component.mukey=mapunit.mukey AND compkind = 'Series' AND CASE WHEN taxsubgrp LIKE '%folist%' THEN 1
WHEN  taxorder LIKE 'Mollisols' AND drainagecl = 'Poorly drained'
 THEN 1 WHEN  taxorder LIKE 'Mollisols'  AND drainagecl = 'Very poorly drained' THEN 1 
ELSE 2 END = 1 GROUP BY compname, taxorder, taxsubgrp, drainagecl  ORDER BY compname ASC