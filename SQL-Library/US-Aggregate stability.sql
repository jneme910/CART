CREATE TABLE #M2
    ( aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT
    );

INSERT INTO #M2
SELECT 1 AS aoiid, areasymbol AS  landunit, mukey, muacres AS mapunit_acres
FROM legend
INNER JOIN mapunit ON mapunit.lkey=legend.lkey AND areasymbol <> 'US'
 ;

-- Component level data with cokey, comppct_r and mapunit sum-of-comppct_r (major components only)
CREATE TABLE #M4
(   aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT,
    cokey INT,
    compname CHAR(60),
    comppct_r INT,
    majcompflag CHAR(3),
	mu_pct_sum INT
    );

INSERT INTO #M4
SELECT M2.aoiid, M2.landunit, M2.mukey, mapunit_acres, CO.cokey, CO.compname, CO.comppct_r, CO.majcompflag, SUM (CO.comppct_r) OVER(PARTITION BY  M2.mukey) AS mu_pct_sum
FROM #M2 AS M2
INNER JOIN component AS CO ON CO.mukey = M2.mukey AND majcompflag = 'Yes'; 


CREATE TABLE #agg1
(  aoiid INT ,
landunit CHAR(20), 
mukey INT,
mapunit_acres FLOAT, 
cokey INT,
compname CHAR(60),
comppct_r INT,
majcompflag  CHAR(3),
localphase CHAR(60),
 hzname CHAR(20),
 hzdept_r INT,
 hzdepb_r INT,
claytotall FLOAT,
claytotalr FLOAT,
claytotalh FLOAT,
oml  FLOAT ,
 omr FLOAT  ,
omh  FLOAT,
 sar_l FLOAT,
 sar_r FLOAT,
 sar_h FLOAT,
 cec7_l FLOAT,
 cec7_r FLOAT,
 cec7_h FLOAT,
 ec_l FLOAT,
 ec_r FLOAT,
 ec_h FLOAT,
 esp_l FLOAT,
esp_r FLOAT,
esp_h FLOAT, 
tcl CHAR(40),
mu_pct_sum INT)
;
-- Component level data with cokey, comppct_r and mapunit sum-of-comppct_r (major components only)
INSERT INTO #agg1


SELECT DISTINCT 
 MA44.aoiid ,
 MA44.landunit, 
 MA44.mukey,
 MA44.mapunit_acres, 
 MA44.cokey,
 MA44.compname,
 MA44.comppct_r,
 MA44.majcompflag,
 localphase,
 hzname,
 hzdept_r,
 hzdepb_r,
 CASE WHEN claytotal_l > 92 then 92 WHEN claytotal_l < 8 THEN 8 ELSE claytotal_l END AS claytotall,
 CASE WHEN claytotal_r > 92 then 92 ELSE claytotal_r END AS claytotalr,
 CASE WHEN claytotal_h > 92 then 92 ELSE claytotal_h END AS claytotalh,
  FORMAT ( CASE WHEN om_l <0.01 THEN 0.05 WHEN om_l > 17 then 17 ELSE om_l END , '#,###,##0.00') AS oml  ,
  FORMAT (CASE WHEN om_r <0.01 THEN 0.05 WHEN om_r > 17 then 17 ELSE om_r END , '#,###,##0.00') AS omr  ,
  FORMAT (CASE WHEN om_h <0.01 THEN 0.05 WHEN om_h > 17 then 17 ELSE om_h END , '#,###,##0.00') AS omh  ,
 sar_l,
 sar_r,
 sar_h,
 cec7_l,
 cec7_r,
 cec7_h,
 ec_l,
 ec_r,
 ec_h,
 CASE WHEN sar_l = 0 THEN '0' ELSE   FORMAT (CAST ((100*(-0.0126+0.01475*sar_l))/(1+(-0.0126+0.01475*sar_l)) as float)  , '#,###,##0.00') END  as esp_l,
  CASE WHEN sar_r = 0 THEN '0' ELSE     FORMAT (CAST ((100*(-0.0126+0.01475*sar_r))/(1+(-0.0126+0.01475*sar_r)) as float) , '#,###,##0.00') END as esp_r,
  CASE WHEN sar_h = 0 THEN '0' ELSE  FORMAT (CAST ((100*(-0.0126+0.01475*sar_h))/(1+(-0.0126+0.01475*sar_h)) as float)  , '#,###,##0.00')  END as esp_h, 
 (SELECT TOP 1 texcl FROM chtexturegrp AS chtg INNER JOIN chtexture AS cht ON chtg.chtgkey=cht.chtgkey  AND chtg.rvindicator = 'yes' AND chtg.chkey=cha.chkey) AS tcl,
 mu_pct_sum
