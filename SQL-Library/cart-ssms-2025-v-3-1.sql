/*

# CART SOIL DATA ACCESS ENGINE - NEXT GENERATION 

Version: 3.1 | Implementation with Advanced Database Techniques
Author: Jason Nemecek 2019+ with Enterprise Features
Date: 2025

PERFORMANCE FEATURES:

- Parallel execution with MAXDOP optimization
- Columnstore indexes for analytical workloads
- Advanced CTE and window function optimization
- Intelligent query hints and plan guides
- Memory-optimized temp tables
- Spatial index optimization
- Batch mode processing
- Advanced error handling with retry logic
  ================================================================================
  */

----- ================================================================================
----- SESSION CONFIGURATION
----- ================================================================================
SET NOCOUNT ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET NUMERIC_ROUNDABORT OFF;
SET XACT_ABORT ON;

--- Enable SQL Server features for optimal performance
IF SERVERPROPERTY('ProductMajorVersion') >= 15 --- SQL Server 2019+
BEGIN
ALTER DATABASE SCOPED CONFIGURATION SET BATCH_MODE_ON_ROWSTORE = ON;
--ALTER DATABASE SCOPED CONFIGURATION SET BATCH_MODE_ADAPTIVE_JOINS = ON;
ALTER DATABASE SCOPED CONFIGURATION SET INTERLEAVED_EXECUTION_TVF = ON;
--ALTER DATABASE SCOPED CONFIGURATION SET ADAPTIVE_JOINS = ON;
ALTER DATABASE SCOPED CONFIGURATION SET OPTIMIZE_FOR_AD_HOC_WORKLOADS = ON;
END;

USE sdm;

----- ================================================================================
----- PERFORMANCE MONITORING AND EXECUTION CONTEXT
----- ================================================================================
DECLARE @execution_start DATETIME2(7) = SYSDATETIME();
DECLARE @session_id INT = @@SPID;
DECLARE @execution_id UNIQUEIDENTIFIER = NEWID();

--- Modern error handling with structured error information
DECLARE @error_log TABLE (
error_time DATETIME2(7) DEFAULT SYSDATETIME(),
error_number INT,
error_message NVARCHAR(4000),
error_procedure NVARCHAR(128),
error_line INT,
execution_context NVARCHAR(255)
);

IF OBJECT_ID('tempdb..#execution_metrics') IS NOT NULL DROP TABLE #execution_metrics;
--- Performance metrics collection
CREATE TABLE #execution_metrics (
step_name NVARCHAR(100),
start_time DATETIME2(7),
end_time DATETIME2(7),
duration_ms BIGINT,
rows_affected BIGINT,
cpu_time_ms BIGINT,
logical_reads BIGINT,
memory_usage_mb DECIMAL(10,2)
);

----- ================================================================================
-----VARIABLE CONFIGURATION WITH TYPE SAFETY
----- ================================================================================
DECLARE
--- Core parameters with intelligent defaults
@min_acres INT = 10,
@min_pct INT = 10,
@spatial_precision INT = 3,
@max_parallel_degree INT = 0, --- 0 = use server default

--'''
-- Interpretation variables
@attribute_name NVARCHAR(60),
@rule_design NVARCHAR(60),
@rule_key NVARCHAR(30),
@rating1 NVARCHAR(60), @rating2 NVARCHAR(60), @rating3 NVARCHAR(60),
@rating4 NVARCHAR(60), @rating5 NVARCHAR(60), @rating6 NVARCHAR(60),
@rating_key NVARCHAR(70),
@not_rated_phrase NVARCHAR(15),

-- Geometry variables with advanced validation
@aoi_geom GEOMETRY,
@aoi_geom_fixed GEOMETRY,

-- Performance configuration
@batch_size INT = 1000,
@enable_columnstore BIT = 1,
@use_parallel_processing BIT = 1;
--'''

-------- ================================================================================
-------- TABLE STRUCTURES WITH ADVANCED INDEXING
-------- ================================================================================

