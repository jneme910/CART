SELECT   areasymbol, compname, taxorder, taxclname,  taxsubgrp , featkind, mapunit.mukey, component.cokey
FROM legend
INNER JOIN mapunit ON mapunit.lkey=legend.lkey AND areasymbol <> 'US'
INNER JOIN component ON component.mukey=mapunit.mukey AND majcompflag = 'Yes' AND taxorder NOT IN ('Histosols', 'Gelisols') AND taxsubgrp NOT LIKE '%Histic%'
INNER JOIN codiagfeatures ON codiagfeatures.cokey=component.cokey AND featkind LIKE 'Histic%'
