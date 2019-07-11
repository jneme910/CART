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
DECLARE @intersectedPolygonGeometries table (id int, geom geometry);
DECLARE @intersectedPolygonGeographies table (id int, geog geography);
DECLARE @AoiId INT ;
DECLARE @boundary VARCHAR(MAX);

CREATE TABLE #AoiTable 
    ( aoiid INT IDENTITY (1,1) ,
    landunit CHAR(20),
    aoigeom GEOMETRY);

CREATE TABLE #AoiSoils 
    ( polyid INT IDENTITY (1,1),
    aoiid INT,
    landunit CHAR(20),
    mukey INT,
    soilgeom GEOMETRY
    );




SELECT @aoiGeom = GEOMETRY::STGeomFromText('MULTIPOLYGON (((-102.12335160658608 45.959173206572416, -102.13402890980223 45.959218442561564, -102.13386921506947 45.944643788188387, -102.12327175652177 45.944703605814198, -102.12335160658608 45.959173206572416)))', 4326);   
SELECT @aoiGeomFixed = @aoiGeom.MakeValid().STUnion(@aoiGeom.STStartPoint());  
INSERT INTO #AoiTable ( landunit, aoigeom )  
VALUES ('T9981 Fld3', @aoiGeomFixed); 
SELECT @aoiGeom = GEOMETRY::STGeomFromText('MULTIPOLYGON (((-102.1130336443976 45.959162795100383, -102.12335160658608 45.959173206572416, -102.12327175652177 45.944703605814198, -102.1128892282776 45.944710506326032, -102.1130336443976 45.959162795100383)))', 4326);   
SELECT @aoiGeomFixed = @aoiGeom.MakeValid().STUnion(@aoiGeom.STStartPoint());  
INSERT INTO #AoiTable ( landunit, aoigeom )  
VALUES ('T9981 Fld4', @aoiGeomFixed);

INSERT INTO #AoiSoils (aoiid, landunit, mukey, soilgeom)
SELECT A.aoiid, A.landunit, M.mukey, M.mupolygongeo.STIntersection(A.aoigeom ) AS soilgeom
FROM mupolygon M, #AoiTable A 
WHERE mupolygongeo.STIntersects(A.aoigeom) = 1;


--SELECT * FROM [SDA_Get_Mupolygonkey_from_intersection_with_WktWgs84] (@boundary);
 select distinct mupolygonkey
   from mupolygon 
   INNER JOIN #AoiSoils AS ASOILS ON ASOILS.mukey=mupolygon.mukey
   INNER JOIN #AoiTable AS ATABLE ON ATABLE.aoiid=ASOILS.aoiid
    where mupolygongeo.STIntersects(aoigeom) = 1;
  ;

---Jason Testing
--SELECT #AoiSoils.polyid, #AoiSoils.landunit, #AoiSoils.mukey, ROUND((( GEOGRAPHY::STGeomFromWKB(soilgeom.STAsBinary(), 4326 ).STArea() ) / 4046.8564224 ), 2 ) AS poly_acres, soilgeom
--FROM #AoiSoils
--INNER JOIN mapunit ON mapunit.mukey = #AoiSoils.mukey

--select @pAoiId = aoiid;
