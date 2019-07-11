-- 2019-03-27 T13:28:13 
----https://websoilsurvey.sc.egov.usda.gov/App/WebSoilSurvey.aspx?aoicoords=MULTIPOLYGON%20(((-98.599033355712876%2039.839814661109379,%20-98.58066558837892%2039.838793139814641,%20-98.579893112182646%2039.827917939050472,%20-98.59916210174562%2039.828643006003304,%20-98.599462509155273%2039.839682852763886,%20-98.599033355712876%2039.839814661109379)),%20((-98.575901985168485%2039.843307490079241,%20-98.572382926940918%2039.836288700736318,%20-98.552942276000977%2039.839320378509363,%20-98.55804920196536%2039.844065344605674,%20-98.575901985168485%2039.843307490079241)))
-- BEGIN CREATING AOI QUERY
--
-- Declare all variables here
use sdmONLINE;
GO
SET STATISTICS IO ON 
GO 

DROP TABLE IF EXISTS #AoiTable
DROP TABLE IF EXISTS #AoiAcres
DROP TABLE IF EXISTS #AoiSoils
DROP TABLE IF EXISTS #AoiSoils2
DROP TABLE IF EXISTS #M2
DROP TABLE IF EXISTS #M5
DROP TABLE IF EXISTS #M4
DROP TABLE IF EXISTS #M6
DROP TABLE IF EXISTS #M8
DROP TABLE IF EXISTS #M10
DROP TABLE IF EXISTS #InterpTable
DROP TABLE IF EXISTS #LandunitRatingsDetailed
DROP TABLE IF EXISTS #LandunitRatingsCART
DROP TABLE IF EXISTS #SDV
DROP TABLE IF EXISTS #RatingClasses
DROP TABLE IF EXISTS #RatingDomain
DROP TABLE IF EXISTS #DateStamps
DROP TABLE IF EXISTS #LandunitMetadata
DROP TABLE IF EXISTS #LandunitRatingsDetailed1
DROP TABLE IF EXISTS #LandunitRatingsDetailed2
DROP TABLE IF EXISTS  #LandunitRatingsCART2
DROP TABLE IF EXISTS #interp_dcd
DROP TABLE IF EXISTS  #Hydric2
DROP TABLE IF EXISTS  #Hydric3
DROP TABLE IF EXISTS #Hydric_A
DROP TABLE IF EXISTS #Hydric_B
DROP TABLE IF EXISTS  #Hydric1
DROP TABLE IF EXISTS  #Hydric3
DROP TABLE IF EXISTS  #FC
DROP TABLE IF EXISTS  #wet
DROP TABLE IF EXISTS  #wet1
DROP TABLE IF EXISTS  #wet2
DROP TABLE IF EXISTS  #pf
DROP TABLE IF EXISTS  #pf1
DROP TABLE IF EXISTS  #pf2
DROP TABLE IF EXISTS  #agg1
DROP TABLE IF EXISTS  #agg2
DROP TABLE IF EXISTS  #agg3
DROP TABLE IF EXISTS  #agg4
DROP TABLE IF EXISTS #agg5
DROP TABLE IF EXISTS #agg6
GO

DECLARE @attributeName CHAR(60);
DECLARE @ruleDesign CHAR(60);
DECLARE @ruleKey CHAR(30);
DECLARE @rating1 CHAR(60);
DECLARE @rating2  CHAR(60);
DECLARE @rating3 CHAR(60);
DECLARE @rating4 CHAR(60);
DECLARE @rating5 CHAR(60);
DECLARE @rating6 CHAR(60);
DECLARE @dateStamp VARCHAR(60);
DECLARE @minAcres INT ;
DECLARE @minPct INT ;
DECLARE @aoiGeom Geometry;
DECLARE @aoiGeomFixed Geometry;
DECLARE @ratingKey CHAR(70);
DECLARE @notRatedPhrase CHAR(15);
DECLARE @Level INT ;
DECLARE @pAoiId INT ;
declare @intersectedPolygonGeometries table (id int, geom geometry);
declare @intersectedPolygonGeographies table (id int, geog geography);



-- 2019-04-03 T13:16:29 

-- BEGIN CREATING AOI QUERY
--
-- Declare all variables here
--| ~DeclareChar(@attributeName,60)~
--| ~DeclareChar(@ruleDesign,60)~
--| ~DeclareChar(@ruleKey,30)~
--| ~DeclareChar(@rating1,60)~
--| ~DeclareChar(@rating2,60)~
--| ~DeclareChar(@rating3,60)~
--| ~DeclareChar(@rating4,60)~
--| ~DeclareChar(@rating5,60)~
--| ~DeclareChar(@rating6,60)~
--| ~DeclareVarchar(@dateStamp,20)~
--| ~DeclareInt(@minAcres)~
--| ~DeclareInt(@minPct)~
--| ~DeclareGeometry(@aoiGeom)~
--| ~DeclareGeometry(@aoiGeomFixed)~
--| ~DeclareChar(@ratingKey,70)~
--| ~DeclareChar(@notRatedPhrase,15)~
--| ~DeclareInt(@Level)~
 
-- 2019-04-03 T13:16:29 

-- BEGIN CREATING AOI QUERY
--
-- Declare all variables here


-- Create AOI table with polygon geometry. Coordinate system must be WGS1984 (EPSG 4326)
CREATE TABLE #AoiTable 
    ( aoiid INT IDENTITY (1,1),
    landunit CHAR(20),
    aoigeom GEOMETRY);
 
-- Insert identifier string and WKT geometry for each AOI polygon after this...
 
SELECT @aoiGeom = GEOMETRY::STGeomFromText('MULTIPOLYGON (((-102.12335160658608 45.959173206572416, -102.13402890980223 45.959218442561564, -102.13386921506947 45.944643788188387, -102.12327175652177 45.944703605814198, -102.12335160658608 45.959173206572416)))', 4326);   

--SELECT @aoiGeom = GEOMETRY::STGeomFromText('MULTIPOLYGON (((-88.935570716857924 43.677245865460151, -88.920550346374526 43.67727690360843, -88.921065330505385 43.662469884232543, -88.9359998703003 43.662407792603673, -88.935570716857924 43.677245865460151)))', 4326);  
SELECT @aoiGeomFixed = @aoiGeom.MakeValid().STUnion(@aoiGeom.STStartPoint());  
INSERT INTO #AoiTable ( landunit, aoigeom )  
VALUES ('T9981 Fld3', @aoiGeomFixed); 
SELECT @aoiGeom = GEOMETRY::STGeomFromText('MULTIPOLYGON (((-102.1130336443976 45.959162795100383, -102.12335160658608 45.959173206572416, -102.12327175652177 45.944703605814198, -102.1128892282776 45.944710506326032, -102.1130336443976 45.959162795100383)))', 4326);   
--SELECT @aoiGeom = GEOMETRY::STGeomFromText('MULTIPOLYGON (((-88.920421600341811 43.677245865460151, -88.905229568481445 43.677245865460151, -88.905787467956557 43.662563021555471, -88.920722007751479 43.6625940672977, -88.920421600341811 43.677245865460151)))', 4326);   
SELECT @aoiGeomFixed = @aoiGeom.MakeValid().STUnion(@aoiGeom.STStartPoint());  
INSERT INTO #AoiTable ( landunit, aoigeom )  
VALUES ('T9981 Fld4', @aoiGeomFixed);
 

-- End of AOI geometry section
 
-- Create summary acres for each landunit 
CREATE TABLE #AoiAcres
    ( aoiid INT,
    landunit CHAR(20),
    landunit_acres FLOAT
    );
 
-- #LandunitRatingsDetailed1 table columns: landunit, attributename, rating, rating_num, rating_key, rating_pct, rating_acres, landunit_acres
CREATE TABLE #LandunitRatingsDetailed1
    ( aoiid INT,
    landunit CHAR(20),
    attributename CHAR(60),
    rating CHAR(60),
    rating_num INT,
    rating_key CHAR(60),
    rating_pct FLOAT,
    rating_acres FLOAT,
    landunit_acres FLOAT
    );
 
-- #LandunitRatingsDetailed2 table columns: landunit, attributename, rating, rating_num, rating_key, rating_pct, rating_acres, landunit_acres, rolling_pct, rolling_acres 
CREATE TABLE #LandunitRatingsDetailed2
    (landunit CHAR(20),
    attributename CHAR(60),
    rating CHAR(60),
    rating_num INT,
    rating_key CHAR(60),
    rating_pct FLOAT,
    rating_acres FLOAT,
    landunit_acres FLOAT,
    rolling_pct FLOAT,
    rolling_acres FLOAT
    );
 
-- #LandunitRatingsCART table columns: id, landunit, attributename, rating, rating_num, rating_key, rolling_pct, rolling_acres, landunit_acres
CREATE TABLE #LandunitRatingsCART
    (id INT,
    landunit CHAR(20),
    attributename CHAR(60),
    rating CHAR(60),
    -- rating_num INT,
    rating_key CHAR(60),
    rolling_pct FLOAT,
    rolling_acres FLOAT,
    landunit_acres FLOAT
    );
 
-- #LandunitRatingsCART table columns: id, landunit, attributename, rating, rating_num, rating_key, rolling_pct, rolling_acres, landunit_acres
-- This table will only contain the final, overall ratings for CART
CREATE TABLE #LandunitRatingsCART2
    (id INT IDENTITY (1,1),
    landunit CHAR(20),
    attributename CHAR(60),
    rating CHAR(60),
    rating_key CHAR(60),
    rolling_pct FLOAT,
    rolling_acres FLOAT,
    landunit_acres FLOAT,
    soils_metadata VARCHAR(150)
    );
 
-- Create intersected soil polygon table with geometry
CREATE TABLE #AoiSoils 
    ( polyid INT IDENTITY (1,1),
    aoiid INT,
    landunit CHAR(20),
    mukey INT,
    soilgeom GEOMETRY
    );
 
-- Soil geometry with landunits
CREATE TABLE #AoiSoils2 
    ( aoiid INT,
    polyid INT,
    landunit CHAR(20),
    mukey INT,
    poly_acres FLOAT,
    soilgeog GEOGRAPHY
    );
 
-- Soil map unit acres, aggregated by mukey (merges polygons together)
CREATE TABLE #M2
    ( aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT
    );
 
 -- Soil map unit acres, aggregated by mukey Farm Class
CREATE TABLE #FC
    ( aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT, 
    farmlndclass CHAR(30)
    );
 
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

-- Component level ratings for the currently selected soil interpretation
CREATE TABLE #M5
   ( aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT,
    cokey INT,
    compname CHAR(60),
    comppct_r INT,
    rating CHAR(60),
    mu_pct_sum INT
    );
 
-- Component level ratings with adjusted component percent to account for missing minor components
-- #M6 columns: aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating, MU_pct_sum, adj_comp_pct
CREATE TABLE #M6
   ( aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT,
    cokey INT,
    compname CHAR(60),
    comppct_r INT,
    rating CHAR(60),
    mu_pct_sum INT,
    adj_comp_pct FLOAT
    );
 
-- Component acres by multiplying map unit acres with adjusted component percent
-- #M8 columns:  aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating, MU_pct_sum, adj_comp_pct, co_acres
CREATE TABLE #M8
    ( aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT,
    cokey INT,
    compname CHAR(60),
    comppct_r INT,
    rating CHAR(60),
    MU_pct_sum INT,
    adj_comp_pct FLOAT,
    co_acres FLOAT
    );
 
-- Aggregated rating class values and sum of component acres  by landunit (Tract and Field number)
CREATE TABLE #M10
    ( landunit CHAR(20),
    rating CHAR(60),
    rating_acres FLOAT
    );
 
