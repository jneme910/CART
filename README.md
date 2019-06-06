#  Conservation Assessment Ranking Tool (CART)
The Conservation Assessment Ranking Tool (CART) will assess clients’ resource concerns, planned practices, and site vulnerability as part of the conservation planning process and will rank client applications for funding. CART starts with a site-specific risk threshold for each resource concern that is based on intrinsic site characteristics, like soils and climate. The assessment then evaluates the benefits of site-specific management to determine when a resource concern is adequately treated. Management credit includes the ways crops are grown and conservation practices that are applied. Management credits are summed and compared to the threshold for existing conditions and planning alternatives. For program ranking purposes, these same points are used as the basis for prioritization, but ranking may be further modified by identified priorities, special considerations, or both.

This query is meant to be run through the [Soil Data Access](https://sdmdataaccess.nrcs.usda.gov/Query.aspx) tabular data query portal. This interface queries current databases maintained by the U.S. National Cooperative Soil Survey. 

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






   