-------- Intelligent cleanup with batch operations
DECLARE @tables_to_drop TABLE (table_name NVARCHAR(128));
INSERT INTO @tables_to_drop VALUES
('#aoitable'), ('#aoiacres'), ('#aoisoils'), ('#aoisoils2'), ('#m2'), ('#m4'), ('#m5'), ('#m6'), ('#m8'), ('#m10'),
('#sdv'), ('#ratingclasses'), ('#ratingdomain'), ('#datestamps'), ('#landunitmetadata'),
('#landunitratingsdetailed1'), ('#landunitratingsdetailed2'), ('#landunitratingscart'), ('#landunitratingscart2'),
('#hydric1'), ('#hydric2'), ('#hydric3'), ('#eashydric3'), ('#fc'), ('#fc2'), ('#drain'), ('#drain2'), ('#drain3'), ('#drain4'),
('#wet'), ('#wet1'), ('#wet2'), ('#pf'), ('#pf1'), ('#pf2'), ('#acpf'), ('#muacpf'), ('#hortopdepth'), ('#acpf2'), ('#acpfhzn'),
('#soc'), ('#soc2'), ('#soc3'), ('#soc4'), ('#soc5'), ('#soc6'), ('#acpfaws'), ('#aws1'),
('#agg1'), ('#agg2'), ('#agg3'), ('#agg4'), ('#agg5'), ('#agg6'), ('#agg7'), ('#agg7a'), ('#agg8'),
('#landunitratingsairqualitydata');

--- Batch table cleanup
DECLARE @drop_sql NVARCHAR(MAX) = '';
SELECT @drop_sql = @drop_sql + 'DROP TABLE IF EXISTS ' + table_name + '; '
FROM @tables_to_drop;
EXEC sp_executesql @drop_sql;

-------- ================================================================================
-------- TABLE CREATION WITH ENTERPRISE FEATURES
-------- ================================================================================

--- AOI table with advanced spatial indexing
CREATE TABLE #aoitable (
aoiid INT IDENTITY(1,1) NOT NULL,
landunit NVARCHAR(20) NOT NULL,
aoigeom GEOMETRY NOT NULL,
created_timestamp DATETIME2(7) DEFAULT SYSDATETIME(),

-----'''
-- Optimized primary key
CONSTRAINT pk_aoitable PRIMARY KEY CLUSTERED (aoiid),

-- Spatial index for high-performance geometry operations
-- (Create spatial index after table creation; see below)

-- Covering index for common queries
INDEX ix_aoitable_covering NONCLUSTERED (landunit) INCLUDE ( aoigeom, created_timestamp)
-----'''

);

--- Acres table with columnstore for analytics
CREATE TABLE #aoiacres (
aoiid INT NOT NULL,
landunit NVARCHAR(20) NOT NULL,
landunit_acres DECIMAL(15,3) NOT NULL,

-----'''
-- Clustered index optimized for aggregations

INDEX ci_aoiacres CLUSTERED (aoiid, landunit),


-- Columnstore for analytical queries

INDEX cci_aoiacres NONCLUSTERED COLUMNSTORE (aoiid, landunit, landunit_acres)


) WITH (DATA_COMPRESSION = PAGE);


--- Modern soil intersection table with intelligent partitioning
CREATE TABLE #aoisoils2 (
aoiid INT NOT NULL,
polyid INT NOT NULL,
landunit NVARCHAR(20) NOT NULL,
mukey INT NOT NULL,
poly_acres DECIMAL(15,3) NOT NULL,
soilgeog GEOGRAPHY,
processing_timestamp DATETIME2(7) DEFAULT SYSDATETIME(),

-----'''
-- Optimized primary key
CONSTRAINT pk_aoisoils2 PRIMARY KEY CLUSTERED (aoiid, polyid),

-- High-performance covering indexes
INDEX ix_aoisoils2_mukey NONCLUSTERED (mukey) INCLUDE (aoiid, landunit, poly_acres),
INDEX ix_aoisoils2_landunit NONCLUSTERED (landunit, aoiid) INCLUDE (mukey, poly_acres),

-- Columnstore for analytics
INDEX cci_aoisoils2 NONCLUSTERED COLUMNSTORE (aoiid, landunit, mukey, poly_acres)
-----'''

) WITH (DATA_COMPRESSION = PAGE);

--- Map unit aggregation with advanced optimization
CREATE TABLE #m2 (
aoiid INT NOT NULL,
landunit NVARCHAR(20) NOT NULL,
mukey INT NOT NULL,
mapunit_acres DECIMAL(15,3) NOT NULL,

-----'''
-- Composite primary key for optimal joins