--Determines the Low, Rv, and High range for Hydric
CREATE TABLE #Hydric2
(mukey INT,
hydric_rating CHAR (25),
low_pct FLOAT,
rv_pct FLOAT,
high_pct FLOAT);
 
CREATE TABLE #Hydric3
(aoiid INT,
landunit CHAR(20),
attributename CHAR(60),
AOI_Acres FLOAT,
rating CHAR(60),
rating_key CHAR(60),
mukey INT,
hydric_flag INT,
low_acres FLOAT,
rv_acres FLOAT,
high_acres  FLOAT);
 
-- Create a table containing neccessary interp data
-- Please note that if we instead get ruledesign from sdvattribute, those values change to integer as in 1:limitation, 2:suitability
CREATE TABLE #SDV
(attributekey BIGINT,
attributename CHAR(60),
attributetablename CHAR(30),
attributecolumnname CHAR(30),
attributelogicaldatatype CHAR(20),
attributefieldsize SMALLINT,
attributeprecision TINYINT,
attributedescription NVARCHAR(MAX),
attributeuom NVARCHAR(60),
attributeuomabbrev NVARCHAR(30),
attributetype CHAR(20),
nasisrulename CHAR(60),
ruledesign NVARCHAR(60),
notratedphrase CHAR(15),
mapunitlevelattribflag TINYINT,
complevelattribflag TINYINT,
cmonthlevelattribflag TINYINT,
horzlevelattribflag TINYINT,
tiebreakdomainname CHAR(40),
tiebreakruleoptionflag TINYINT,
tiebreaklowlabel CHAR(20),
tiebreakhighlabel CHAR(20),
tiebreakrule SMALLINT,
resultcolumnname CHAR(10),
sqlwhereclause CHAR(255),
primaryconcolname CHAR(30),
pcclogicaldatatype CHAR(20),
primaryconstraintlabel CHAR(30),
secondaryconcolname CHAR(30),
scclogicaldatatype CHAR(20),
secondaryconstraintlabel CHAR(30),
dqmodeoptionflag TINYINT,
depthqualifiermode CHAR(20),
layerdepthtotop FLOAT,
layerdepthtobottom FLOAT,
layerdepthuom CHAR(20),
monthrangeoptionflag TINYINT,
beginningmonth CHAR(9),
endingmonth CHAR(9),
horzaggmeth CHAR(30),
interpnullsaszerooptionflag TINYINT,
interpnullsaszeroflag TINYINT,
nullratingreplacementvalue CHAR(254),
basicmodeflag TINYINT,
maplegendkey SMALLINT,
maplegendclasses TINYINT,
maplegendxml XML,
nasissiteid BIGINT,
wlupdated DATETIME,
algorithmname CHAR(50),
componentpercentcutoff TINYINT,
readytodistribute TINYINT,
effectivelogicaldatatype CHAR(20),
rulekey CHAR(30)
);
 
-- Create a table containing the first six rating classes for each interp
CREATE TABLE #RatingClasses
(attributename CHAR(60),
ruledesign CHAR(60),
rating1 CHAR(60),
rating2 CHAR(60),
rating3 CHAR(60),
rating4 CHAR(60),
rating5 CHAR(60),
rating6 CHAR(60)
);
 
-- Create a table containing the first six rating classes for each interp
CREATE TABLE #RatingDomain
(id INT IDENTITY (1,1),
rating_key CHAR(60),
attributename CHAR(60),
rating CHAR(60),
rating_num INT
);
 
-- Create table to store survey area datestamps (sacatalog.saverest)
CREATE TABLE #DateStamps
(landunit CHAR(20),
datestamp VARCHAR(32));
 
-- Create table to store landunit metadata (survey area and saverest) which comes from #DateStamps
CREATE TABLE #LandunitMetadata
(landunit CHAR(20),
soils_metadata VARCHAR(150)
);
 
-- End of CREATE TABLE section
 
-- Begin populating static tables. These are for the base soils data and metadata. No interp data yet.
--
-- Populate #SDV with interp metadata
-- I would like to incorporate the same information (and perhaps more) for soil properties. The table can incorporate everything thing that sdvattribute contains.
INSERT INTO #SDV (attributename, nasisrulename, rulekey, ruledesign, notratedphrase, resultcolumnname, maplegendxml, attributedescription)
SELECT sdv.attributename, sdv.nasisrulename, md.rulekey, md.ruledesign, sdv.notratedphrase, sdv.resultcolumnname, sdv.maplegendxml, sdv.attributedescription
FROM sdvattribute sdv
LEFT OUTER JOIN distinterpmd md ON sdv.nasisrulename = md.rulename
WHERE sdv.attributename IN ('Agricultural Organic Soil Subsidence', 'Soil Susceptibility to Compaction', 'Organic Matter Depletion', 'Surface Salt Concentration', 'Hydric Rating by Map Unit', 'Suitability for Aerobic Soil Organisms')
GROUP BY md.rulekey, sdv.attributename, sdv.nasisrulename, sdv.resultcolumnname, md.ruledesign, sdv.notratedphrase, sdv.maplegendxml, sdv.attributedescription;
 
INSERT INTO #AoiAcres (aoiid, landunit, landunit_acres )
SELECT  aoiid, landunit,
SUM( ROUND( ( ( GEOGRAPHY::STGeomFromWKB(aoigeom.STAsBinary(), 4326 ).STArea() ) / 4046.8564224 ), 3 ) ) AS landunit_acres
FROM #AoiTable
GROUP BY aoiid, landunit;
 
-- Populate intersected soil polygon table with geometry
INSERT INTO #AoiSoils (aoiid, landunit, mukey, soilgeom)
SELECT A.aoiid, A.landunit, M.mukey, M.mupolygongeo.STIntersection(A.aoigeom ) AS soilgeom
FROM mupolygon M, #AoiTable A
WHERE mupolygongeo.STIntersects(A.aoigeom) = 1;
 
-- Populate Soil geometry with landunit attribute
INSERT INTO #AoiSoils2   
SELECT aoiid, polyid, landunit,  mukey, ROUND((( GEOGRAPHY::STGeomFromWKB(soilgeom.STAsBinary(), 4326 ).STArea() ) / 4046.8564224 ), 3 ) AS poly_acres, GEOGRAPHY::STGeomFromWKB(soilgeom.STAsBinary(), 4326 ) AS soilgeog 
FROM #AoiSoils;
 
-- Populate soil map unit acres, aggregated by mukey (merges polygons together)
INSERT INTO #M2
SELECT DISTINCT M1.aoiid, M1.landunit, M1.mukey,
ROUND (SUM (M1.poly_acres) OVER(PARTITION BY M1.landunit, M1.mukey), 3) AS mapunit_acres
FROM #AoiSoils2 AS M1
GROUP BY M1.aoiid, M1.landunit, M1.mukey, M1.poly_acres;
 
---Farm Class
INSERT INTO #FC
SELECT aoiid, landunit, mu.mukey, mapunit_acres,  CASE WHEN (farmlndcl) IS NULL  THEN '---'
                        WHEN farmlndcl =  'All areas are prime farmland' THEN 'Prime farmland' 
                        WHEN farmlndcl LIKE 'Prime if%' THEN 'Prime farmland if'
                        WHEN farmlndcl =  'Farmland of statewide importance' THEN 'State importance' 
						WHEN farmlndcl LIKE  'Farmland of statewide importance, if%' THEN 'State importance if' 
                        WHEN farmlndcl = 'Farmland of local importance' THEN 'Local importance' 
						WHEN farmlndcl LIKE 'Farmland of local importance, if%' THEN 'Local importance if' 
                        WHEN farmlndcl = 'Farmland of unique importance' THEN 'Unique importance' ELSE 'Not Prime farmland' END AS farmlndclass
FROM #M2 AS fcc
INNER JOIN mapunit AS mu ON mu.mukey=fcc.mukey;
 
-- Populate component level data with cokey, comppct_r and mapunit sum-of-comppct_r
-- #M4 columns: aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, majcompflag
INSERT INTO #M4
SELECT M2.aoiid, M2.landunit, M2.mukey, mapunit_acres, CO.cokey, CO.compname, CO.comppct_r, CO.majcompflag, SUM (CO.comppct_r) OVER(PARTITION BY M2.landunit, M2.mukey) AS mu_pct_sum
FROM #M2 AS M2
INNER JOIN component AS CO ON CO.mukey = M2.mukey AND majcompflag = 'Yes'; --keep major component flag as Yes. It will mess up everything below
 
-- Get survey area dates for all soil mapunits involved
INSERT INTO #DateStamps
SELECT DISTINCT AM.landunit, ([SC].[areasymbol] + ' ' + CONVERT(VARCHAR(32),[SC].[saverest],120) ) AS datestamp
FROM #M4 AM
INNER JOIN mapunit Mu ON AM.mukey = Mu.mukey
INNER JOIN legend LG ON Mu.lkey = LG.lkey
INNER JOIN sacatalog SC ON Lg.areasymbol = SC.areasymbol;
 
-- Populate landunit soils-metadata
-- 
INSERT INTO #LandunitMetadata
SELECT DISTINCT
landunit,
STUFF((SELECT ' | ' + CAST([datestamp] AS VARCHAR(30))
FROM #DateStamps dt2
WHERE dt1.landunit = dt2.landunit
FOR XML PATH ('') ), 1, 2, '') AS soils_metadata
FROM #DateStamps dt1;
 
-- END OF STATIC SECTION
-- ************************************************************************************************
--Begin Aggregate Aggregate Stability

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
  FORMAT (CAST ((100*(-0.0126+0.01475*sar_l))/(1+(-0.0126+0.01475*sar_l)) as float)  , '#,###,##0.00')  as esp_l,
 FORMAT (CAST ((100*(-0.0126+0.01475*sar_r))/(1+(-0.0126+0.01475*sar_r)) as float) , '#,###,##0.00')  as esp_r,
 FORMAT (CAST ((100*(-0.0126+0.01475*sar_h))/(1+(-0.0126+0.01475*sar_h)) as float)  , '#,###,##0.00')  as esp_h, 
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
landunit_acres FLOAT, 
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
landunit_acres,
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
tcl,  mu_pct_sum, (1.0 * comppct_r / mu_pct_sum) AS adj_comp_pct, CASE WHEN hzdepb_r IS NULL THEN 0
WHEN hzdept_r IS NULL THEN 0 ELSE hzdepb_r-hzdept_r END AS thickness, 
CASE  WHEN hzdept_r < 15 then hzdept_r ELSE 0 END AS AGG_InRangeTop_0_15, 
CASE  WHEN hzdepb_r <= 15 THEN hzdepb_r WHEN hzdepb_r > 15 and hzdept_r < 15 THEN 15 ELSE 0 END AS AGG_InRangeBot_0_15
FROM #AoiAcres
LEFT OUTER JOIN #agg3 AS ag ON ag.aoiid=#AoiAcres.aoiid WHERE majcompflag = 'Yes' GROUP BY ag.aoiid ,
ag.landunit, 
landunit_acres,
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
landunit_acres FLOAT, 
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
landunit_acres,
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
WHEN AGG_InRangeBot_0_15 IS NULL THEN 0 ELSE AGG_InRangeBot_0_15 - AGG_InRangeTop_0_15 END) over(PARTITION BY cokey, aoiid) AS InRangeSumThickness
FROM #agg4
GROUP BY aoiid ,
landunit, 
landunit_acres,
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
landunit_acres FLOAT,
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
landunit_acres,
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
SUM ((CAST (InRangeThickness AS FLOAT)/CAST (InRangeSumThickness AS FLOAT)) * AgStab_l)  over(PARTITION BY ag5.cokey, aoiid) AS comp_weighted_average_l,
SUM((CAST (InRangeThickness AS FLOAT)/CAST (InRangeSumThickness AS FLOAT)) * AgStab_r)  over(PARTITION BY ag5.cokey, aoiid) AS comp_weighted_average_r,
SUM((CAST (InRangeThickness AS FLOAT)/CAST (InRangeSumThickness AS FLOAT)) * AgStab_h)  over(PARTITION BY ag5.cokey, aoiid) comp_weighted_average_h
FROM  #agg5 AS ag5 GROUP BY aoiid, landunit, 
landunit_acres,
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
landunit_acres,
mukey,
mapunit_acres, 
mu_pct_sum,
--AgStab_l ,
--AgStab_r , 
--AgStab_h ,
 FORMAT ( SUM (adj_comp_pct * comp_weighted_average_l) over(PARTITION BY ag6.mukey, aoiid )  , '#,###,##0.00') AS MU_SUM_AGG_L,
