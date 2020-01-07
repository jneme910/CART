 SELECT areasymbol, musym, muname, mu.mukey/1  AS MUKEY, 
 (SELECT TOP 1 ROUND (AVG(interphr) over(partition by interphrc),2)
 FROM mapunit
 INNER JOIN component ON component.mukey=mapunit.mukey
 INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE 'SOH - Soil Susceptibility to Compaction' GROUP BY interphrc, interphr
 ORDER BY SUM (comppct_r) DESC)as rating,
 (SELECT TOP 1 interphrc
 FROM mapunit
 INNER JOIN component ON component.mukey=mapunit.mukey
 INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey AND ruledepth = 0 AND mrulename LIKE 'SOH - Soil Susceptibility to Compaction'
 GROUP BY interphrc, comppct_r ORDER BY SUM(comppct_r) over(partition by interphrc) DESC) as class,
 
  (SELECT DISTINCT SUBSTRING(  (  SELECT ( '; ' + interphrc)
FROM mapunit
INNER JOIN component ON component.mukey=mapunit.mukey AND compkind != 'miscellaneous area' AND component.cokey=c.cokey
INNER JOIN cointerp ON component.cokey = cointerp.cokey AND mapunit.mukey = mu.mukey 

AND ruledepth != 0 AND interphrc NOT LIKE 'Not%' AND mrulename LIKE 'SOH - Soil Susceptibility to Compaction' GROUP BY interphrc, interphr
ORDER BY interphr DESC, interphrc
FOR XML PATH('') ), 3, 1000) )as reason

  
 FROM legend  AS l
 INNER JOIN  mapunit AS mu ON mu.lkey = l.lkey AND l.areasymbol <> 'US'
 INNER JOIN  component AS c ON c.mukey = mu.mukey AND c.cokey =
 (SELECT TOP 1 c1.cokey FROM component AS c1
 INNER JOIN mapunit ON c.mukey=mapunit.mukey AND c1.mukey=mu.mukey ORDER BY c1.comppct_r DESC, c1.cokey)
 ORDER BY areasymbol, musym, muname, mu.mukey
 