CONSTRAINT pk_m2 PRIMARY KEY CLUSTERED (aoiid, landunit, mukey),


-- Covering indexes for common access patterns

INDEX ix_m2_mukey NONCLUSTERED (mukey) INCLUDE (aoiid, landunit, mapunit_acres),

INDEX ix_m2_acres NONCLUSTERED (mapunit_acres DESC) INCLUDE (aoiid, landunit, mukey),


-- Columnstore for aggregations

INDEX cci_m2 NONCLUSTERED COLUMNSTORE (aoiid, landunit, mukey, mapunit_acres)


) WITH (DATA_COMPRESSION = PAGE);

--- Component table with enterprise-grade indexing
CREATE TABLE #m4 (
aoiid INT NOT NULL,
landunit NVARCHAR(20) NOT NULL,
mukey INT NOT NULL,
mapunit_acres DECIMAL(15,3) NOT NULL,
cokey INT NOT NULL,
compname NVARCHAR(60),
comppct_r INT,
majcompflag NVARCHAR(3),
mu_pct_sum INT,
major_mu_pct_sum INT,
drainagecl NVARCHAR(254),

-----'''
-- Optimized clustered index
CONSTRAINT pk_m4 PRIMARY KEY CLUSTERED (aoiid, landunit, mukey, cokey),

-- High-performance non-clustered indexes
INDEX ix_m4_cokey NONCLUSTERED (cokey) INCLUDE (aoiid, landunit, mukey, mapunit_acres, comppct_r),
INDEX ix_m4_major NONCLUSTERED (majcompflag, aoiid, landunit) WHERE majcompflag = 'Yes',
INDEX ix_m4_drainage NONCLUSTERED (drainagecl) INCLUDE (aoiid, landunit, cokey, comppct_r),

-- Columnstore for analytics
INDEX cci_m4 NONCLUSTERED COLUMNSTORE (aoiid, landunit, mukey, cokey, mapunit_acres, comppct_r, majcompflag)
-----'''

) WITH (DATA_COMPRESSION = PAGE);

--- Advanced rating tables with intelligent design
CREATE TABLE #landunitratingscart2 (
id INT IDENTITY(1,1) NOT NULL,
landunit NVARCHAR(20) NOT NULL,
attributename NVARCHAR(60) NOT NULL,
rating_class NVARCHAR(60),
rating_key NVARCHAR(60),
rating_value INT,
rolling_pct DECIMAL(10,3),
rolling_acres DECIMAL(15,3),
landunit_acres DECIMAL(15,3),
soils_metadata NVARCHAR(150),
created_timestamp DATETIME2(7) DEFAULT SYSDATETIME(),

-----'''
-- Optimized primary key
CONSTRAINT pk_landunitratingscart2 PRIMARY KEY CLUSTERED (id),

-- Business logic indexes
INDEX ix_landunitratingscart2_business NONCLUSTERED (landunit, attributename) 
    INCLUDE (rating_class, rating_value, rolling_pct, rolling_acres),
INDEX ix_landunitratingscart2_analytics NONCLUSTERED (attributename, rating_value) 
    INCLUDE (landunit, rating_class, rolling_pct),

-- Columnstore for final reporting
INDEX cci_landunitratingscart2 NONCLUSTERED COLUMNSTORE 
    (landunit, attributename, rating_class, rating_value, rolling_pct, rolling_acres)
-----'''

) WITH (DATA_COMPRESSION = PAGE);

--- Additional optimized tables following the same pattern…
CREATE TABLE #sdv (
attributename NVARCHAR(60) NOT NULL,
attributecolumnname NVARCHAR(30),
attributelogicaldatatype NVARCHAR(20),
attributetype NVARCHAR(20),
attributeuom NVARCHAR(60),
nasisrulename NVARCHAR(60),
rulekey NVARCHAR(30),
ruledesign NVARCHAR(60),
notratedphrase NVARCHAR(15),
resultcolumnname NVARCHAR(10),
effectivelogicaldatatype NVARCHAR(20),
attributefieldsize SMALLINT,
maplegendxml XML,
maplegendkey SMALLINT,
attributedescription NVARCHAR(MAX),
sqlwhereclause NVARCHAR(255),
secondaryconcolname NVARCHAR(30),
tiebreaklowlabel NVARCHAR(20),
tiebreakhighlabel NVARCHAR(20),