FORMAT (SUM (adj_comp_pct * comp_weighted_average_r) over(PARTITION BY ag6.mukey, aoiid )  , '#,###,##0.00') AS MU_SUM_AGG_R,
FORMAT (SUM (adj_comp_pct * comp_weighted_average_h) over(PARTITION BY ag6.mukey, aoiid )  , '#,###,##0.00') ASMU_SUM_AGG_H
FROM #agg6 AS ag6
GROUP BY aoiid ,
landunit, 
landunit_acres,
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

--flooding frequency  and Ponding frequency 
---The assessment will trigger a soil data web service to determine flood frequency rating of occasional, frequent, or very frequent 

-- Water Table
CREATE TABLE #pf
( aoiid INT, 
 landunit CHAR(20), 
 mukey INT, 
 mapunit_acres FLOAT, 
 cokey INT , 
 cname CHAR(60), 
 copct  INT, 
 majcompflag CHAR(3), 
 flodfreq CHAR(20), 
  pondfreq CHAR(20), 
 mu_pct_sum INT);

INSERT INTO #pf
SELECT DISTINCT
aoiid, 
landunit, 
M44.mukey, 
 FORMAT ( mapunit_acres  , '#,###,##0.00') AS mapunit_acres , 
M44.cokey AS cokey, 
M44.compname AS cname, 
M44.comppct_r AS copct ,
M44.majcompflag AS majcompflag,
(SELECT TOP 1 flodfreqcl FROM comonth, MetadataDomainMaster AS  MD, MetadataDomainDetail AS DD WHERE comonth.cokey = M44.cokey and flodfreqcl = ChoiceLabel and DomainName = 'flooding_frequency_class' and 
MD.DomainID = DD.DomainID order by choicesequence desc) as flodfreq,
(SELECT TOP 1 pondfreqcl FROM  comonth, MetadataDomainMaster AS  MD, MetadataDomainDetail AS DD WHERE comonth.cokey = M44.cokey and pondfreqcl = ChoiceLabel and DomainName = 'ponding_frequency_class' and 
MD.DomainID = DD.DomainID order by choicesequence desc) as pondfreq,
mu_pct_sum
FROM #M4 AS M44 
INNER JOIN comonth AS CM ON M44.cokey = CM.cokey AND M44.majcompflag = 'Yes' 
AND CASE 
WHEN (flodfreqcl IN ('occasional', 'common', 'frequent', 'very frequent'))  THEN 1 
WHEN (pondfreqcl IN ('occasional', 'common', 'frequent'))  THEN 1
ELSE 2 END  = 1
GROUP BY aoiid, landunit, M44.mukey, mapunit_acres,mu_pct_sum, M44.cokey,M44.compname , M44.majcompflag, M44.comppct_r, flodfreqcl, pondfreqcl


CREATE TABLE #pf1
( aoiid INT, 
 landunit CHAR(20), 
  landunit_acres FLOAT,
 mukey INT, 
 mapunit_acres FLOAT, 
  cokey INT , 
 cname CHAR(60), 
 copct  INT, 
 majcompflag CHAR(3), 
 flodfreq CHAR(20), 
  pondfreq CHAR(20), 
 mu_pct_sum INT,
  adj_comp_pct FLOAT
      );

INSERT INTO #pf1
SELECT DISTINCT pf.aoiid, pf.landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct, majcompflag, flodfreq, pondfreq ,  mu_pct_sum, (1.0 * copct / mu_pct_sum) AS adj_comp_pct
FROM #AoiAcres
LEFT OUTER JOIN #pf AS pf ON pf.aoiid=#AoiAcres.aoiid
GROUP BY  pf.aoiid, pf.landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct, majcompflag, flodfreq, pondfreq ,  mu_pct_sum,  mu_pct_sum

CREATE TABLE #pf2
    ( aoiid INT,
    landunit CHAR(20),
	landunit_acres FLOAT, 
    mukey INT,
    mapunit_acres FLOAT,
    cokey INT,
    cname CHAR(60),
    copct INT,
    MU_pct_sum INT,
    adj_comp_pct FLOAT,
    co_acres FLOAT
    );

TRUNCATE TABLE #pf2
INSERT INTO #pf2
SELECT  aoiid, landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct,  MU_pct_sum, adj_comp_pct, ROUND ( (adj_comp_pct * mapunit_acres), 2) AS co_acres
FROM #pf1;

--End Ponding and Flooding

--Begin Water
-- Water Table
CREATE TABLE #wet
( aoiid INT, 
 landunit CHAR(20), 
 mukey INT, 
 mapunit_acres FLOAT, 
 cokey INT , 
 cname CHAR(60), 
 copct  INT, 
 majcompflag CHAR(3), 
 soimoistdept_l INT, 
 soimoistdept_r INT,
 soimoiststat CHAR(7), 
 MIN_soimoistdept_l  INT, 
 MIN_soimoistdept_r INT,
 mu_pct_sum INT

      );

INSERT INTO #wet
SELECT 
aoiid, 
landunit, 
M44.mukey, 
mapunit_acres, 
M44.cokey AS cokey, 
M44.compname AS cname, 
M44.comppct_r AS copct ,
M44.majcompflag AS majcompflag, 
soimoistdept_l, 
soimoistdept_r,
soimoiststat, 
MIN (soimoistdept_l) over(partition by M44.cokey) AS  MIN_soimoistdept_l,
MIN (soimoistdept_r) over(partition by M44.cokey) AS  MIN_soimoistdept_r,
mu_pct_sum
FROM (#M4 AS M44 INNER JOIN (comonth AS CM  INNER JOIN  cosoilmoist   AS COSM  ON COSM.comonthkey=CM.comonthkey AND soimoiststat = 'Wet' AND CASE WHEN soimoistdept_l < 46 THEN 1 WHEN soimoistdept_r < 46 THEN 1 ELSE 2 END = 1
) ON M44.cokey = CM.cokey AND M44.majcompflag = 'Yes' 
INNER JOIN component ON  M44.cokey=component.cokey 
AND (CASE WHEN soimoistdept_l IS NULL THEN soimoistdept_r ELSE soimoistdept_l END) = (SELECT MIN (CASE WHEN soimoistdept_l IS NULL THEN soimoistdept_r ELSE soimoistdept_l END) 
FROM comonth AS CM2  
INNER JOIN  cosoilmoist  AS COSM2  ON COSM2.comonthkey=CM2.comonthkey AND soimoiststat = 'Wet' AND CASE WHEN soimoistdept_l < 46 THEN 1 WHEN soimoistdept_r < 46 THEN 1 ELSE 2 END = 1  AND  CM2.cokey=M44.cokey
))
WHERE CASE 
WHEN (taxorder = 'gelisols'  AND taxtempcl IN ('hypergelic', 'pergelic', 'subgelic') AND CM.month IN ('jul', 'aug')) THEN 1 
WHEN (taxtempregime IN ('cryic', 'pergelic', 'isofrigid') AND CM.month  IN ('jul', 'aug')) THEN 1 
WHEN (taxtempregime IN ('frigid') AND CM.month IN ('may', 'jun', 'jul', 'aug', 'sep')) THEN 1
WHEN (taxtempregime IN ('mesic') AND CM.month IN ( 'apr','may', 'jun', 'jul', 'aug', 'sep', 'oct')) THEN 1
WHEN (taxtempregime IN ('thermic', 'hyperthermic') and CM.month IN ('mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct'))THEN 1
WHEN (taxtempregime IN ('isothermic', 'isohyperthermic', 'isomesic') AND CM.month IN ('feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov')) THEN 1
WHEN (CM.month IN ('jun', 'jul')) THEN 1
ELSE 2 END  = 1


CREATE TABLE #wet1
( aoiid INT, 
 landunit CHAR(20), 
 landunit_acres FLOAT,
 mukey INT, 
 mapunit_acres FLOAT, 
 cokey INT , 
 cname CHAR(60), 
 copct  INT, 
 majcompflag CHAR(3), 
 MIN_soimoistdept_l  INT, 
 MIN_soimoistdept_r INT,
 mu_pct_sum INT,
  adj_comp_pct FLOAT
      );

INSERT INTO #wet1
SELECT DISTINCT wet.aoiid, wet.landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct, majcompflag,  MIN_soimoistdept_l, MIN_soimoistdept_r, mu_pct_sum, (1.0 * copct / mu_pct_sum) AS adj_comp_pct
FROM #AoiAcres
LEFT OUTER JOIN #wet AS wet ON wet.aoiid=#AoiAcres.aoiid
GROUP BY  wet.aoiid,  wet.landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct, majcompflag, MIN_soimoistdept_r, MIN_soimoistdept_l, mu_pct_sum

CREATE TABLE #wet2
    ( aoiid INT,
    landunit CHAR(20),
	landunit_acres FLOAT, 
    mukey INT,
    mapunit_acres FLOAT,
    cokey INT,
    cname CHAR(60),
    copct INT,
    MU_pct_sum INT,
    adj_comp_pct FLOAT,
    co_acres FLOAT
    );

TRUNCATE TABLE #wet2
INSERT INTO #wet2
SELECT  aoiid, landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct,  MU_pct_sum, adj_comp_pct, ROUND ( (adj_comp_pct * mapunit_acres), 4) AS co_acres
FROM #wet1;

-- Aggregated rating class values and sum of component acres  by landunit (Tract and Field number)
--CREATE TABLE #M10
 --   ( landunit CHAR(20),
 --   rating CHAR(60),
  --  rating_acres FLOAT
  --  );

-- Aggregates the classes and sums up the component acres  by landunit (Tract and Field number)
--TRUNCATE TABLE #M10
--INSERT INTO #M10


-- ************************************************************************************************
-- BEGIN QUERIES FOR SOIL PROPERTIES...
-- ************************************************************************************************

-- Hydric Rating begins here

-- Identify all hydric components, using table #M4.
-- These data will be used to generate a soils map, NOT landunit ratings.
CREATE TABLE #Hydric_A
    (mukey INT,
    cokey INT,
    hydric_pct INT
    );
 
-- #M4 columns: aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, majcompflag
INSERT INTO #Hydric_A (mukey, cokey, hydric_pct)
    SELECT DISTINCT M4.mukey, M4.cokey, M4.comppct_r AS hydric_pct
    FROM #M4 M4
    LEFT OUTER JOIN component C ON M4.cokey = C.cokey
    WHERE C.hydricrating = 'Yes';
 