FROM (#M4 AS MA44 INNER JOIN (component AS coa INNER JOIN  chorizon   AS cha  ON cha.cokey=coa.cokey AND cha.hzdept_r < 15 ) ON MA44.cokey=coa.cokey AND MA44.majcompflag = 'Yes' );

CREATE TABLE #agg2
(  aoiid INT ,
landunit CHAR(20), 
mukey INT,
mapunit_acres FLOAT, 
cokey INT,
compname CHAR(60),
comppct_r INT,
majcompflag  CHAR(3),
localphase CHAR(60),
 hzname CHAR(20),
 hzdept_r INT,
 hzdepb_r INT,
claytotall FLOAT,
claytotalr FLOAT,
claytotalh FLOAT,
oml  FLOAT,
omr FLOAT,
omh  FLOAT,
 sar_l FLOAT,
 sar_r FLOAT,
 sar_h FLOAT,
 cec7_l FLOAT,
 cec7_r FLOAT,
 cec7_h FLOAT,
 ec_l FLOAT,
 ec_r FLOAT,
 ec_h FLOAT,
 esp_l FLOAT,
esp_r FLOAT,
esp_h FLOAT, 
tcl CHAR(40),
sandy INT,
 mu_pct_sum INT);

INSERT INTO #agg2
SELECT DISTINCT
aoiid ,
landunit, 
mukey,
mapunit_acres, 
cokey,
compname,
comppct_r,
majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r,
claytotall,
claytotalr,
claytotalh,
oml ,
omr ,
omh ,
sar_l,
sar_r,
sar_h,
cec7_l,
cec7_r,
cec7_h,
ec_l,
ec_r,
ec_h,
CASE WHEN cec7_l < 50 + 0 and (cec7_l) IS NOT NULL  and (sar_l) IS NOT NULL and sar_l !=0 and sar_l < 40 + 0  and ec_l < 20 + 0 then esp_l
            WHEN  sar_l !=0 and  (sar_l) IS NOT NULL then 1.5*sar_l/(1 + 0.015*sar_l)
            WHEN sar_l < 0.01 then 0 else null END AS esp_l, 

 CASE WHEN cec7_r < 50 + 0 and (cec7_r) IS NOT NULL  and (sar_r) IS NOT NULL and sar_r !=0 and sar_r < 40 + 0  and ec_r < 20 + 0 then esp_r
            WHEN  sar_r !=0 and  (sar_r) IS NOT NULL then 1.5*sar_r/(1 + 0.015*sar_r)
            WHEN sar_r < 0.01 then 0 else null END AS esp_r, 

CASE WHEN cec7_h < 50 + 0 and (cec7_h) IS NOT NULL  and (sar_h) IS NOT NULL and sar_h !=0 and sar_h < 40 + 0  and ec_h < 20 + 0 then esp_h
            WHEN  sar_h !=0 and  (sar_h) IS NOT NULL then 1.5*sar_h/(1 + 0.015*sar_h)
           WHEN sar_h < 0.01 then 0 else null END AS esp_h, 
tcl, 
CASE WHEN  tcl ='Loamy coarse sand' THEN 1
WHEN  tcl = 'Loamy fine sand' THEN 1
WHEN  tcl = 'Loamy sand'  THEN 1
WHEN  tcl = 'Sand' THEN 1
WHEN  tcl = 'Coarse sand' THEN 1
WHEN  tcl = 'Fine sand' THEN 1 ELSE 0 END AS sandy,  mu_pct_sum
FROM #agg1;

CREATE TABLE #agg3
(  aoiid INT ,
landunit CHAR(20), 
mukey INT,
mapunit_acres FLOAT, 
cokey INT,
compname CHAR(60),
comppct_r INT,
majcompflag  CHAR(3),
localphase CHAR(60),
 hzname CHAR(20),
 hzdept_r INT,
 hzdepb_r INT,
claytotall FLOAT,
claytotalr FLOAT,
claytotalh FLOAT,
oml FLOAT,
omr FLOAT,
omh FLOAT,
sandy INT, 
AgStab_l FLOAT,
AgStab_r FLOAT,
AgStab_h FLOAT,
tcl CHAR(40),  mu_pct_sum INT)
;

INSERT INTO #agg3
SELECT DISTINCT 
aoiid ,
landunit, 
mukey,
mapunit_acres, 
cokey,
compname,
comppct_r,
majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r, 
claytotall,
claytotalr,
claytotalh,
oml,
omr,
omh,
sandy,
FORMAT (49.7+13.7*LOG(oml) + 0.61*claytotall-0.0045*POWER(claytotall,2) - 0.28*esp_h-0.06*POWER(esp_h,2), '#,###,##0.00')  AS AgStab_l,
FORMAT (49.7+13.7*LOG(omr) + 0.61*claytotalr-0.0045*POWER(claytotalr,2) - 0.28*esp_r-0.06*POWER(esp_r,2), '#,###,##0.00')  AS AgStab_r,
FORMAT (49.7+13.7*LOG(omh) + 0.61*claytotalh-0.0045*POWER(claytotalh,2) - 0.28*esp_l-0.06*POWER(esp_l,2), '#,###,##0.00')  AS AgStab_h, 
tcl,  mu_pct_sum 
FROM #agg2;


CREATE TABLE #agg4
(  aoiid INT ,
landunit CHAR(20), 

mukey INT,
mapunit_acres FLOAT, 
cokey INT,
compname CHAR(60),
comppct_r INT,
majcompflag  CHAR(3),
localphase CHAR(60),
 hzname CHAR(20),
 hzdept_r INT,
 hzdepb_r INT,
AgStab_l FLOAT,
AgStab_r FLOAT,
AgStab_h FLOAT,
tcl CHAR(40),  
mu_pct_sum INT,
adj_comp_pct FLOAT, 
thickness INT,
AGG_InRangeTop_0_15 INT,
AGG_InRangeBot_0_15 INT
)
;

INSERT INTO #agg4
SELECT DISTINCT ag.aoiid ,
ag.landunit, 
mukey,
mapunit_acres, 
cokey,
compname,
comppct_r,
majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r, 
CASE WHEN AgStab_l > 100  THEN 100 WHEN claytotall >= 0  and claytotall < 5 THEN null WHEN sandy=1 THEN null WHEN oml > 20 THEN null ELSE AgStab_l END AS AgStab_l,
CASE WHEN AgStab_r > 100  THEN 100 WHEN claytotalr >= 0  and claytotalr < 5 THEN null WHEN sandy=1 THEN null WHEN omr > 20 THEN null ELSE AgStab_r END AS AgStab_r,
CASE WHEN AgStab_h > 100  THEN 100 WHEN claytotalh >= 0  and claytotalh < 5 THEN null WHEN sandy=1 THEN null WHEN omh > 20 THEN null ELSE AgStab_h END AS AgStab_h,
tcl,  mu_pct_sum, 

CASE WHEN comppct_r = 0 THEN 0 
WHEN mu_pct_sum = 0 THEN 100 ELSE (1.0 * comppct_r / mu_pct_sum) END AS adj_comp_pct, 
CASE WHEN hzdepb_r IS NULL THEN 0
WHEN hzdept_r IS NULL THEN 0 ELSE hzdepb_r-hzdept_r END AS thickness, 
CASE  WHEN hzdept_r < 15 then hzdept_r ELSE 0 END AS AGG_InRangeTop_0_15, 
CASE  WHEN hzdepb_r <= 15 THEN hzdepb_r WHEN hzdepb_r > 15 and hzdept_r < 15 THEN 15 ELSE 0 END AS AGG_InRangeBot_0_15
FROM  #agg3 AS ag  WHERE majcompflag = 'Yes' GROUP BY ag.aoiid ,
ag.landunit, 

mukey,
mapunit_acres, 
cokey,
compname,
comppct_r,
majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r, AgStab_l , AgStab_h, AgStab_r, claytotall, claytotalr, claytotalh, sandy,comppct_r , mu_pct_sum , oml, omr, omh, tcl;


CREATE TABLE #agg5
(  aoiid INT ,
landunit CHAR(20), 

mukey INT,
mapunit_acres FLOAT, 
cokey INT,
compname CHAR(60),
comppct_r INT,
majcompflag  CHAR(3),
localphase CHAR(60),
 hzname CHAR(20),
 hzdept_r INT,
 hzdepb_r INT,
AgStab_l FLOAT,
AgStab_r FLOAT,
AgStab_h FLOAT,
tcl CHAR(40),  
mu_pct_sum INT,
adj_comp_pct FLOAT, 
thickness INT,
AGG_InRangeTop_0_15 INT,
AGG_InRangeBot_0_15 INT,
InRangeThickness INT, 
InRangeSumThickness INT )
;

INSERT INTO #agg5
SELECT DISTINCT  aoiid ,
landunit, 

mukey,
mapunit_acres, 
cokey,
compname,
comppct_r,
majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r, 
AgStab_l,
AgStab_r,
AgStab_h,
tcl, 
mu_pct_sum,
adj_comp_pct,
thickness, 
AGG_InRangeTop_0_15, 
AGG_InRangeBot_0_15,
CASE WHEN AGG_InRangeTop_0_15 IS NULL THEN 0 
WHEN AGG_InRangeBot_0_15 IS NULL THEN 0 ELSE AGG_InRangeBot_0_15 - AGG_InRangeTop_0_15 END AS InRangeThickness,
SUM (CASE WHEN AGG_InRangeTop_0_15 IS NULL THEN 0 
WHEN AGG_InRangeBot_0_15 IS NULL THEN 0 ELSE AGG_InRangeBot_0_15 - AGG_InRangeTop_0_15 END) over(PARTITION BY cokey) AS InRangeSumThickness
FROM #agg4
GROUP BY aoiid ,
landunit, 

mukey,
mapunit_acres, 
cokey,
compname,
comppct_r,
majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r, 
AgStab_l,
AgStab_r,
AgStab_h,
tcl, 
mu_pct_sum,
adj_comp_pct,
thickness, 
AGG_InRangeTop_0_15, 
AGG_InRangeBot_0_15 ;


CREATE TABLE #agg6
( aoiid INT,
landunit CHAR(20),  

mukey INT,
mapunit_acres FLOAT, 
cokey INT,
compname CHAR(60),
localphase CHAR(60),
mu_pct_sum INT,
adj_comp_pct FLOAT ,
--AGG_InRangeTop_0_15 INT, 
--AGG_InRangeBot_0_15 INT, 
--InRangeThickness INT, 
--InRangeSumThickness INT, 
--AgStab_l FLOAT,
--AgStab_r FLOAT, 
--AgStab_h FLOAT,
comp_weighted_average_l FLOAT, 
comp_weighted_average_r FLOAT, 
comp_weighted_average_h FLOAT
)
;

INSERT INTO #agg6
SELECT DISTINCT  aoiid ,
landunit, 

mukey,
mapunit_acres, 
cokey,
compname,
localphase,
mu_pct_sum,
adj_comp_pct,
--AGG_InRangeTop_0_15, 
--AGG_InRangeBot_0_15,
--InRangeThickness,
--InRangeSumThickness, 
--AgStab_l ,
--AgStab_r , 
--AgStab_h ,
CASE WHEN InRangeSumThickness IS NULL THEN 0 WHEN  InRangeThickness IS NULL THEN 0 WHEN  InRangeThickness = 0 THEN 0 WHEN InRangeSumThickness = 0 THEN 0 WHEN AgStab_l = 0 THEN 0  WHEN AgStab_l IS NULL THEN 0 ELSE  SUM ((CAST (InRangeThickness AS FLOAT)/CAST (InRangeSumThickness AS FLOAT)) * AgStab_l)  over(PARTITION BY ag5.cokey) END  AS comp_weighted_average_l,
CASE  WHEN InRangeSumThickness IS NULL THEN 0  WHEN  InRangeThickness IS NULL THEN 0  WHEN InRangeThickness = 0 THEN 0 WHEN InRangeSumThickness = 0 THEN 0 WHEN AgStab_r = 0 THEN 0 WHEN AgStab_r IS NULL THEN 0 ELSE SUM((CAST (InRangeThickness AS FLOAT)/CAST (InRangeSumThickness AS FLOAT)) * AgStab_r)  over(PARTITION BY ag5.cokey) END AS  comp_weighted_average_r,
CASE WHEN InRangeSumThickness IS NULL THEN 0 WHEN  InRangeThickness IS NULL THEN 0  WHEN InRangeThickness = 0 THEN 0 WHEN InRangeSumThickness = 0 THEN 0 WHEN AgStab_h = 0 THEN 0 WHEN AgStab_h IS NULL THEN 0 ELSE SUM((CAST (InRangeThickness AS FLOAT)/CAST (InRangeSumThickness AS FLOAT)) * AgStab_h)  over(PARTITION BY ag5.cokey) END AS comp_weighted_average_h
FROM  #agg5 AS ag5 
WHERE InRangeSumThickness !=0
GROUP BY aoiid, landunit, 

mukey,
mapunit_acres, 
cokey,
compname,
localphase,
mu_pct_sum,
adj_comp_pct,-- AgStab_l ,
--AgStab_r , 
--AgStab_h ,
--AGG_InRangeTop_0_15, 
--AGG_InRangeBot_0_15,
InRangeThickness,
InRangeSumThickness, AgStab_l, AgStab_r, AgStab_h ;

SELECT DISTINCT aoiid ,
landunit, 

mukey,
mapunit_acres, 
mu_pct_sum,
--AgStab_l ,
--AgStab_r , 
--AgStab_h ,
 CASE WHEN adj_comp_pct = 0 THEN '0' ELSE  FORMAT ( SUM (adj_comp_pct * comp_weighted_average_l) over(PARTITION BY ag6.mukey, aoiid )  , '#,###,##0.00') END AS MU_SUM_AGG_L,
 CASE WHEN adj_comp_pct = 0 THEN '0' ELSE FORMAT (SUM (adj_comp_pct * comp_weighted_average_r) over(PARTITION BY ag6.mukey, aoiid )  , '#,###,##0.00') END  AS MU_SUM_AGG_R,
 CASE WHEN adj_comp_pct = 0 THEN '0' ELSE FORMAT (SUM (adj_comp_pct * comp_weighted_average_h) over(PARTITION BY ag6.mukey, aoiid )  , '#,###,##0.00') END   AS MU_SUM_AGG_H
FROM #agg6 AS ag6
GROUP BY aoiid ,
landunit, 

mukey,
mapunit_acres, 
mu_pct_sum,
adj_comp_pct,
--AgStab_l,
--AgStab_r,
--AgStab_h,
comp_weighted_average_l,
comp_weighted_average_r,
comp_weighted_average_h 
;