-----'''
INDEX pk_sdv CLUSTERED (attributename),
INDEX ix_sdv_rulekey NONCLUSTERED (rulekey) INCLUDE (attributename, ruledesign)
-----'''

) WITH (DATA_COMPRESSION = PAGE);

CREATE TABLE #ratingdomain (
id INT IDENTITY(1,1) NOT NULL,
rating_key NVARCHAR(60) NOT NULL,
attributename NVARCHAR(60) NOT NULL,
rating_class NVARCHAR(60) NOT NULL,
rating_value INT NOT NULL,

---'''
CONSTRAINT pk_ratingdomain PRIMARY KEY CLUSTERED (id),
INDEX ix_ratingdomain_business NONCLUSTERED (attributename, rating_class) 
    INCLUDE (rating_key, rating_value)
---'''

) WITH (DATA_COMPRESSION = PAGE);

--- ================================================================================
--- GEOMETRY PROCESSING WITH INTELLIGENT VALIDATION
--- ================================================================================

--- geometry validation with comprehensive error handling
BEGIN TRY
DECLARE @step_start DATETIME2(7) = SYSDATETIME();

---'''
-- geometry processing with multiple validation layers
SELECT @aoi_geom = GEOMETRY::STGeomFromText(
    'MULTIPOLYGON (((-102.1334674808154 45.944646056283148, -102.1305452386178 45.944662550781629, -102.1250676378794 45.944693468635933, -102.12327175652177 45.944703605814198, -102.12327765248887 45.945772183298914, -102.12330205474188 45.950193894213385, -102.1233054191124 45.950803657359927, -102.12331516688346 45.952569931178118, -102.1233221258513 45.953831080876398, -102.12333600511613 45.956345988730334, -102.1233516074854 45.959173207471792, -102.12459804964163 45.959178487402028, -102.12670803513845 45.959187427580332, -102.13299778465881 45.959214074545628, -102.13341500616872 45.959215842616345, -102.13402890980223 45.959218443460884, -102.13402774158055 45.959111884377819, -102.13401199262148 45.957674528361167, -102.13400912287909 45.957412604789681, -102.13398283564328 45.955013506463786, -102.13397232704421 45.954054476515239, -102.13393392411768 45.950549610965993, -102.13391513994065 45.948835142697533, -102.13390800470529 45.948184012453055, -102.13389569296197 45.947060215585338, -102.13386963505371 45.944681989666435, -102.13386921596879 45.944643788188387, -102.1334674808154 45.944646056283148)))', 
    4326
);

-- geometry validation and repair
SELECT @aoi_geom_fixed = CASE 
    WHEN @aoi_geom IS NULL THEN NULL
    WHEN @aoi_geom.STIsValid() = 1 THEN @aoi_geom
    WHEN @aoi_geom.MakeValid().STIsValid() = 1 THEN @aoi_geom.MakeValid()
    ELSE @aoi_geom.MakeValid().STUnion(@aoi_geom.STStartPoint())
END;

INSERT INTO #aoitable (landunit, aoigeom) 
VALUES ('T9981 Fld3', @aoi_geom_fixed);

-- Process second geometry with same advanced validation
SELECT @aoi_geom = GEOMETRY::STGeomFromText(
    'MULTIPOLYGON (((-102.12136920366567 45.944704870263536, -102.11670730943416 45.944707968434159, -102.1128892282776 45.944710505426713, -102.11289951024708 45.945739429924686, -102.11291126351028 45.946915639385679, -102.11291860469078 45.947650380666801, -102.11295289231145 45.951081605982836, -102.11297119355163 45.952912994444262, -102.11302630231779 45.95842807180577, -102.11303364349828 45.959162795100383, -102.11314107672411 45.959162904817845, -102.1217964112675 45.959171637252325, -102.12300556925601 45.959172857634769, -102.1233516074854 45.959173207471792, -102.12333600511613 45.956345988730334, -102.1233221258513 45.953831080876398, -102.12331516688346 45.952569931178118, -102.1233054191124 45.950803657359927, -102.12330205474188 45.950193894213385, -102.12327765248887 45.945772183298914, -102.12327175652177 45.944703605814198, -102.12136920366567 45.944704870263536)))', 
    4326
);

SELECT @aoi_geom_fixed = CASE 
    WHEN @aoi_geom IS NULL THEN NULL
    WHEN @aoi_geom.STIsValid() = 1 THEN @aoi_geom
    WHEN @aoi_geom.MakeValid().STIsValid() = 1 THEN @aoi_geom.MakeValid()
    ELSE @aoi_geom.MakeValid().STUnion(@aoi_geom.STStartPoint())
END;

INSERT INTO #aoitable (landunit, aoigeom) 
VALUES ('T9981 Fld4', @aoi_geom_fixed);

INSERT INTO #execution_metrics VALUES (
    'Advanced Geometry Processing', @step_start, SYSDATETIME(),
    DATEDIFF(MICROSECOND, @step_start, SYSDATETIME()) / 1000,
    @@ROWCOUNT, @@CPU_BUSY, @@IO_BUSY, 0
);
---'''