-- Hydric soils at the mapunit level, using all components where hydricrating = 'Yes'.
-- Please note that any hydric components with a comppct_r of zero will not be counted.
CREATE TABLE #Hydric_B
    (mukey INT,
    hydric_pct INT
    );
 
INSERT INTO #Hydric_B (mukey, hydric_pct)
SELECT mukey, SUM(hydric_pct) AS hydric_pct
FROM #Hydric_A H1
GROUP BY mukey
ORDER BY mukey;
 
-- SELECT * FROM #Hydric_B;
 
-- 
-- End of mapunit hydric percent
 
-- Begin Jason's new Hydric queries here
--
-- Hydric soils at the Map Unit, using all map units from table #M2.
CREATE TABLE #Hydric1
(mukey INT,
comp_count INT,        -- cnt_comp
count_maj_comp INT,    -- cnt_mjr
all_hydric INT,        -- cnt_hydric
all_not_hydric INT,    -- cnt_nonhydric
maj_hydric INT,        -- cnt_mjr_hydric
maj_not_hydric INT,    -- cnt_mjr_nonhydric
hydric_inclusions INT, -- cnt_minor_hydric
hydric_null INT);      -- cnt_null_hydric

-- Gets counts for major-minor components and different hydric ratings (Yes, No, NULL)
-- mukey,
-- total number of components,
-- number of major components,
-- total number of hydric components,
-- number of major hydric components,
-- number of major non-hydric components,
-- number of minor hydric components,
-- total number of non-hydric components,
-- number of components where hydric is null
--
INSERT INTO #Hydric1 (mukey, comp_count, count_maj_comp, all_hydric, all_not_hydric, maj_hydric, maj_not_hydric, hydric_inclusions, hydric_null)
SELECT DISTINCT M4.mukey,   
(SELECT TOP 1 COUNT(*)
 FROM mapunit
 INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey) AS comp_count,
 (SELECT TOP 1 COUNT(*)
 FROM mapunit
 INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey
 AND majcompflag = 'Yes') AS count_maj_comp,
 (SELECT TOP 1 COUNT(*)
 FROM mapunit
 INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey
 AND hydricrating = 'Yes' ) AS all_hydric,
 (SELECT TOP 1 COUNT(*)
 FROM mapunit
 INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey
 AND hydricrating  != 'Yes') AS all_not_hydric, 
 (SELECT TOP 1 COUNT(*)
 FROM mapunit
 INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey
 AND majcompflag = 'Yes' AND hydricrating = 'Yes') AS maj_hydric,
 (SELECT TOP 1 COUNT(*)
 FROM mapunit
 INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey
 AND majcompflag = 'Yes' AND hydricrating != 'Yes') AS maj_not_hydric,
 (SELECT TOP 1 COUNT(*)
 FROM mapunit
 INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey
 AND majcompflag != 'Yes' AND hydricrating  = 'Yes' ) AS hydric_inclusions,
 (SELECT TOP 1 COUNT(*)
 FROM mapunit
 INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey
 AND hydricrating  IS NULL ) AS hydric_null 
FROM #M4 AS M4;

-- Diagnostic
-- SELECT * FROM #Hydric1
 
-- Takes hydric count statistics and converts them to interpretation-type rating classes (hydric_rating)
-- Also assigns fuzzy-type values as rating percents. These will be used later in a calculation involving
-- mapunit acres. If a hydricrating of 'Error' or rating number of 0.0 is returned, there is an error that needs to be checked.
--
INSERT INTO #Hydric2 (mukey, hydric_rating, low_pct, rv_pct, high_pct)
SELECT  
mukey,
CASE WHEN comp_count = all_not_hydric + hydric_null THEN 'Nonhydric' 
WHEN comp_count = all_hydric  THEN 'Hydric' 
WHEN comp_count != all_hydric AND count_maj_comp = maj_hydric THEN 'Predominantly hydric' 
WHEN hydric_inclusions >= 0.5 AND  maj_hydric < 0.5 THEN  'Predominantly nonydric' 
WHEN maj_not_hydric >= 0.5  AND  maj_hydric >= 0.5 THEN 'Partially hydric'
ELSE 'Error'
END AS hydric_rating, 
 
CASE WHEN comp_count = all_not_hydric + hydric_null THEN 0.00 --'Nonhydric' 
WHEN comp_count = all_hydric  THEN 1 --'Hydric' 
WHEN comp_count != all_hydric AND count_maj_comp = maj_hydric THEN 0.80 --'Predominantly hydric' 
WHEN hydric_inclusions >= 0.5 AND  maj_hydric < 0.5 THEN 0.01 --'Predominantly nonydric' 
WHEN maj_not_hydric >= 0.5  AND maj_hydric >= 0.5 THEN 0.15 --'Partially hydric' 
ELSE 0.00 --'Error' 
END AS low_pct, 
 
CASE WHEN comp_count = all_not_hydric + hydric_null THEN 0.00 --'Nonhydric' 
WHEN comp_count = all_hydric  THEN 1 --'Hydric' 
WHEN comp_count != all_hydric AND count_maj_comp = maj_hydric THEN 0.85 --'Predominantly hydric' 
WHEN hydric_inclusions >= 0.5 AND  maj_hydric < 0.5 THEN 0.05 --'Predominantly nonydric' 
WHEN maj_not_hydric >= 0.5  AND  maj_hydric >= 0.5 THEN  0.50 --'Partially hydric' 
ELSE 0.00 --'Error' 
END AS rv_pct, 
 
CASE WHEN comp_count = all_not_hydric + hydric_null THEN 0.00 --'Nonhydric' 
WHEN comp_count = all_hydric  THEN 1 --'Hydric' 
WHEN comp_count != all_hydric AND count_maj_comp = maj_hydric THEN 0.99 --'Predominantly hydric' 
WHEN hydric_inclusions >= 0.5 AND maj_hydric < 0.5 THEN 0.20 --'Predominantly nonydric' 
WHEN maj_not_hydric >= 0.5  AND maj_hydric >= 0.5 THEN  0.79 --'Partially hydric' 
ELSE 0.00 --'Error' 
END AS high_pct
FROM #Hydric1;

INSERT INTO #Hydric3 ( aoiid, landunit, attributename, aoi_acres, mukey, hydric_flag, low_acres, rv_acres, high_acres)
SELECT DISTINCT aoiid,
landunit,
'Hydric Interp' AS attributename,
ROUND (SUM (mapunit_acres ) OVER(PARTITION BY aoiid), 2) AS aoi_acres,
H3.mukey,
CASE WHEN hydric_rating = 'Nonhydric' THEN 0 ELSE 1 END AS hydric_flag,
mapunit_acres * low_pct AS low_acres, 
mapunit_acres * rv_pct AS rv_acres , 
mapunit_acres * high_pct AS high_acres  
FROM #Hydric2 AS H3
INNER JOIN #M2 AS MH2 ON MH2.mukey = H3.mukey
GROUP BY aoiid, landunit, H3.mukey, mapunit_acres, hydric_rating, low_pct, rv_pct, high_pct




 
--
-- End Jason's new hydric interpretation queries here

-- Populate the #SDV table with information for Hydric Rating by Map Unit

 
--
-- Hydric Rating ends here
 
-- ************************************************************************************************
-- END OF QUERIES FOR SOIL PROPERTIES...
-- ************************************************************************************************
 

-- ************************************************************************************************
-- Begin query for soil interpretation:  Surface Salt Concentration 
-- ************************************************************************************************
 
SELECT @attributeName = 'Surface Salt Concentration';
SELECT @minPct = 10;
SELECT @minAcres = 10;
 
-- Get ordered set of interphrc values from sdvattribute.maplegendxml. This is assumed to begin with the 'worst' rating. Need to double-check this for all interps.
SELECT @rating1 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[1]', 'VARCHAR(100)');
SELECT @rating2 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[2]', 'VARCHAR(100)');
SELECT @rating3 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[3]', 'VARCHAR(100)');
SELECT @rating4 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[4]', 'VARCHAR(100)');
SELECT @rating5 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[5]', 'VARCHAR(100)');
SELECT @rating6 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[6]', 'VARCHAR(100)');
 
-- Set interp rulekey and ruledesign as a variable to be used in cointerp query
SELECT @ruleKey = (SELECT rulekey FROM #SDV WHERE attributename = @attributeName);
SELECT @ruleDesign = (SELECT ruledesign FROM #SDV WHERE attributename = @attributeName)
SELECT @notRatedPhrase = (SELECT notratedphrase FROM #SDV WHERE attributename = @attributeName);

-- Add Not rated phrase to @rating variables
IF @notRatedPhrase IS NOT NULL
  IF @rating1 IS NULL (SELECT @rating1 = @notRatedPhrase)
  ELSE 
    IF @rating2 IS NULL (SELECT @rating2 = @notRatedPhrase)
    ELSE
      IF @rating3 IS NULL (SELECT @rating3 = @notRatedPhrase)
      ELSE
        IF @rating4 IS NULL (SELECT @rating4 = @notRatedPhrase)
        ELSE 
          IF @rating5 IS NULL (SELECT @rating5 = @notRatedPhrase)
          ELSE
            IF @rating6 IS NULL (SELECT @rating6 = @notRatedPhrase)

-- Append the rating classes for this interp to the #RatingClasses table
INSERT INTO #RatingClasses (attributename, ruledesign, rating1, rating2, rating3, rating4, rating5, rating6)
SELECT @attributeName AS attributename, @ruleDesign AS ruledesign, @rating1 AS rating1, @rating2 AS rating2, @rating3 AS rating3, @rating4 AS rating4, @rating5 AS rating5, @rating6 AS rating6;
 
-- Populate the #RatingDomain table with a unique rating_key for this interp
SELECT @ratingKey = RTRIM(@attributeName) + ':1'
IF NOT @rating1 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating1, 1)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':2'
IF NOT @rating2 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating2, 2)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':3'
IF NOT @rating3 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating3, 3)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':4'
IF NOT @rating4 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating4, 4)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':5'
IF NOT @rating5 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating5, 5)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':6'
IF NOT @rating6 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating6, 6)
 
-- Populate component level ratings using the currently set soil interpretation
TRUNCATE TABLE #M5
INSERT INTO #M5
SELECT M4.aoiid, M4.landunit, M4.mukey, mapunit_acres, M4.cokey, M4.compname, M4.comppct_r, TP.interphrc AS rating, SUM (M4.comppct_r) OVER(PARTITION BY M4.landunit, M4.mukey) AS mu_pct_sum
FROM #M4 AS M4
LEFT OUTER JOIN cointerp AS TP ON M4.cokey = TP.cokey AND rulekey = @ruleKey
WHERE M4.majcompflag = 'Yes';
 
-- Populate component level ratings with adjusted component percent to account for the un-used minor components
-- Can I use this table to determine the dominant interphrc-condition for each mapunit???
TRUNCATE TABLE #M6
INSERT INTO #M6
SELECT aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating, mu_pct_sum, (1.0 * comppct_r / mu_pct_sum) AS adj_comp_pct
FROM #M5;
 
-- Populates component acres by multiplying map unit acres with adjusted component percent
TRUNCATE TABLE #M8
INSERT INTO #M8
SELECT  aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating, MU_pct_sum, adj_comp_pct, ROUND ( (adj_comp_pct * mapunit_acres), 4) AS co_acres
FROM #M6;
 
-- Aggregates the classes and sums up the component acres  by landunit (Tract and Field number)
TRUNCATE TABLE #M10
INSERT INTO #M10
SELECT landunit, rating, SUM (co_acres) AS rating_acres
FROM #M8
GROUP BY landunit, rating
ORDER BY landunit, rating_acres DESC;
 
