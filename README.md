#  Conservation Assessment Ranking Tool (CART)
The Conservation Assessment Ranking Tool (CART) will assess clients’ resource concerns, planned practices, and site vulnerability as part of the conservation planning process and will rank client applications for funding. CART starts with a site-specific risk threshold for each resource concern that is based on intrinsic site characteristics, like soils and climate. The assessment then evaluates the benefits of site-specific management to determine when a resource concern is adequately treated. Management credit includes the ways crops are grown and conservation practices that are applied. Management credits are summed and compared to the threshold for existing conditions and planning alternatives. For program ranking purposes, these same points are used as the basis for prioritization, but ranking may be further modified by identified priorities, special considerations, or both.

This query is meant to be run through the [Soil Data Access](https://sdmdataaccess.nrcs.usda.gov/Query.aspx) tabular data query portal. This interface queries current databases maintained by the U.S. National Cooperative Soil Survey. 

# Resource Concerns
## [Soil Quality Degradation](https://ncss-tech.github.io/CART/chapters/SOIL%20QUALITY%20DEGRADATION.html) 

CART has 6 resource concerns related to Soil Quality Degradation and each will involve analysis of soil interpretation data from the Soil Data Access Query service. Soil maps and reports for these interpretations are also available from Web Soil Survey. Both applications are connecting to the same soils database.

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

![Example: Service Data](https://github.com/jneme910/CART/blob/master/TableImages/https://github.com/jneme910/CART/blob/master/TableImages/Service%20Data.PNG)

Areas with the highest risk will be assigned a rating number of 1. Areas with a lower risk will be assigned a larger rating number. Rating values are calculated using soils data at the component level.

### Land unit Detailed Ratings

The service request then calculates the rolling sum values for rating_acres and rating percent for each resource concern and finds the single most limiting rating (per land unit) that comprises **at least 10% by area or 10 acres.** 

![Example: Land Unit Detail RatingsService Data](https://github.com/jneme910/CART/blob/master/TableImages/Land%20Unit%20Detail%20Ratings.PNG)

In this example, it is the second row that meets these criteria and will be provided to the CART application as the land unit rating for Concentration of Salts and Other Chemicals. It is important to understand that the functionality for calculating land unit ratings is not available from Web Soil Survey. It is only designed to provide soil maps and reports. 

### Final Land unit Ratings 

The final Soil Data Access land unit ratings for each of the resource concerns will be returned to CART for awarding of points. The publication date of the soils data will also be returned to CART as metadata. This will ensure that any of the Soil Quality Degradation ratings can be tied back to a particular version of SSURGO soils data.

![Example: Final Land Unit Ratings](https://github.com/jneme910/CART/blob/master/TableImages/Final%20Land%20Unit%20Ratings.PNG)


















   