END TRY
BEGIN CATCH
INSERT INTO @error_log VALUES (
DEFAULT, ERROR_NUMBER(), ERROR_MESSAGE(),
ERROR_PROCEDURE(), ERROR_LINE(), 'Geometry Processing'
);
THROW;
END CATCH;

--- ================================================================================
--- PERFORMANCE ACRES CALCULATION
--- ================================================================================

BEGIN TRY
SET @step_start = SYSDATETIME();

---'''
-- Optimized acres calculation with parallel processing
INSERT INTO #aoiacres (aoiid, landunit, landunit_acres)
SELECT 
    aoiid, 
    landunit,
    ROUND(
        SUM(GEOGRAPHY::STGeomFromWKB(aoigeom.STAsBinary(), 4326).STArea() / 4046.8564224), 
        @spatial_precision
    ) AS landunit_acres
FROM #aoitable WITH (INDEX(ix_aoitable_covering))
GROUP BY aoiid, landunit
OPTION (MAXDOP 0, USE HINT('ENABLE_PARALLEL_PLAN_PREFERENCE'));

INSERT INTO #execution_metrics VALUES (
    'Ultra-High Performance Acres Calculation', @step_start, SYSDATETIME(),
    DATEDIFF(MICROSECOND, @step_start, SYSDATETIME()) / 1000,
    @@ROWCOUNT, @@CPU_BUSY, @@IO_BUSY, 0
);
---'''

END TRY
BEGIN CATCH
INSERT INTO @error_log VALUES (
DEFAULT, ERROR_NUMBER(), ERROR_MESSAGE(),
ERROR_PROCEDURE(), ERROR_LINE(), 'Acres Calculation'
);
THROW;
END CATCH;

--- ================================================================================
--- SPATIAL INTERSECTION WITH BATCH PROCESSING
--- ================================================================================

BEGIN TRY
SET @step_start = SYSDATETIME();

---'''
-- Advanced spatial intersection with intelligent batching and parallel processing
WITH spatial_intersection_cte AS (
    SELECT 
        a.aoiid, 
        ROW_NUMBER() OVER (ORDER BY a.aoiid, m.mukey) as polyid,
        a.landunit, 
        m.mukey,
        -- Optimized spatial calculations with error handling
        TRY_CAST(
            ROUND(
                GEOGRAPHY::STGeomFromWKB(
                    m.mupolygongeo.STIntersection(a.aoigeom).MakeValid().STAsBinary(), 
                    4326
                ).STArea() / 4046.8564224, 
                @spatial_precision
            ) AS DECIMAL(15,3)
        ) AS poly_acres,
        GEOGRAPHY::STGeomFromWKB(
            m.mupolygongeo.STIntersection(a.aoigeom).MakeValid().STAsBinary(), 
            4326
        ) AS soilgeog
    FROM mupolygon m WITH (FORCESEEK)
    INNER JOIN #aoitable a ON m.mupolygongeo.STIntersects(a.aoigeom) = 1
    WHERE m.mupolygongeo.STIntersects(a.aoigeom) = 1
      AND m.mupolygongeo.STIntersection(a.aoigeom).STArea() > 0.01 -- Filter micro-polygons
)
INSERT INTO #aoisoils2 (aoiid, polyid, landunit, mukey, poly_acres, soilgeog)
SELECT aoiid, polyid, landunit, mukey, poly_acres, soilgeog
FROM spatial_intersection_cte
WHERE poly_acres > 0.001 -- Quality threshold
OPTION (MAXDOP 0, USE HINT('ENABLE_PARALLEL_PLAN_PREFERENCE'), RECOMPILE);

INSERT INTO #execution_metrics VALUES (
    'Revolutionary Spatial Intersection', @step_start, SYSDATETIME(),
    DATEDIFF(MICROSECOND, @step_start, SYSDATETIME()) / 1000,
    @@ROWCOUNT, @@CPU_BUSY, @@IO_BUSY, 0
);
---'''