-- Group of insert statements to populate the final output tables
 
-- Detailed Landunit Ratings1: rating acres and rating percent by area for each soil-landunit polygon
-- These will be summarized to a single set of interp ratings for each landunit. Currently there are 4 interps.
INSERT INTO #LandunitRatingsDetailed1 (aoiid, landunit, attributename, rating, rating_key, rating_num, rating_pct, rating_acres, landunit_acres)
SELECT aoiid, M10.landunit, @attributeName AS attributename, M10.rating, RD.rating_key, RD.rating_num,
ROUND ((rating_acres/ landunit_acres) * 100.0, 2) AS rating_pct, 
ROUND (rating_acres,2) AS rating_acres,
ROUND ( landunit_acres, 2) AS landunit_acres
FROM #M10 M10
LEFT OUTER JOIN #AoiAcres ON #AoiAcres.landunit = M10.landunit
INNER JOIN #RatingDomain RD ON M10.rating = RD.rating
WHERE RD.attributename = @attributeName
GROUP BY aoiid, M10.landunit, M10.rating, rating_key, rating_acres, landunit_acres, rating_num
ORDER BY landunit, attributename, rating_num DESC;
 
-- #LandunitRatingsDetailed2 is populated with all information plus rolling_pct and rolling_acres which are using in the landunit summary rating.
-- Detailed Landunit Ratings2 table columns: landunit, attributename, rating, rating_key, rating_num, rating_pct, rating_acres, landunit_acres, rolling_pct, rolling_acres 
INSERT INTO #LandunitRatingsDetailed2 (landunit, attributename, rating, rating_num, rating_key, rating_pct, rating_acres, landunit_acres, rolling_pct, rolling_acres)
SELECT landunit, attributename, rating, rating_num, rating_key, rating_pct, rating_acres, landunit_acres,
  rolling_pct = SUM(rating_pct) OVER
  (
    PARTITION BY landunit
    ORDER BY rating_key ROWS UNBOUNDED PRECEDING
  ),
  rolling_acres = SUM(rating_acres) OVER
  (
    PARTITION BY landunit
    ORDER BY rating_key ROWS UNBOUNDED PRECEDING
  )
  FROM #LandunitRatingsDetailed1
  WHERE attributename = @attributeName
  ORDER BY landunit, attributename;

-- SELECT * FROM #LandunitRatingsDetailed2 WHERE attributename = @attributeName;
 
-- CART
-- #LandunitRatingsCART
-- Identifies the single, most limiting rating (per landunit) that comprises at least 10% by area or 10 acres.
-- This record will have an id value of 1.
INSERT INTO #LandunitRatingsCART (id, landunit, attributename, rating, rating_key, rolling_pct, rolling_acres, landunit_acres)
SELECT ROW_NUMBER() OVER(PARTITION BY landunit ORDER BY rating_key ASC) AS "id",
landunit, attributename, rating, rating_key, rolling_pct, rolling_acres, landunit_acres
FROM #LandunitRatingsDetailed2
WHERE attributename = @attributeName AND (rolling_pct >= @minPct OR rolling_acres >= @minAcres)
 
-- SELECT * FROM #LandunitRatingsCART WHERE attributename = @attributeName;

-- End of:  Surface Salt Concentration 
-- ************************************************************************************************

-- ************************************************************************************************
-- Begin query for soil interpretation:  Soil Susceptibility to Compaction 
-- ************************************************************************************************
 
SELECT @attributeName = 'Soil Susceptibility to Compaction';
SELECT @minPct = 10;
SELECT @minAcres = 10;
 
-- Get ordered set of interphrc values from sdvattribute.maplegendxml. This is assumed to begin with the 'worst' rating. Need to double-check this for all interps.
SELECT @rating1 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[1]', 'VARCHAR(100)');
SELECT @rating2 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[2]', 'VARCHAR(100)');
SELECT @rating3 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[3]', 'VARCHAR(100)');
SELECT @rating4 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[4]', 'VARCHAR(100)');
SELECT @rating5 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[5]', 'VARCHAR(100)');
SELECT @rating6 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[6]', 'VARCHAR(100)');
 
-- Set interp rulekey and ruledesign as a variable to be used in cointerp query
SELECT @ruleKey = (SELECT rulekey FROM #SDV WHERE attributename = @attributeName);
SELECT @ruleDesign = (SELECT ruledesign FROM #SDV WHERE attributename = @attributeName)
SELECT @notRatedPhrase = (SELECT notratedphrase FROM #SDV WHERE attributename = @attributeName);

-- Add Not rated phrase to @rating variables
IF @notRatedPhrase IS NOT NULL
  IF @rating1 IS NULL (SELECT @rating1 = @notRatedPhrase)
  ELSE 
    IF @rating2 IS NULL (SELECT @rating2 = @notRatedPhrase)
    ELSE
      IF @rating3 IS NULL (SELECT @rating3 = @notRatedPhrase)
      ELSE
        IF @rating4 IS NULL (SELECT @rating4 = @notRatedPhrase)
        ELSE 
          IF @rating5 IS NULL (SELECT @rating5 = @notRatedPhrase)
          ELSE
            IF @rating6 IS NULL (SELECT @rating6 = @notRatedPhrase)

-- Append the rating classes for this interp to the #RatingClasses table
INSERT INTO #RatingClasses (attributename, ruledesign, rating1, rating2, rating3, rating4, rating5, rating6)
SELECT @attributeName AS attributename, @ruleDesign AS ruledesign, @rating1 AS rating1, @rating2 AS rating2, @rating3 AS rating3, @rating4 AS rating4, @rating5 AS rating5, @rating6 AS rating6;
 
-- Populate the #RatingDomain table with a unique rating_key for this interp
SELECT @ratingKey = RTRIM(@attributeName) + ':1'
IF NOT @rating1 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating1, 1)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':2'
IF NOT @rating2 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating2, 2)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':3'
IF NOT @rating3 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating3, 3)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':4'
IF NOT @rating4 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating4, 4)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':5'
IF NOT @rating5 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating5, 5)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':6'
IF NOT @rating6 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating6, 6)
 
-- Populate component level ratings using the currently set soil interpretation
TRUNCATE TABLE #M5
INSERT INTO #M5
SELECT M4.aoiid, M4.landunit, M4.mukey, mapunit_acres, M4.cokey, M4.compname, M4.comppct_r, TP.interphrc AS rating, SUM (M4.comppct_r) OVER(PARTITION BY M4.landunit, M4.mukey) AS mu_pct_sum
FROM #M4 AS M4
LEFT OUTER JOIN cointerp AS TP ON M4.cokey = TP.cokey AND rulekey = @ruleKey
WHERE M4.majcompflag = 'Yes';
 
-- Populate component level ratings with adjusted component percent to account for the un-used minor components
-- Can I use this table to determine the dominant interphrc-condition for each mapunit???
TRUNCATE TABLE #M6
INSERT INTO #M6
SELECT aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating, mu_pct_sum, (1.0 * comppct_r / mu_pct_sum) AS adj_comp_pct
FROM #M5;
 
-- Populates component acres by multiplying map unit acres with adjusted component percent
TRUNCATE TABLE #M8
INSERT INTO #M8
SELECT  aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating, MU_pct_sum, adj_comp_pct, ROUND ( (adj_comp_pct * mapunit_acres), 4) AS co_acres
FROM #M6;
 
-- Aggregates the classes and sums up the component acres  by landunit (Tract and Field number)
TRUNCATE TABLE #M10
INSERT INTO #M10
SELECT landunit, rating, SUM (co_acres) AS rating_acres
FROM #M8
GROUP BY landunit, rating
ORDER BY landunit, rating_acres DESC;
 
-- Group of insert statements to populate the final output tables
 
-- Detailed Landunit Ratings1: rating acres and rating percent by area for each soil-landunit polygon
-- These will be summarized to a single set of interp ratings for each landunit. Currently there are 4 interps.
INSERT INTO #LandunitRatingsDetailed1 (aoiid, landunit, attributename, rating, rating_key, rating_num, rating_pct, rating_acres, landunit_acres)
SELECT aoiid, M10.landunit, @attributeName AS attributename, M10.rating, RD.rating_key, RD.rating_num,
ROUND ((rating_acres/ landunit_acres) * 100.0, 2) AS rating_pct, 
ROUND (rating_acres,2) AS rating_acres,
ROUND ( landunit_acres, 2) AS landunit_acres
FROM #M10 M10
LEFT OUTER JOIN #AoiAcres ON #AoiAcres.landunit = M10.landunit
INNER JOIN #RatingDomain RD ON M10.rating = RD.rating
WHERE RD.attributename = @attributeName
GROUP BY aoiid, M10.landunit, M10.rating, rating_key, rating_acres, landunit_acres, rating_num
ORDER BY landunit, attributename, rating_num DESC;
 
-- #LandunitRatingsDetailed2 is populated with all information plus rolling_pct and rolling_acres which are using in the landunit summary rating.
-- Detailed Landunit Ratings2 table columns: landunit, attributename, rating, rating_key, rating_num, rating_pct, rating_acres, landunit_acres, rolling_pct, rolling_acres 
INSERT INTO #LandunitRatingsDetailed2 (landunit, attributename, rating, rating_num, rating_key, rating_pct, rating_acres, landunit_acres, rolling_pct, rolling_acres)
SELECT landunit, attributename, rating, rating_num, rating_key, rating_pct, rating_acres, landunit_acres,
  rolling_pct = SUM(rating_pct) OVER
  (
    PARTITION BY landunit
    ORDER BY rating_key ROWS UNBOUNDED PRECEDING
  ),
  rolling_acres = SUM(rating_acres) OVER
  (
    PARTITION BY landunit
    ORDER BY rating_key ROWS UNBOUNDED PRECEDING
  )
  FROM #LandunitRatingsDetailed1
  WHERE attributename = @attributeName
  ORDER BY landunit, attributename;

-- SELECT * FROM #LandunitRatingsDetailed2 WHERE attributename = @attributeName;
 
-- CART
-- #LandunitRatingsCART
-- Identifies the single, most limiting rating (per landunit) that comprises at least 10% by area or 10 acres.
-- This record will have an id value of 1.
INSERT INTO #LandunitRatingsCART (id, landunit, attributename, rating, rating_key, rolling_pct, rolling_acres, landunit_acres)
SELECT ROW_NUMBER() OVER(PARTITION BY landunit ORDER BY rating_key ASC) AS "id",
landunit, attributename, rating, rating_key, rolling_pct, rolling_acres, landunit_acres
FROM #LandunitRatingsDetailed2
WHERE attributename = @attributeName AND (rolling_pct >= @minPct OR rolling_acres >= @minAcres)
 
-- SELECT * FROM #LandunitRatingsCART WHERE attributename = @attributeName;

-- End of:  Soil Susceptibility to Compaction 
-- ************************************************************************************************

-- ************************************************************************************************
-- Begin query for soil interpretation:  Organic Matter Depletion 
-- ************************************************************************************************
 
SELECT @attributeName = 'Organic Matter Depletion';
SELECT @minPct = 10;
SELECT @minAcres = 10;
 
-- Get ordered set of interphrc values from sdvattribute.maplegendxml. This is assumed to begin with the 'worst' rating. Need to double-check this for all interps.
SELECT @rating1 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[1]', 'VARCHAR(100)');
SELECT @rating2 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[2]', 'VARCHAR(100)');
SELECT @rating3 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[3]', 'VARCHAR(100)');
SELECT @rating4 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[4]', 'VARCHAR(100)');
SELECT @rating5 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[5]', 'VARCHAR(100)');
SELECT @rating6 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[6]', 'VARCHAR(100)');
 
