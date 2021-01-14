# Conservation Assessment Ranking Tool (CART)
Jason Nemecek and Steve Peaslee 

July 15, 2019 

The Conservation Assessment Ranking Tool (CART) is designed for use in the conservation planning process to assess resource concerns, planned practices, and site vulnerability. It ranks applications for USDA conservation funding. CART starts with a site-specific risk threshold for each resource concern. The thresholds are based on intrinsic site characteristics, such as soils and climate. The tool evaluates the benefits of site-specific management for treating resource concerns. A “management credit” score is assigned to each site based on such factors as the methods used for crop production and the conservation practices that are applied. The scores are summed, and the total is compared to the threshold for existing conditions and to planning alternatives. The scores can also be used to prioritize program ranking, which may be further modified by identified priorities, special considerations, or both.

This documentation describes the SQL queries that access soils data for CART.  The queries described in this documentation run through the [Soil Data Access](https://sdmdataaccess.nrcs.usda.gov/Query.aspx) tabular data query portal.  The portal accesses current databases maintained by the U.S. National Cooperative Soil Survey.

### Structured Query Language (SQL) script for the Conservation Assessment Ranking Tool: Soil.
1.  SQL Server version: [Click here](https://github.com/jneme910/CART/blob/master/SQL-Library/CART_SoilsQuery_kitchensink_20200109.sql)
2.  Soil Data Access SQL version: [Click here](https://github.com/jneme910/CART/blob/master/SQL-Library/SDA_CART_SoilsQuery_kitchensink_20190612.txt)
3.  Area of Interest (AOI) Geometry examples to copy into the SQL script:  [Click here](https://raw.githubusercontent.com/jneme910/CART/master/SQL-Library/AOI_Geometry_Examples.txt)

### The soils data used in CART can be found in four main sections.
1. Resource Assessment (Resource Concerns); 
   * Soil Quality Degradation 
   * Other
2.	EP—Easement Program
3.	EE—Environmental Evaluation
4.	Outcome Results (Under Development)


 ||Datasets|Purpose* |Documentation| Section|
|-----|----------|--------|--------|----------------------------------------|
|1| Ponding or Flooding |RA, EP|[Click here](https://jneme910.github.io/CART/chapters/Ponding_or_Flooding)|Excess Water-Ponding and Flooding, Easements|
|2|Depth to Water Table |RA, EP |[Click here](https://jneme910.github.io/CART/chapters/Depth_to_Water_Table) |Excess Water-Seasonal High Water Table, Easements|
|3|Hydric Rating by Map Unit |RA, EP |[Click here](https://jneme910.github.io/CART/chapters/Hydric_Rating_by_Map_Unit)|Excess Water: Seeps; Air Quality: Emissions of Greenhouse Gases; Easements|
|4 |Nitrogen Leaching |RA | [Click here](https://jneme910.github.io/CART/chapters/Nitrogen_Leaching_Potential)|Future Development (Water Quality-Diffuse Nutrient, Pesticide and Pathogens Transport to Water
 |5|Farmland Classification |EE, EP |[Click here](https://jneme910.github.io/CART/chapters/Farmland_Classification) |Easements; Environmental Evaluation|
|6|Available Water Storage |EP |[Click here](https://jneme910.github.io/CART/chapters/Available_Water_Storage) |Easements|
|7|Soil Organic Carbon Stock|RA, EP |[Click here](https://jneme910.github.io/CART/chapters/Soil_Organic_Carbon_Stock)|Easements; Air Quality: Emissions of Greenhouse Gases |
 |8|Drainage Class |EP |[Click here](https://jneme910.github.io/CART/chapters/Drainage_Class) |Easements|
|9|Organic Soils |RA |See 'Hydric Rating by Mapunit'|---|
|10|Agricultural Organic Soil Subsidence |RA |[Click here](https://jneme910.github.io/CART/chapters//EditedRMD/Agricultural_Organic_Soil_Subsidence) |Soil Quality Degradation: Subsidence|
|11|Soil Susceptibility to Compaction |RA |[Click here](https://jneme910.github.io/CART/chapters/Soil_Susceptibility_to_Compaction)|Soil Quality Degradation:Compaction| 
|12|Soil Susceptibility Organic Matter Depletion |RA |[Click here](https://jneme910.github.io/CART/chapters/Organic_Matter_Depletion)|Soil Quality Degradation:Organic Matter Depletion|
|13|Surface Salt Concentration |RA |[Click here](https://jneme910.github.io/CART/chapters/Surface_Salt_Concentration)|Soil Quality Degradation:Concentration of Salts and Other Chemicals
|14|Suitability for Aerobic Soil Organisms |RA |[Click here](https://jneme910.github.io/CART/chapters/Suitability_for_Aerobic_Soil_Organisms)|Soil Quality Degradation:Soil Organism Habitat Loss and Degradation|
|15|Aggregate stability |RA |[Click here](https://jneme910.github.io/CART/chapters/Aggregate_stability) |Soil Quality Degradation:Aggregate Instability|
|16| Domain Tables|---|  [Click here](https://jneme910.github.io/CART/chapters/CART_Soil_Data_Access_Domains) |---|
|17|Soil Property List by Interpretation |---| [Click here](https://jneme910.github.io/CART/chapters/Soil_Property_List_by_Soil_Interpretation) |---|
|18|Soil Property List and Column Descriptions |---|[Click here](https://jneme910.github.io/CART/chapters/Soil_Propert_List_and_Definition)|---|
|19|Data Checks |--- |[Click here](https://jneme910.github.io/CART/chapters/Soil_Data_Checks)|---|
|20|Outcomes |--- |[Click here](https://jneme910.github.io/CART/chapters/Outcomes) |---|
|21|Future Development|--- |[Click here](https://jneme910.github.io/CART/chapters/future) |---|
|22|CART User’s Guide|--- |[Click here](https://github.com/jneme910/CART/blob/master/documents/CART_Resource_Concern_Assessment_Draft.docx) |---|
|23|CART Overview |--- |[Click here](https://github.com/jneme910/CART/blob/master/documents/CART_Overview.pdf) |---|
|24|Soil Data Access Metrics|---|[Click here](https://jneme910.github.io/CART/chapters/Metric) |---| 

 *RA—Resource Assessment; EP—Easement Program; EE—Environmental Evaluation; RT—Ranking Tool

Soil properties can be divided into two broad categories: intrinsic and non-intrinsic. Intrinsic soil properties are those empirical soil properties that are not based on any other soil properties (e.g., content of very fine sand). Non-intrinsic soil properties tend to be derived from multiple intrinsic soil properties (e.g., K factor). Non-intrinsic soil properties also tend to be interpretive in nature. Examples of non-intrinsic soil properties include Farmland Classification, T Factor, and Wind Erodibility Group.

# Resource Concerns
## Soil Quality Degradation 
CART evaluates six resource concerns related to soil quality degradation. Each involves analysis of soil interpretation data from the Soil Data Access Query service. Soil maps and reports for these interpretations are also available from Web Soil Survey. Both the Soil Data Access Query service and Web Soil Survey connect to the same soils database. Five of the resources concerns use traditional soil interpretations; the sixth, Aggregate Stability, is written entirely in SQL. 

||Resource Concerns|Related Soil Interpretation
|-----|----------|--------|
|1|Subsidence|Agricultural Organic Soil Subsidence|
|2|	Compaction|	Soil Susceptibility to Compaction|
|3|	Organic Matter Depletion|Organic Matter Depletion|
|4	|Concentration of Salts and Other Chemicals|	Surface Salt Concentration|
|5| Soil organism habitat loss or degradation|Suitability for Aerobic Soil Organisms|
|6|Aggregate instability| Aggregate stability|

### Soil Data Access Requests by CART
1.	The request for soils data begins once land units have been selected (fig. 1).
2. The request is in the form of an SQL query and contains:
   * Land unit identifier
   * Bounding coordinates
3.	CART automatically sends the request to Soil Data Access Query Service.
4.	Map layers are processed in the background and are not displayed.

![Example: Park County, Wyoming](https://jneme910.github.io/CART/TableImages/Park_County_WY.png)

Figure 1.—This map is here to show you a landunit in Park County, Wyoming.
### MAP DATA PROCESSING
 
![Example: Map data is processed in the background](https://jneme910.github.io/CART/TableImages/Map%20Data%20is%20processed%20in%20the%20background.PNG)

Figure 2.—A map of the soils in the selected area and a map showing the soil interpretation for surface salt concentration. 

Map data is processed in the background. In figure 2, the map on the left shows 8 different soils within a land unit. The map on the right illustrates risk of surface salinization. The red polygon indicates an area of high risk for surface salinization. The yellow areas have a moderate risk, and the green areas are low risk.

### Service Data

In the following table, the query service returned soils information for ”Risk of Surface Salt Concentration” within the land unit. The soil interpretation rating was used to calculate the CART rating.  The table shows the magnitude of the CART rating as both a land unit percentage and as land unit acres.

![Example: Service Data](https://jneme910.github.io/CART/TableImages/Service%20Data.PNG)

Areas with the highest risk are assigned a rating of 1. Areas with a lower risk are assigned a larger rating number. Rating values are calculated using soils data at the component level.

### Land unit Detailed Ratings

The service request calculates the rolling sum values for rating acres and rating percent for each resource concern and finds the single most limiting rating (per land unit) that comprises  **at least 10% by area or 10 acres.** 

![Example: Land Unit Detail Ratings](https://jneme910.github.io/CART/TableImages/Land%20Unit%20Detail%20Ratings.PNG)

In this example, the most limiting rating that meets these criteria is the second row.  This rating is provided to the CART application as the land unit rating for Concentration of Salts and Other Chemicals. It is important to understand that the Web Soil Survey does not have the functionality for calculating the land unit ratings. Web Soil Survey is only designed to provide soil maps and reports.

### Final Land unit Ratings 

For each of the resource concerns, the final land unit ratings (which are derived from Soil Data Access) are returned to CART for awarding of points. The publication date of the soils data is also returned to CART as metadata. This metadata ensures that the Soil Quality Degradation ratings can be associated with a particular version of SSURGO soils data.

![Example: Final Land Unit Ratings](https://jneme910.github.io/CART/TableImages/Final%20Land%20Unit%20Ratings.PNG)

The following domain table contains an ordered list of all possible rating values. 

![Example: Domain](https://jneme910.github.io/CART/TableImages/Domain.PNG)

# EASEMENTS
Click a heading below for specific information on a listed query.

1. [Soil Organic Carbon Stock](https://jneme910.github.io/CART/chapters/Soil_Organic_Carbon_Stock)
2. [Farmland Classification](https://jneme910.github.io/CART/chapters/Farmland_Classification)
3. [Hydric Soil Rating by Map Unit](https://jneme910.github.io/CART/chapters/Hydric_Rating_by_Map_Unit)
4. [Ponding or Flooding Frequency](https://jneme910.github.io/CART/chapters/Ponding_or_Flooding)
5. [Depth to Water Table](https://jneme910.github.io/CART/chapters/Depth_to_Water_Table)
6. [Drainage Class](https://jneme910.github.io/CART/chapters/Drainage_Class)
7. [Available Water Storage](https://jneme910.github.io/CART/chapters/Available_Water_Storage)

# Environmental Evaluation (CPA-52)
Click a heading below for specific information on a listed query.

1. [Farmland Classification](https://jneme910.github.io/CART/chapters/Farmland_Classification)
2. [Hydric Soils Rating by Mapunit](https://jneme910.github.io/CART/chapters/Hydric_Rating_by_Map_Unit)

# Outcomes
The programming proposed for outcomes is intended to provide NRCS leadership with the ability to model data and report the natural resource impacts and outcomes of conservation practices, systems, programs, and initiatives. It will also facilitate the identification of conservation treatment needs and the reporting of outcomes for NRCS and USDA.

1. Outcomes Design Concept: [Click here](https://jneme910.github.io/CART/chapters/Outcomes)
2. Data connections (CART-NPAD): [Click here](https://github.com/jneme910/CART/blob/master/documents/npad_70_051419.pdf)

# Acknowledgements
1.	Steve Campbell: Soil Scientist, NRCS
2.	Skye Wills: Soil Scientist, NRCS
3.	Chad Volkman: Cartographer, NRCS
4.	Phil Anzel: Senior Software Developer, Vistronix
5.	Susan McGlasson: Database Administrator, Vistronix
6.	Bob Dobos: Soil Scientist, NRCS
7.	Cathy Seybold: Soil Scientist, NRCS
8.	Jeff Thomas: Soil Scientist, NRCS
9.	Mike Robotham: National Leader for Technical Soil Services, NRCS
10.	Laura Morton: Management Analyst, NRCS
11.	Aaron Lauster: National Sustainable Agriculture Leader, NRCS
12.	Casey Sheley: Natural Resource Specialist, NRCS
13.	Eric Hesketh: Soil Scientist, NRCS
14.	Greg Zwicke: Environmental Engineer, NRCS
15.	Matt Flint: Natural Resource Specialist, NRCS
16.	Danielle Balduff: Natural Resource Specialist, NRCS
17.	Breanna Barlow: Management Analyst, NRCS
18.	Barry Fisher: Central Region Soil Health Team Leader, NRCS
19.	Robin Plummer: Developer, NRCS
20.	Aaron Bustamante: 
21.	Pam Thomas: Associate Director of Soil Survey Programs, NRCS

*With support from the Resource Concern Team and Workgroups.* 


