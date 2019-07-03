# Conservation Assessment Ranking Tool (CART)
Jason Nemecek and Steve Peaslee 

June 19, 2019


The Conservation Assessment Ranking Tool (CART) will assess clients’ resource concerns, planned practices, and site vulnerability as part of the conservation planning process and will rank client applications for funding. CART starts with a site-specific risk threshold for each resource concern that is based on intrinsic site characteristics, like soils and climate. The assessment then evaluates the benefits of site-specific management to determine when a resource concern is adequately treated. Management credit includes the ways crops are grown and conservation practices that are applied. Management credits are summed and compared to the threshold for existing conditions and planning alternatives. For program ranking purposes, these same points are used as the basis for prioritization, but ranking may be further modified by identified priorities, special considerations, or both.

This query is meant to be run through the [Soil Data Access](https://sdmdataaccess.nrcs.usda.gov/Query.aspx) tabular data query portal. This interface queries current databases maintained by the U.S. National Cooperative Soil Survey.  [SQL Server SQL version - Click here](https://github.com/jneme910/CART/blob/master/SQL-Library/CART_SoilsQuery_kitchensink_20190612.sql) or [Soil Data Access SQL version - Click here](https://github.com/jneme910/CART/blob/master/SQL-Library/SDA_CART_SoilsQuery_kitchensink_20190612.txt) for the Conservation Assessment Ranking Tool soil SQL Script. 

 ||Datasets|Purpose* |Location| Section|
|-----|----------|--------|--------|----------------------------------------|
|1| Ponding or Flooding |RA, EP|[Click here](https://jneme910.github.io/CART/chapters/Ponding_or_Flooding)|Excess Water-Ponding and Flooding, Easements|
|2|Depth to Water Table |RA, EP |[Click here](https://jneme910.github.io/CART/chapters/Depth_to_Water_Table) |Excess Water-Seasonal High Water Table, Easements|
|3|Hydric Rating by Map Unit |RA, EP |[Click here](https://jneme910.github.io/CART/chapters/Hydric_Rating_by_Map_Unit)|Excess Water-Seeps, Air Quality-Emmisions of Greenhouse Gases, Easements|
|4 |Nitrogen Leaching |RA | |
 |5|Farmland Classification |EE, EP |[Click here](https://jneme910.github.io/CART/chapters/Farmland_Classification) |Easements, Environmental Evaluation|
|6|Availible Water Storage |EP |[Click here](https://jneme910.github.io/CART/chapters/Available_Water_Storage) |Easements|
|7|Soil Organic Carbon Stock|EP |[Click here](https://ncss-tech.github.io/sda-lib/chapters/Soil%20Organic%20Carbon%20Stocks.html)|Easements, Air Quality-Emmisions of Greenhouse Gases |
 |8|Drainage Class |EP |[Click here](https://jneme910.github.io/CART/chapters/Drainage_Class) |Easements|
|9|Organic Soils |RA |See 'Hydric Rating by Mapunit'|---|
|10|Agricultural Organic Soil Subsidence |RA |[Click here](https://jneme910.github.io/CART/chapters/Agricultural_Organic_Soil_Subsidence) |Soil Quality Degradation-Subsidence |
|11|Soil Susceptibility to Compaction |RA |[Click here](https://jneme910.github.io/CART/chapters/Soil_Susceptibility_to_Compaction)|Soil Quality Degradation-Compaction| 
|12|Organic Matter Depletion |RA |[Click here](https://ncss-tech.github.io/sda-lib/chapters/Organic_Matter_Depletion)|Soil Quality Degradation-Organic Matter Depletion|
|13|Surface Salt Concentration |RA |[Click here](https://ncss-tech.github.io/sda-lib/chapters/Surface_Salt_Concentration.)|Soil Quality Degradation-Concentration of Salts and Other Chemicals}
|14|Suitability for Aerobic Soil Organisms |RA |[Click here](https://ncss-tech.github.io/sda-lib/chapters/Suitability_for_Aerobic_Soil_Organism)|Soil Quality Degradation-Soil Organism Habitat Loss and Degradation|
|15|Aggregate stability |RA |[Click here](https://jneme910.github.io/CART/chapters/Aggregate_stability) |Soil Quality Degradation-Aggregate Instability|
|16| Domain Tables|---|  [Click here](https://jneme910.github.io/CART/chapters/CART_Soil_Data_Access_Domains) |---|
|17|Soil Property List by Interpretation |---| [Click here](https://jneme910.github.io/CART/chapters/Soil_Property_List_by_Soil_Interpretation) |---|
|18|Soil Property List and Column Descriptions |---|[Click here](https://jneme910.github.io/CART/chapters/Soil_Propert_List_and_Definition)|---|
|19|Data Checks |--- |[Click here](https://jneme910.github.io/CART/chapters/Soil_Data_Checks)|---|
 
 *RA - Resource Assessment; EP- Easement Program; EE - Environmental Evaluation; RT - Ranking Tool
 
 Soil properties themselves can be divided into two broad categories, intrinsic soil properties and non-intrinsic soil
properties. Intrinsic soil properties are those empirical soil properties that are not based on any other soil properties
(very fine sand content). Non-intrinsic soil properties tend to be derived from multiple intrinsic soil properties
(Kfactor). Non-intrinsic soil properties tend to be interpretive in nature. Examples of non-intrinsic soil properties
include Farmland Classification, T Factor and Wind Erodibility Group.


# Resource Concerns
## Soil Quality Degradation 
CART has 6 resource concerns related to Soil Quality Degradation and each will involve analysis of soil interpretation data from the Soil Data Access Query service. Soil maps and reports for these interpretations are also available from Web Soil Survey. Both applications are connecting to the same soils database. 5 of the resources concerns use traditional soil interpretations whereas Aggregation stability is written entirely in SQL. 

||Resource Concerns|Soil Interpretation
|-----|----------|--------|
|1|Subsidence|Agricultural Organic Soil Subsidence|
|2|	Compaction|	Soil Susceptibility to Compaction|
|3|	Organic Matter Depletion|Organic Matter Depletion|
|4	|Concentration of Salts and Other Chemicals|	Surface Salt Concentration|
|5| Soil organism habitat loss or degradation|Suitability for Aerobic Soil Organisms|
|6|Aggregate instability| Aggregate stability|

### Soil Data Access Requests by CART
1. The request for soils data begins once land units have been selected.
2. The request is in the form of an SQL query and contains:
   * Land unit identifier
   * Bounding coordinates
3. CART will automatically send the request to Soil Data Access Query Service.
4. Map layers are processed in the background and will not be displayed.

![Example: Park County, Wyoming](https://github.com/jneme910/CART/blob/master/TableImages/Park_County_WY.png)

### Map data is processed in the background
 
![Example: Map data is processed in the background](https://github.com/jneme910/CART/blob/master/TableImages/Map%20Data%20is%20processed%20in%20the%20background.PNG)

The map on the left shows 8 different soils within this land unit. The map on the right side illustrates risk of surface salinization. The red polygon indicates an area of high risk for surface salinization, yellow areas have a moderate risk and green areas are low risk.

### Service Data

In the example below, the Query service has returned soils data for the ‘Risk of Surface Salt Concentration’ within the land unit. The rating data shown in table below is then used to calculate the magnitude of each rating as both a land unit percentage and as land unit acres. 

![Example: Service Data](https://github.com/jneme910/CART/blob/master/TableImages/Service%20Data.PNG)

Areas with the highest risk will be assigned a rating number of 1. Areas with a lower risk will be assigned a larger rating number. Rating values are calculated using soils data at the component level.

### Land unit Detailed Ratings

The service request then calculates the rolling sum values for rating_acres and rating percent for each resource concern and finds the single most limiting rating (per land unit) that comprises **at least 10% by area or 10 acres.** 

![Example: Land Unit Detail Ratings](https://github.com/jneme910/CART/blob/master/TableImages/Land%20Unit%20Detail%20Ratings.PNG)

In this example, it is the second row that meets these criteria and will be provided to the CART application as the land unit rating for Concentration of Salts and Other Chemicals. It is important to understand that the functionality for calculating land unit ratings is not available from Web Soil Survey. It is only designed to provide soil maps and reports. 

### Final Land unit Ratings 

The final Soil Data Access land unit ratings for each of the resource concerns will be returned to CART for awarding of points. The publication date of the soils data will also be returned to CART as metadata. This will ensure that any of the Soil Quality Degradation ratings can be tied back to a particular version of SSURGO soils data.

![Example: Final Land Unit Ratings](https://github.com/jneme910/CART/blob/master/TableImages/Final%20Land%20Unit%20Ratings.PNG)


This domain table contains an ordered list of all possible rating values.
![Example: Domain](https://github.com/jneme910/CART/blob/master/TableImages/Domain.PNG)

# EASEMENTS

1. [Soil Organic Carbon Stock](https://ncss-tech.github.io/sda-lib/chapters/Soil%20Organic%20Carbon%20Stocks.html)
2. [Farmland Classification](https://jneme910.github.io/CART/chapters/Farmland_Classification)
3. [Hydric Soil Rating by Map Unit](https://jneme910.github.io/CART/chapters/Hydric_Rating_by_Map_Unit)
4. [Ponding or Flooding Frequency](https://jneme910.github.io/CART/chapters/Ponding_or_Flooding)
5. [Depth to Water Table](https://jneme910.github.io/CART/chapters/Depth_to_Water_Table)
6. [Drainage Class](https://jneme910.github.io/CART/chapters/Drainage_Class)
7. [Availible Water Storage](https://jneme910.github.io/CART/chapters/Available_Water_Storage)

# Environmental Evaluation (CPA-52)
1. [Farmland Classification](https://jneme910.github.io/CART/chapters/Farmland_Classification)
2. [Hydric Soils Rating by Mapunit](https://jneme910.github.io/CART/chapters/Hydric_Rating_by_Map_Unit)

# Outcomes
Provides leadership within NRCS for data modeling and reporting the natural resource impacts and outcomes of conservation practices, systems, programs and initiatives; and facilitates the ability to identify conservation treatment needs and the ability to report outcomes for NRCS and USDA.  

1. [Outcomes Design Concept](https://jneme910.github.io/CART/chapters/Outcomes)
2. Data connections (CART-NPAD) [Click Here](https://github.com/jneme910/CART/blob/master/documents/npad_70_051419.pdf)























   