-- Set interp rulekey and ruledesign as a variable to be used in cointerp query
SELECT @ruleKey = (SELECT rulekey FROM #SDV WHERE attributename = @attributeName);
SELECT @ruleDesign = (SELECT ruledesign FROM #SDV WHERE attributename = @attributeName)
SELECT @notRatedPhrase = (SELECT notratedphrase FROM #SDV WHERE attributename = @attributeName);

-- Add Not rated phrase to @rating variables
IF @notRatedPhrase IS NOT NULL
  IF @rating1 IS NULL (SELECT @rating1 = @notRatedPhrase)
  ELSE 
    IF @rating2 IS NULL (SELECT @rating2 = @notRatedPhrase)
    ELSE
      IF @rating3 IS NULL (SELECT @rating3 = @notRatedPhrase)
      ELSE
        IF @rating4 IS NULL (SELECT @rating4 = @notRatedPhrase)
        ELSE 
          IF @rating5 IS NULL (SELECT @rating5 = @notRatedPhrase)
          ELSE
            IF @rating6 IS NULL (SELECT @rating6 = @notRatedPhrase)

-- Append the rating classes for this interp to the #RatingClasses table
INSERT INTO #RatingClasses (attributename, ruledesign, rating1, rating2, rating3, rating4, rating5, rating6)
SELECT @attributeName AS attributename, @ruleDesign AS ruledesign, @rating1 AS rating1, @rating2 AS rating2, @rating3 AS rating3, @rating4 AS rating4, @rating5 AS rating5, @rating6 AS rating6;
 
-- Populate the #RatingDomain table with a unique rating_key for this interp
SELECT @ratingKey = RTRIM(@attributeName) + ':1'
IF NOT @rating1 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating1, 1)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':2'
IF NOT @rating2 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating2, 2)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':3'
IF NOT @rating3 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating3, 3)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':4'
IF NOT @rating4 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating4, 4)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':5'
IF NOT @rating5 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating5, 5)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':6'
IF NOT @rating6 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating6, 6)
 
-- Populate component level ratings using the currently set soil interpretation
TRUNCATE TABLE #M5
INSERT INTO #M5
SELECT M4.aoiid, M4.landunit, M4.mukey, mapunit_acres, M4.cokey, M4.compname, M4.comppct_r, TP.interphrc AS rating, SUM (M4.comppct_r) OVER(PARTITION BY M4.landunit, M4.mukey) AS mu_pct_sum
FROM #M4 AS M4
LEFT OUTER JOIN cointerp AS TP ON M4.cokey = TP.cokey AND rulekey = @ruleKey
WHERE M4.majcompflag = 'Yes';
 
-- Populate component level ratings with adjusted component percent to account for the un-used minor components
-- Can I use this table to determine the dominant interphrc-condition for each mapunit???
TRUNCATE TABLE #M6
INSERT INTO #M6
SELECT aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating, mu_pct_sum, (1.0 * comppct_r / mu_pct_sum) AS adj_comp_pct
FROM #M5;
 
-- Populates component acres by multiplying map unit acres with adjusted component percent
TRUNCATE TABLE #M8
INSERT INTO #M8
SELECT  aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating, MU_pct_sum, adj_comp_pct, ROUND ( (adj_comp_pct * mapunit_acres), 4) AS co_acres
FROM #M6;
 
-- Aggregates the classes and sums up the component acres  by landunit (Tract and Field number)
TRUNCATE TABLE #M10
INSERT INTO #M10
SELECT landunit, rating, SUM (co_acres) AS rating_acres
FROM #M8
GROUP BY landunit, rating
ORDER BY landunit, rating_acres DESC;
 
-- Group of insert statements to populate the final output tables
 
-- Detailed Landunit Ratings1: rating acres and rating percent by area for each soil-landunit polygon
-- These will be summarized to a single set of interp ratings for each landunit. Currently there are 4 interps.
INSERT INTO #LandunitRatingsDetailed1 (aoiid, landunit, attributename, rating, rating_key, rating_num, rating_pct, rating_acres, landunit_acres)
SELECT aoiid, M10.landunit, @attributeName AS attributename, M10.rating, RD.rating_key, RD.rating_num,
ROUND ((rating_acres/ landunit_acres) * 100.0, 2) AS rating_pct, 
ROUND (rating_acres,2) AS rating_acres,
ROUND ( landunit_acres, 2) AS landunit_acres
FROM #M10 M10
LEFT OUTER JOIN #AoiAcres ON #AoiAcres.landunit = M10.landunit
INNER JOIN #RatingDomain RD ON M10.rating = RD.rating
WHERE RD.attributename = @attributeName
GROUP BY aoiid, M10.landunit, M10.rating, rating_key, rating_acres, landunit_acres, rating_num
ORDER BY landunit, attributename, rating_num DESC;
 
-- #LandunitRatingsDetailed2 is populated with all information plus rolling_pct and rolling_acres which are using in the landunit summary rating.
-- Detailed Landunit Ratings2 table columns: landunit, attributename, rating, rating_key, rating_num, rating_pct, rating_acres, landunit_acres, rolling_pct, rolling_acres 
INSERT INTO #LandunitRatingsDetailed2 (landunit, attributename, rating, rating_num, rating_key, rating_pct, rating_acres, landunit_acres, rolling_pct, rolling_acres)
SELECT landunit, attributename, rating, rating_num, rating_key, rating_pct, rating_acres, landunit_acres,
  rolling_pct = SUM(rating_pct) OVER
  (
    PARTITION BY landunit
    ORDER BY rating_key ROWS UNBOUNDED PRECEDING
  ),
  rolling_acres = SUM(rating_acres) OVER
  (
    PARTITION BY landunit
    ORDER BY rating_key ROWS UNBOUNDED PRECEDING
  )
  FROM #LandunitRatingsDetailed1
  WHERE attributename = @attributeName
  ORDER BY landunit, attributename;

-- SELECT * FROM #LandunitRatingsDetailed2 WHERE attributename = @attributeName;
 
-- CART
-- #LandunitRatingsCART
-- Identifies the single, most limiting rating (per landunit) that comprises at least 10% by area or 10 acres.
-- This record will have an id value of 1.
INSERT INTO #LandunitRatingsCART (id, landunit, attributename, rating, rating_key, rolling_pct, rolling_acres, landunit_acres)
SELECT ROW_NUMBER() OVER(PARTITION BY landunit ORDER BY rating_key ASC) AS "id",
landunit, attributename, rating, rating_key, rolling_pct, rolling_acres, landunit_acres
FROM #LandunitRatingsDetailed2
WHERE attributename = @attributeName AND (rolling_pct >= @minPct OR rolling_acres >= @minAcres)
 
-- SELECT * FROM #LandunitRatingsCART WHERE attributename = @attributeName;

-- End of:  Organic Matter Depletion 
-- ************************************************************************************************

-- ************************************************************************************************
-- Begin query for soil interpretation:  Agricultural Organic Soil Subsidence 
-- ************************************************************************************************
 
SELECT @attributeName = 'Agricultural Organic Soil Subsidence';
SELECT @minPct = 10;
SELECT @minAcres = 10;
 
-- Get ordered set of interphrc values from sdvattribute.maplegendxml. This is assumed to begin with the 'worst' rating. Need to double-check this for all interps.
SELECT @rating1 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[1]', 'VARCHAR(100)');
SELECT @rating2 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[2]', 'VARCHAR(100)');
SELECT @rating3 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[3]', 'VARCHAR(100)');
SELECT @rating4 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[4]', 'VARCHAR(100)');
SELECT @rating5 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[5]', 'VARCHAR(100)');
SELECT @rating6 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[6]', 'VARCHAR(100)');
 
-- Set interp rulekey and ruledesign as a variable to be used in cointerp query
SELECT @ruleKey = (SELECT rulekey FROM #SDV WHERE attributename = @attributeName);
SELECT @ruleDesign = (SELECT ruledesign FROM #SDV WHERE attributename = @attributeName)
SELECT @notRatedPhrase = (SELECT notratedphrase FROM #SDV WHERE attributename = @attributeName);

-- Add Not rated phrase to @rating variables
IF @notRatedPhrase IS NOT NULL
  IF @rating1 IS NULL (SELECT @rating1 = @notRatedPhrase)
  ELSE 
    IF @rating2 IS NULL (SELECT @rating2 = @notRatedPhrase)
    ELSE
      IF @rating3 IS NULL (SELECT @rating3 = @notRatedPhrase)
      ELSE
        IF @rating4 IS NULL (SELECT @rating4 = @notRatedPhrase)
        ELSE 
          IF @rating5 IS NULL (SELECT @rating5 = @notRatedPhrase)
          ELSE
            IF @rating6 IS NULL (SELECT @rating6 = @notRatedPhrase)

-- Append the rating classes for this interp to the #RatingClasses table
INSERT INTO #RatingClasses (attributename, ruledesign, rating1, rating2, rating3, rating4, rating5, rating6)
SELECT @attributeName AS attributename, @ruleDesign AS ruledesign, @rating1 AS rating1, @rating2 AS rating2, @rating3 AS rating3, @rating4 AS rating4, @rating5 AS rating5, @rating6 AS rating6;
 
-- Populate the #RatingDomain table with a unique rating_key for this interp
SELECT @ratingKey = RTRIM(@attributeName) + ':1'
IF NOT @rating1 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating1, 1)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':2'
IF NOT @rating2 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating2, 2)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':3'
IF NOT @rating3 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating3, 3)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':4'
IF NOT @rating4 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating4, 4)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':5'
IF NOT @rating5 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating5, 5)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':6'
IF NOT @rating6 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating6, 6)
 
-- Populate component level ratings using the currently set soil interpretation
TRUNCATE TABLE #M5
INSERT INTO #M5
SELECT M4.aoiid, M4.landunit, M4.mukey, mapunit_acres, M4.cokey, M4.compname, M4.comppct_r, TP.interphrc AS rating, SUM (M4.comppct_r) OVER(PARTITION BY M4.landunit, M4.mukey) AS mu_pct_sum
FROM #M4 AS M4
LEFT OUTER JOIN cointerp AS TP ON M4.cokey = TP.cokey AND rulekey = @ruleKey
WHERE M4.majcompflag = 'Yes';
 
-- Populate component level ratings with adjusted component percent to account for the un-used minor components
-- Can I use this table to determine the dominant interphrc-condition for each mapunit???
TRUNCATE TABLE #M6
INSERT INTO #M6
SELECT aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating, mu_pct_sum, (1.0 * comppct_r / mu_pct_sum) AS adj_comp_pct
FROM #M5;
 
-- Populates component acres by multiplying map unit acres with adjusted component percent
TRUNCATE TABLE #M8
INSERT INTO #M8
SELECT  aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating, MU_pct_sum, adj_comp_pct, ROUND ( (adj_comp_pct * mapunit_acres), 4) AS co_acres
FROM #M6;
 
-- Aggregates the classes and sums up the component acres  by landunit (Tract and Field number)
TRUNCATE TABLE #M10
INSERT INTO #M10
SELECT landunit, rating, SUM (co_acres) AS rating_acres
FROM #M8
GROUP BY landunit, rating
ORDER BY landunit, rating_acres DESC;
 
-- Group of insert statements to populate the final output tables
 