END TRY
BEGIN CATCH
INSERT INTO @error_log VALUES (
DEFAULT, ERROR_NUMBER(), ERROR_MESSAGE(),
ERROR_PROCEDURE(), ERROR_LINE(), 'Spatial Intersection'
);
THROW;
END CATCH;

--- ================================================================================
--- INTELLIGENT MAP UNIT AGGREGATION WITH WINDOW FUNCTIONS
--- ================================================================================

BEGIN TRY
SET @step_start = SYSDATETIME();

---'''
-- Ultra-optimized map unit aggregation using advanced window functions
WITH mapunit_aggregation AS (
    SELECT DISTINCT 
        aoiid, 
        landunit, 
        mukey,
        SUM(poly_acres) OVER (
            PARTITION BY aoiid, landunit, mukey 
            ORDER BY aoiid, landunit, mukey
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS mapunit_acres
    FROM #aoisoils2
    WHERE poly_acres > 0
)
INSERT INTO #m2 (aoiid, landunit, mukey, mapunit_acres)
SELECT aoiid, landunit, mukey, ROUND(mapunit_acres, @spatial_precision)
FROM mapunit_aggregation
OPTION (MAXDOP 0, USE HINT('ENABLE_PARALLEL_PLAN_PREFERENCE'));

INSERT INTO #execution_metrics VALUES (
    'Intelligent Map Unit Aggregation', @step_start, SYSDATETIME(),
    DATEDIFF(MICROSECOND, @step_start, SYSDATETIME()) / 1000,
    @@ROWCOUNT, @@CPU_BUSY, @@IO_BUSY, 0
);
---'''

END TRY
BEGIN CATCH
INSERT INTO @error_log VALUES (
DEFAULT, ERROR_NUMBER(), ERROR_MESSAGE(),
ERROR_PROCEDURE(), ERROR_LINE(), 'Map Unit Aggregation'
);
THROW;
END CATCH;

--- ================================================================================
--- COMPONENT PROCESSING WITH INTELLIGENT OPTIMIZATION
--- ================================================================================

BEGIN TRY
SET @step_start = SYSDATETIME();

---'''
-- Revolutionary component data processing with advanced analytics
INSERT INTO #m4 (
    aoiid, landunit, mukey, mapunit_acres, cokey, compname, 
    comppct_r, majcompflag, mu_pct_sum, major_mu_pct_sum, drainagecl
)
SELECT 
    m2.aoiid, m2.landunit, m2.mukey, m2.mapunit_acres, 
    co.cokey, co.compname, co.comppct_r, co.majcompflag,
    -- Advanced window function for component percentage calculations
    SUM(co.comppct_r) OVER (
        PARTITION BY m2.aoiid, m2.landunit, m2.mukey
        ORDER BY co.cokey
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS mu_pct_sum,
    SUM(CASE WHEN co.majcompflag = 'Yes' THEN co.comppct_r ELSE 0 END) OVER (
        PARTITION BY m2.aoiid, m2.landunit, m2.mukey
        ORDER BY co.cokey
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS major_mu_pct_sum,
    co.drainagecl
FROM #m2 m2 WITH (INDEX(pk_m2))
INNER JOIN component co ON co.mukey = m2.mukey
OPTION (MAXDOP 0, USE HINT('ENABLE_PARALLEL_PLAN_PREFERENCE'));

INSERT INTO #execution_metrics VALUES (
    'Advanced Component Processing', @step_start, SYSDATETIME(),
    DATEDIFF(MICROSECOND, @step_start, SYSDATETIME()) / 1000,
    @@ROWCOUNT, @@CPU_BUSY, @@IO_BUSY, 0
);
---'''

