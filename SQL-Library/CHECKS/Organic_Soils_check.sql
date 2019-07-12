SELECT 
aoiid, 
landunit, 
M44.mukey, 
mapunit_acres, 
M44.cokey AS cokey, 
M44.compname AS cname, 
M44.comppct_r AS copct ,
M44.majcompflag AS majcompflag, 
taxgrtgroup,
taxsubgrp,
hydricrating  
FROM 
mapunit AS M44 
INNER JOIN component ON  M44.cokey=component.cokey --AND M44.majcompflag = 'Yes' 
AND CASE WHEN taxsubgrp LIKE '%hist%'THEN 1 
WHEN taxsubgrp LIKE '%ists%'AND taxsubgrp NOT LIKE '%fol%' THEN 1 
WHEN taxgrtgroup LIKE '%ists%'AND taxgrtgroup NOT LIKE '%fol%' THEN 1 
---WHEN hydricrating = 'Yes'  THEN 1
 ELSE 2 END = 1;