-- Detailed Landunit Ratings1: rating acres and rating percent by area for each soil-landunit polygon
-- These will be summarized to a single set of interp ratings for each landunit. Currently there are 4 interps.
INSERT INTO #LandunitRatingsDetailed1 (aoiid, landunit, attributename, rating, rating_key, rating_num, rating_pct, rating_acres, landunit_acres)
SELECT aoiid, M10.landunit, @attributeName AS attributename, M10.rating, RD.rating_key, RD.rating_num,
ROUND ((rating_acres/ landunit_acres) * 100.0, 2) AS rating_pct, 
ROUND (rating_acres,2) AS rating_acres,
ROUND ( landunit_acres, 2) AS landunit_acres
FROM #M10 M10
LEFT OUTER JOIN #AoiAcres ON #AoiAcres.landunit = M10.landunit
INNER JOIN #RatingDomain RD ON M10.rating = RD.rating
WHERE RD.attributename = @attributeName
GROUP BY aoiid, M10.landunit, M10.rating, rating_key, rating_acres, landunit_acres, rating_num
ORDER BY landunit, attributename, rating_num DESC;
 
-- #LandunitRatingsDetailed2 is populated with all information plus rolling_pct and rolling_acres which are using in the landunit summary rating.
-- Detailed Landunit Ratings2 table columns: landunit, attributename, rating, rating_key, rating_num, rating_pct, rating_acres, landunit_acres, rolling_pct, rolling_acres 
INSERT INTO #LandunitRatingsDetailed2 (landunit, attributename, rating, rating_num, rating_key, rating_pct, rating_acres, landunit_acres, rolling_pct, rolling_acres)
SELECT landunit, attributename, rating, rating_num, rating_key, rating_pct, rating_acres, landunit_acres,
  rolling_pct = SUM(rating_pct) OVER
  (
    PARTITION BY landunit
    ORDER BY rating_key ROWS UNBOUNDED PRECEDING
  ),
  rolling_acres = SUM(rating_acres) OVER
  (
    PARTITION BY landunit
    ORDER BY rating_key ROWS UNBOUNDED PRECEDING
  )
  FROM #LandunitRatingsDetailed1
  WHERE attributename = @attributeName
  ORDER BY landunit, attributename;

-- SELECT * FROM #LandunitRatingsDetailed2 WHERE attributename = @attributeName;
 
-- CART
-- #LandunitRatingsCART
-- Identifies the single, most limiting rating (per landunit) that comprises at least 10% by area or 10 acres.
-- This record will have an id value of 1.
INSERT INTO #LandunitRatingsCART (id, landunit, attributename, rating, rating_key, rolling_pct, rolling_acres, landunit_acres)
SELECT ROW_NUMBER() OVER(PARTITION BY landunit ORDER BY rating_key ASC) AS "id",
landunit, attributename, rating, rating_key, rolling_pct, rolling_acres, landunit_acres
FROM #LandunitRatingsDetailed2
WHERE attributename = @attributeName AND (rolling_pct >= @minPct OR rolling_acres >= @minAcres)
 
-- SELECT * FROM #LandunitRatingsCART WHERE attributename = @attributeName;

-- End of:  Agricultural Organic Soil Subsidence 
-- ************************************************************************************************
-- ************************************************************************************************

-- ************************************************************************************************
-- Begin query for soil interpretation:  Suitability for Aerobic Soil Organisms 
-- ************************************************************************************************
 
SELECT @attributeName = 'Suitability for Aerobic Soil Organisms';
SELECT @minPct = 10;
SELECT @minAcres = 10;
 
-- Get ordered set of interphrc values from sdvattribute.maplegendxml. This is assumed to begin with the 'worst' rating. Need to double-check this for all interps.
SELECT @rating1 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[1]', 'VARCHAR(100)');
SELECT @rating2 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[2]', 'VARCHAR(100)');
SELECT @rating3 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[3]', 'VARCHAR(100)');
SELECT @rating4 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[4]', 'VARCHAR(100)');
SELECT @rating5 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[5]', 'VARCHAR(100)');
SELECT @rating6 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[6]', 'VARCHAR(100)');
 
-- Set interp rulekey and ruledesign as a variable to be used in cointerp query
SELECT @ruleKey = (SELECT rulekey FROM #SDV WHERE attributename = @attributeName);
SELECT @ruleDesign = (SELECT ruledesign FROM #SDV WHERE attributename = @attributeName)
SELECT @notRatedPhrase = (SELECT notratedphrase FROM #SDV WHERE attributename = @attributeName);

-- Add Not rated phrase to @rating variables
IF @notRatedPhrase IS NOT NULL
  IF @rating1 IS NULL (SELECT @rating1 = @notRatedPhrase)
  ELSE 
    IF @rating2 IS NULL (SELECT @rating2 = @notRatedPhrase)
    ELSE
      IF @rating3 IS NULL (SELECT @rating3 = @notRatedPhrase)
      ELSE
        IF @rating4 IS NULL (SELECT @rating4 = @notRatedPhrase)
        ELSE 
          IF @rating5 IS NULL (SELECT @rating5 = @notRatedPhrase)
          ELSE
            IF @rating6 IS NULL (SELECT @rating6 = @notRatedPhrase)

-- Append the rating classes for this interp to the #RatingClasses table
INSERT INTO #RatingClasses (attributename, ruledesign, rating1, rating2, rating3, rating4, rating5, rating6)
SELECT @attributeName AS attributename, @ruleDesign AS ruledesign, @rating1 AS rating1, @rating2 AS rating2, @rating3 AS rating3, @rating4 AS rating4, @rating5 AS rating5, @rating6 AS rating6;
 
-- Populate the #RatingDomain table with a unique rating_key for this interp
SELECT @ratingKey = RTRIM(@attributeName) + ':1'
IF NOT @rating1 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating1, 1)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':2'
IF NOT @rating2 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating2, 2)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':3'
IF NOT @rating3 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating3, 3)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':4'
IF NOT @rating4 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating4, 4)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':5'
IF NOT @rating5 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating5, 5)
 
SELECT @ratingKey = RTRIM(@attributeName) + ':6'
IF NOT @rating6 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating6, 6)
 
-- Populate component level ratings using the currently set soil interpretation
TRUNCATE TABLE #M5
INSERT INTO #M5
SELECT M4.aoiid, M4.landunit, M4.mukey, mapunit_acres, M4.cokey, M4.compname, M4.comppct_r, TP.interphrc AS rating, SUM (M4.comppct_r) OVER(PARTITION BY M4.landunit, M4.mukey) AS mu_pct_sum
FROM #M4 AS M4
LEFT OUTER JOIN cointerp AS TP ON M4.cokey = TP.cokey AND rulekey = @ruleKey
WHERE M4.majcompflag = 'Yes';
 
-- Populate component level ratings with adjusted component percent to account for the un-used minor components
-- Can I use this table to determine the dominant interphrc-condition for each mapunit???
TRUNCATE TABLE #M6
INSERT INTO #M6
SELECT aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating, mu_pct_sum, (1.0 * comppct_r / mu_pct_sum) AS adj_comp_pct
FROM #M5;
 
-- Populates component acres by multiplying map unit acres with adjusted component percent
TRUNCATE TABLE #M8
INSERT INTO #M8
SELECT  aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating, MU_pct_sum, adj_comp_pct, ROUND ( (adj_comp_pct * mapunit_acres), 4) AS co_acres
FROM #M6;
 
-- Aggregates the classes and sums up the component acres  by landunit (Tract and Field number)
TRUNCATE TABLE #M10
INSERT INTO #M10
SELECT landunit, rating, SUM (co_acres) AS rating_acres
FROM #M8
GROUP BY landunit, rating
ORDER BY landunit, rating_acres DESC;
 
-- Group of insert statements to populate the final output tables
 
-- Detailed Landunit Ratings1: rating acres and rating percent by area for each soil-landunit polygon
-- These will be summarized to a single set of interp ratings for each landunit. Currently there are 4 interps.
INSERT INTO #LandunitRatingsDetailed1 (aoiid, landunit, attributename, rating, rating_key, rating_num, rating_pct, rating_acres, landunit_acres)
SELECT aoiid, M10.landunit, @attributeName AS attributename, M10.rating, RD.rating_key, RD.rating_num,
ROUND ((rating_acres/ landunit_acres) * 100.0, 2) AS rating_pct, 
ROUND (rating_acres,2) AS rating_acres,
ROUND ( landunit_acres, 2) AS landunit_acres
FROM #M10 M10
LEFT OUTER JOIN #AoiAcres ON #AoiAcres.landunit = M10.landunit
INNER JOIN #RatingDomain RD ON M10.rating = RD.rating
WHERE RD.attributename = @attributeName
GROUP BY aoiid, M10.landunit, M10.rating, rating_key, rating_acres, landunit_acres, rating_num
ORDER BY landunit, attributename, rating_num DESC;
 
-- #LandunitRatingsDetailed2 is populated with all information plus rolling_pct and rolling_acres which are using in the landunit summary rating.
-- Detailed Landunit Ratings2 table columns: landunit, attributename, rating, rating_key, rating_num, rating_pct, rating_acres, landunit_acres, rolling_pct, rolling_acres 
INSERT INTO #LandunitRatingsDetailed2 (landunit, attributename, rating, rating_num, rating_key, rating_pct, rating_acres, landunit_acres, rolling_pct, rolling_acres)
SELECT landunit, attributename, rating, rating_num, rating_key, rating_pct, rating_acres, landunit_acres,
  rolling_pct = SUM(rating_pct) OVER
  (
    PARTITION BY landunit
    ORDER BY rating_key ROWS UNBOUNDED PRECEDING
  ),
  rolling_acres = SUM(rating_acres) OVER
  (
    PARTITION BY landunit
    ORDER BY rating_key ROWS UNBOUNDED PRECEDING
  )
  FROM #LandunitRatingsDetailed1
  WHERE attributename = @attributeName
  ORDER BY landunit, attributename;

-- SELECT * FROM #LandunitRatingsDetailed2 WHERE attributename = @attributeName;
 
-- CART
-- #LandunitRatingsCART
-- Identifies the single, most limiting rating (per landunit) that comprises at least 10% by area or 10 acres.
-- This record will have an id value of 1.
INSERT INTO #LandunitRatingsCART (id, landunit, attributename, rating, rating_key, rolling_pct, rolling_acres, landunit_acres)
SELECT ROW_NUMBER() OVER(PARTITION BY landunit ORDER BY rating_key ASC) AS "id",
landunit, attributename, rating, rating_key, rolling_pct, rolling_acres, landunit_acres
FROM #LandunitRatingsDetailed2
WHERE attributename = @attributeName AND (rolling_pct >= @minPct OR rolling_acres >= @minAcres)
 
-- SELECT * FROM #LandunitRatingsCART WHERE attributename = @attributeName;

-- End of:  Suitability for Aerobic Soil Organisms 









-- ************************************************************************************************
-- ************************************************************************************************
-- Final output queries follow...
-- ************************************************************************************************

 