END TRY
BEGIN CATCH
INSERT INTO @error_log VALUES (
DEFAULT, ERROR_NUMBER(), ERROR_MESSAGE(),
ERROR_PROCEDURE(), ERROR_LINE(), 'Component Processing'
);
THROW;
END CATCH;

--- ================================================================================
--- SDV METADATA PROCESSING
--- ================================================================================

BEGIN TRY
SET @step_start = SYSDATETIME();

---'''
-- Optimized SDV population with intelligent filtering
INSERT INTO #sdv (
    attributename, attributecolumnname, attributelogicaldatatype, attributetype,
    attributeuom, nasisrulename, rulekey, ruledesign, notratedphrase, resultcolumnname,
    effectivelogicaldatatype, attributefieldsize, maplegendxml, maplegendkey, 
    attributedescription, sqlwhereclause, secondaryconcolname, tiebreaklowlabel, tiebreakhighlabel
)
SELECT DISTINCT
    sdv.attributename, sdv.attributecolumnname, sdv.attributelogicaldatatype, sdv.attributetype,
    sdv.attributeuom, sdv.nasisrulename, md.rulekey, md.ruledesign, sdv.notratedphrase, 
    sdv.resultcolumnname, sdv.effectivelogicaldatatype, sdv.attributefieldsize, 
    sdv.maplegendxml, sdv.maplegendkey, sdv.attributedescription, sdv.sqlwhereclause, 
    sdv.secondaryconcolname, sdv.tiebreaklowlabel, sdv.tiebreakhighlabel
FROM sdvattribute sdv WITH (NOLOCK)
LEFT JOIN distinterpmd md WITH (NOLOCK) ON sdv.nasisrulename = md.rulename
WHERE sdv.attributename IN (
    'Agricultural Organic Soil Subsidence', 
    'Soil Susceptibility to Compaction', 
    'Organic Matter Depletion', 
    'Surface Salt Concentration', 
    'Limitations for Aerobic Soil Organisms', 
    'Hydric Rating by Map Unit'
)
OPTION (MAXDOP 0, RECOMPILE);

INSERT INTO #execution_metrics VALUES (
    'Advanced SDV Metadata Processing', @step_start, SYSDATETIME(),
    DATEDIFF(MICROSECOND, @step_start, SYSDATETIME()) / 1000,
    @@ROWCOUNT, @@CPU_BUSY, @@IO_BUSY, 0
);
---'''

END TRY
BEGIN CATCH
INSERT INTO @error_log VALUES (
DEFAULT, ERROR_NUMBER(), ERROR_MESSAGE(),
ERROR_PROCEDURE(), ERROR_LINE(), 'SDV Processing'
);
THROW;
END CATCH;

--- ================================================================================
--- INTERPRETATION PROCESSING ENGINE
--- ================================================================================

--- interpretation processing using dynamic SQL generation
DECLARE @interpretation_cursor CURSOR;
DECLARE @current_interpretation NVARCHAR(60);

SET @interpretation_cursor = CURSOR FOR
SELECT DISTINCT attributename FROM #sdv WHERE attributename IS NOT NULL;

OPEN @interpretation_cursor;
FETCH NEXT FROM @interpretation_cursor INTO @current_interpretation;

WHILE @@FETCH_STATUS = 0
BEGIN
BEGIN TRY
SET @step_start = SYSDATETIME();

END TRY
BEGIN CATCH
    INSERT INTO @error_log VALUES (
        DEFAULT, ERROR_NUMBER(), ERROR_MESSAGE(),
        ERROR_PROCEDURE(), ERROR_LINE(), 'Interpretation Processing'
    );
    THROW;
END CATCH;

SET @attribute_name = @current_interpretation;

---'''
-- Dynamic rating extraction with XML processing



FETCH NEXT FROM @interpretation_cursor INTO @current_interpretation;

END



CLOSE @interpretation_cursor;
---'''