-- Diagnostic tables or ArcMap spatial layers. Not intended for the production CART queries
--
-- Component level table with adjusted component percent (does this use major components only?
---SELECT * FROM #M6
 

 
-- Rating domain values 
-- SELECT * FROM #RatingDomain;
 
-- Diagnostic table contains an ordered set of rating classes for each interpretation
-- SELECT * FROM #RatingClasses;
 
-- Diagnostic table contains an ordered set of rating classes for each interpretation
-- SELECT attributename, nasisrulename, rulekey, ruledesign, notratedphrase, resultcolumnname, CAST(maplegendxml AS NVARCHAR(2048)) AS maplegendxml, attributedescription
-- FROM #SDV;
 
-- Aggregated Map Unit Acres into Farm Class Acres.
-- Please note. This query returns multiple values per landunit, not an overall rating for each landunit.
-- Also note that the aaoid was removed from the DISTINCT list. Make sure that just using landunit string does not cause problems.

--Ponding and Flooding
SELECT landunit, ROUND (landunit_acres,2) landunit_acres, ROUND (SUM (co_acres),2) AS ponding_flooding_acres, 'Ponding or Flooding' AS attributename 
FROM #pf2
GROUP BY landunit, landunit_acres
ORDER BY landunit;

--Water Table By Land Unit
SELECT landunit, ROUND (landunit_acres,2) landunit_acres, ROUND (SUM (co_acres),2) AS water_table_acres, 'Water Table' AS attributename 
FROM #wet2
GROUP BY landunit, landunit_acres
ORDER BY landunit;


--Farm Class By Land Unit
SELECT DISTINCT landunit, SUM (mapunit_acres) OVER(PARTITION BY aoiid, farmlndclass) AS rating_acres, farmlndclass, 'Farm Class' AS attributename 
FROM #FC
GROUP BY aoiid, landunit, mapunit_acres, farmlndclass;


-- Return hydric by Land Unit
SELECT DISTINCT landunit,
attributename,
ROUND (SUM (low_acres) OVER(PARTITION BY aoiid), 2) AS aoiid_low_acres, 
ROUND (SUM (rv_acres) OVER(PARTITION BY aoiid), 2) AS aoiid_rv_acres, 
ROUND (SUM (high_acres) OVER(PARTITION BY aoiid), 2) AS aoiid_high_acres,
ROUND((ROUND (SUM (low_acres) OVER(PARTITION BY aoiid), 2) / aoi_acres) * 100.0, 2) AS aoiid_low_pct, 
ROUND((ROUND (SUM (rv_acres) OVER(PARTITION BY aoiid), 2) / aoi_acres) * 100.0, 2) AS aoiid_rv_pct,
ROUND((ROUND (SUM (high_acres) OVER(PARTITION BY aoiid), 2) / aoi_acres) * 100.0, 2) AS aoiid_high_pct
FROM #Hydric3

-- Soil landunit polygon geometry has the intersected landunits and soil (WKT geometry)
--SELECT landunit, AS2.mukey, MU.musym, MU.muname, poly_acres, soilgeog.STAsText() AS wktgeom, soilgeom
--FROM #AoiSoils2 AS2
--INNER JOIN mapunit MU ON AS2.mukey = MU.mukey
--ORDER BY polyid ASC;

-- Soil geometry with landunits

 --DOMINANT CONDITION
SELECT M2.mukey,  rulename, attributename, (SELECT TOP 1 interphrc
 FROM mapunit
 INNER JOIN component ON component.mukey=mapunit.mukey AND majcompflag = 'Yes' 
 INNER JOIN cointerp AS coi ON component.cokey = coi.cokey AND mapunit.mukey = M2.mukey AND ruledepth = 0 AND TP.rulekey=coi.rulekey
 GROUP BY interphrc, comppct_r ORDER BY SUM(comppct_r) over(partition by interphrc) DESC) as interp_dcd
FROM #M2 AS M2
INNER JOIN component AS CO ON CO.mukey = M2.mukey AND majcompflag = 'Yes'
LEFT OUTER JOIN cointerp AS TP ON CO.cokey = TP.cokey 
INNER JOIN #SDV AS s ON s.rulekey=TP.rulekey
GROUP BY M2.mukey, rulename, TP.rulekey, attributename
ORDER BY M2.mukey, rulename, TP.rulekey, attributename


-- Detailed CART soil interpretation ratings for each landunit. This table contains the neccesary rolling_pct and rolling_acres data.
-- SELECT DT.landunit, rating_key, rating_pct, rolling_pct, rating_acres, rolling_acres, landunit_acres, MD.soils_metadata
-- FROM #LandunitRatingsDetailed2 DT
-- INNER JOIN #LandunitMetadata MD ON DT.landunit = MD.landunit
-- ORDER BY landunit, rating_key, rating_pct DESC;
 
-- Final CART soil interpretation ratings for each landunit
-- The LandunitRatingsCART table will have all data, but the record for the overall landunit rating will have an id = 1.
INSERT INTO #LandunitRatingsCART2 (landunit, attributename, rating, rating_key, rolling_pct, rolling_acres, landunit_acres, soils_metadata)
SELECT LC.landunit, LC.attributename, LC.rating, LC.rating_key, rolling_pct, rolling_acres, landunit_acres, MD.soils_metadata
FROM #LandunitRatingsCART LC
INNER JOIN #RatingDomain RD ON LC.attributename = RD.attributename AND LC.rating = RD.rating
INNER JOIN #LandunitMetadata MD ON LC.landunit = MD.landunit
WHERE LC.id = 1
ORDER BY landunit, rating_key;
 
SELECT landunit, rating_key, soils_metadata FROM #LandunitRatingsCART2;

-- Diagnostic component level soils data that can be related (1:M) to the soil polygon layer using mukey column.
SELECT DISTINCT M4.compname, M4.comppct_r, M4.majcompflag, Mu.musym, Mu.muname, M4.cokey, M4.mukey
FROM #M4 M4
INNER JOIN mapunit Mu ON M4.mukey = Mu.Mukey
ORDER BY M4.mukey, M4.comppct_r DESC, M4.cokey;

---Jason Testing
SELECT #AoiSoils.polyid, #AoiSoils.landunit, #AoiSoils.mukey, ROUND((( GEOGRAPHY::STGeomFromWKB(soilgeom.STAsBinary(), 4326 ).STArea() ) / 4046.8564224 ), 2 ) AS poly_acres, soilgeom,
 SUBSTRING( (SELECT DISTINCT ( ', ' +  cogm2.geomfname ) 
FROM mapunit AS m2
INNER JOIN component AS c2 ON c2.mukey = m2.mukey AND hydricrating = 'Yes' AND m2.mukey = mu.mukey 
INNER JOIN cogeomordesc AS cogm2 ON c2.cokey = cogm2.cokey AND cogm2.rvindicator='Yes' AND cogm2.geomftname = 'Landform' GROUP  BY  m2.mukey, cogm2.geomfname FOR XML PATH('') ), 3, 1000) AS hydric_landforms,

SUBSTRING( (SELECT  DISTINCT ( ', ' +  cogm.geomfname ) 
   FROM mapunit AS m1
   INNER JOIN component AS c1 ON c1.mukey = m1.mukey AND hydricrating = 'Yes' AND m1.mukey = mu.mukey 
   INNER JOIN cogeomordesc AS cogm ON c1.cokey = cogm.cokey AND cogm.rvindicator = 'Yes' AND cogm.geomftname = 'Microfeature' GROUP BY m1.mukey, cogm.geomfname FOR XML PATH('') ), 3, 1000) AS hydric_microfeatures,  

SUBSTRING( ( SELECT ( ', ' + hydriccriterion ) 
   FROM mapunit AS m
   INNER JOIN component AS c ON c.mukey = m.mukey AND hydricrating = 'Yes' AND m.mukey = mu.mukey
   INNER JOIN cohydriccriteria AS coh ON c.cokey = coh.cokey GROUP BY m.mukey, hydriccriterion ORDER BY hydriccriterion ASC FOR XML PATH('') ), 3, 1000) AS hydric_criteria, 
hydric_rating, farmlndclass 
FROM #AoiSoils
INNER JOIN #Hydric2 AS mu ON mu.mukey=#AoiSoils.mukey
INNER JOIN mapunit ON mapunit.mukey = mu.mukey
INNER JOIN #FC AS FC ON FC.mukey=#AoiSoils.mukey;

-- Return detailed hydric data for map layer
SELECT mukind, SUBSTRING( (SELECT DISTINCT ( ', ' +  cogm2.geomfname ) 
FROM mapunit AS m2
INNER JOIN component AS c2 ON c2.mukey = m2.mukey AND hydricrating = 'Yes' AND m2.mukey = mu.mukey 
INNER JOIN cogeomordesc AS cogm2 ON c2.cokey = cogm2.cokey AND cogm2.rvindicator='Yes' AND cogm2.geomftname = 'Landform' GROUP  BY  m2.mukey, cogm2.geomfname FOR XML PATH('') ), 3, 1000) AS hydric_landforms,

SUBSTRING( (SELECT  DISTINCT ( ', ' +  cogm.geomfname ) 
   FROM mapunit AS m1
   INNER JOIN component AS c1 ON c1.mukey = m1.mukey AND hydricrating = 'Yes' AND m1.mukey = mu.mukey 
   INNER JOIN cogeomordesc AS cogm ON c1.cokey = cogm.cokey AND cogm.rvindicator = 'Yes' AND cogm.geomftname = 'Microfeature' GROUP BY m1.mukey, cogm.geomfname FOR XML PATH('') ), 3, 1000) AS hydric_microfeatures,  

SUBSTRING( ( SELECT ( ', ' + hydriccriterion ) 
   FROM mapunit AS m
   INNER JOIN component AS c ON c.mukey = m.mukey AND hydricrating = 'Yes' AND m.mukey = mu.mukey
   INNER JOIN cohydriccriteria AS coh ON c.cokey = coh.cokey GROUP BY m.mukey, hydriccriterion ORDER BY hydriccriterion ASC FOR XML PATH('') ), 3, 1000) AS hydric_criteria, 
hydric_rating, low_pct, rv_pct, high_pct, mu.mukey
FROM #Hydric2 AS mu
INNER JOIN mapunit ON mapunit.mukey = mu.mukey

DROP TABLE IF EXISTS #AoiTable
DROP TABLE IF EXISTS #AoiAcres
DROP TABLE IF EXISTS #AoiSoils
DROP TABLE IF EXISTS #AoiSoils2
DROP TABLE IF EXISTS #M2
DROP TABLE IF EXISTS #M5
DROP TABLE IF EXISTS #M4
DROP TABLE IF EXISTS #M6
DROP TABLE IF EXISTS #M8
DROP TABLE IF EXISTS #M10
DROP TABLE IF EXISTS #InterpTable
DROP TABLE IF EXISTS #LandunitRatingsDetailed
DROP TABLE IF EXISTS #LandunitRatingsCART
DROP TABLE IF EXISTS #SDV
DROP TABLE IF EXISTS #RatingClasses
DROP TABLE IF EXISTS #RatingDomain
DROP TABLE IF EXISTS #DateStamps
DROP TABLE IF EXISTS #LandunitMetadata
DROP TABLE IF EXISTS #LandunitRatingsDetailed1
DROP TABLE IF EXISTS #LandunitRatingsDetailed2
DROP TABLE IF EXISTS  #LandunitRatingsCART2
DROP TABLE IF EXISTS #interp_dcd
DROP TABLE IF EXISTS  #Hydric2
DROP TABLE IF EXISTS  #Hydric3
DROP TABLE IF EXISTS #Hydric_A
DROP TABLE IF EXISTS #Hydric_B
DROP TABLE IF EXISTS  #Hydric1
DROP TABLE IF EXISTS  #Hydric3
DROP TABLE IF EXISTS  #FC
DROP TABLE IF EXISTS  #wet
DROP TABLE IF EXISTS  #wet1
DROP TABLE IF EXISTS  #wet2
DROP TABLE IF EXISTS  #pf
DROP TABLE IF EXISTS  #pf1
DROP TABLE IF EXISTS  #pf2
DROP TABLE IF EXISTS  #agg1
DROP TABLE IF EXISTS  #agg2
DROP TABLE IF EXISTS  #agg3
DROP TABLE IF EXISTS  #agg4
DROP TABLE IF EXISTS #agg5
DROP TABLE IF EXISTS #agg6
GO