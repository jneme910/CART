# Conservation Assessment Ranking Tool (CART)

## Soil Data Access documentation and interpretation logic for conservation planning

The **Conservation Assessment Ranking Tool (CART)** supports the conservation planning process by helping evaluate **resource concerns, site vulnerability, easement-related considerations, and planned conservation practices**. This repository documents the **soil data access logic, SQL query patterns, interpretive datasets, and supporting reference materials** used to derive soil-based information for CART.

It is centered on how **Soil Data Access (SDA)** is used to retrieve and shape soils information that supports CART workflows across:

- **Resource Assessment**
- **Easement Program**
- **Environmental Evaluation**
- **Outcome-oriented reporting concepts**

**Repository links**
- GitHub repository: [jneme910/CART](https://github.com/jneme910/CART)
- Project site: [jneme910.github.io/CART](https://jneme910.github.io/CART/)

---

## Start here

If you are new to this repository, use this order:

1. Read this README for the project overview.
2. Review the main SQL resources in `SQL-Library/`.
3. Explore `chapters/` for interpretation-specific documentation.
4. Open `documents/` for supporting guides and overview materials.
5. Review `TableImages/` and the project site for visual examples and output context.

This repository is especially useful for users who need to understand how soils information is retrieved, processed, and translated into CART planning outputs.

---

## Why this project matters

CART brings together **soil interpretation data, map-based workflows, SQL-driven retrieval, and conservation program logic** into a practical planning framework. This repository helps explain and document how soils information is assembled and used for conservation decision support.

This work is especially relevant for users involved in:

- conservation planning
- soil interpretation workflows
- NRCS program support
- land unit assessment
- environmental evaluation
- easement-related analysis

---

## What this repository contains

This repository includes:

- SQL scripts for CART soil data requests
- Soil Data Access query examples
- prototype outputs and documentation pages
- interpretation-specific technical chapters
- domain tables and property reference materials
- figures and workflow illustrations
- supporting program and outcomes documentation

---

## Repository structure

| Path | Purpose |
|---|---|
| `README.md` | Main repository overview and navigation |
| `SQL-Library/` | SQL scripts and SDA query resources used by CART |
| `chapters/` | Published topic-by-topic technical documentation |
| `documents/` | Guides, overview files, prototypes, and supporting reference material |
| `TableImages/` | Figures and screenshots used to explain workflows and outputs |
| `_site/` | Generated site output |

---

## Key technical components

### SQL and query resources
Primary SQL resources documented here include:

1. **SQL Server version**  
   [CART_SoilsQuery_20240925SSMS.sql](https://github.com/jneme910/CART/blob/master/SQL-Library/CART_SoilsQuery_20240925SSMS.sql)
2. **Soil Data Access version**  
   [CART_SoilsQuery_kitchensink_20240925.sql](https://github.com/jneme910/CART/blob/master/SQL-Library/CART_SoilsQuery_kitchensink_20240925.sql)
3. **AOI geometry examples**  
   [AOI_Geometry_Examples.txt](https://raw.githubusercontent.com/jneme910/CART/master/SQL-Library/AOI_Geometry_Examples.txt)

### Prototype and reference pages
- [Prototype](https://jneme910.github.io/CART/documents/rev00_Organic_Matter_Depletion.html)
- [Prototype 2](https://jneme910.github.io/CART/documents/rev00.html)
- [Prototype 3](https://jneme910.github.io/CART/documents/rev00_with_description.html)

---

## Example topics by use case

| Example / topic | Use case | Difficulty | Output |
|---|---|---|---|
| Ponding or Flooding | excess water assessment | Intermediate | interpretation / documentation |
| Depth to Water Table | seasonal high water table review | Intermediate | interpretation / documentation |
| Hydric Rating by Map Unit | hydric and easement evaluation | Intermediate | interpretation / documentation |
| Nitrogen Leaching Potential | water-quality-related assessment | Advanced | interpretation / documentation |
| Farmland Classification | easements and environmental evaluation | Beginner | interpretation / documentation |
| Available Water Storage | easement support | Beginner | interpretation / documentation |
| Soil Organic Carbon Stock | carbon and air-quality context | Intermediate | interpretation / documentation |
| Aggregate Stability | soil quality degradation analysis | Advanced | interpretation / documentation |
| Soil Data Access Metrics | SDA monitoring and reference | Intermediate | metrics / documentation |

---

## Major data sections used in CART

The soils data described in this repository is organized into four major sections:

1. **Resource Assessment**
   - Soil Quality Degradation
   - Other resource concerns
2. **EP — Easement Program**
3. **EE — Environmental Evaluation**
4. **Outcome Results** *(under development)*

---

## Representative datasets and documentation

Selected documented datasets and interpretation areas include:

- Ponding or Flooding
- Depth to Water Table
- Hydric Rating by Map Unit
- Nitrogen Leaching Potential
- Farmland Classification
- Available Water Storage
- Soil Organic Carbon Stock
- Drainage Class
- Agricultural Organic Soil Subsidence
- Soil Susceptibility to Compaction
- Organic Matter Depletion
- Surface Salt Concentration
- Suitability for Aerobic Soil Organisms
- Aggregate Stability
- Domain tables and property definitions
- Data checks and outcomes concepts

See the project site for the full chapter library and interpretation details:
[https://jneme910.github.io/CART/](https://jneme910.github.io/CART/)

---

## Resource concerns supported

CART evaluates several soil-quality-related resource concerns using interpretation data retrieved through Soil Data Access. These include:

- Subsidence
- Compaction
- Organic Matter Depletion
- Concentration of Salts and Other Chemicals
- Soil Organism Habitat Loss or Degradation
- Aggregate Instability

These interpretation outputs are used to support land-unit-level ratings and downstream planning logic within CART.

---

## How CART uses Soil Data Access

At a high level, the workflow is:

1. A land unit is selected.
2. A request is assembled using SQL and bounding coordinates.
3. Soil Data Access returns soils information and interpretation outputs.
4. Background map processing supports land-unit analysis.
5. Component- and rating-level information is summarized into final planning values.

This repository documents the logic and reference materials behind that process.

---

## Screenshots and figures

This repository already includes visual materials in `TableImages/` and the published project site. These figures help explain:

- land unit selection context
- background map processing
- service data returned from Soil Data Access
- detailed land unit ratings
- final land unit ratings and domain ordering

For best presentation value, consider surfacing 2–3 of the strongest images near the top of the README in a future pass.

---

## Notes on common SDA patterns

Users working with this repository will encounter recurring SDA patterns such as:

- SQL requests driven by land-unit geometry and identifiers
- component- and interpretation-level aggregation
- domain-based rating logic
- use of AOI geometry inputs
- translation of raw soils outputs into planning-oriented summary values

Adding short examples of these patterns in future updates would make onboarding even easier for new technical users.

---

## Audiences

This repository is most useful for:

- soil scientists
- conservation planners
- GIS specialists
- analysts working with SSURGO/SDA outputs
- developers supporting conservation tools
- technical users who need documentation for CART soil logic

---

## Related documentation and outputs

Additional repository materials include:

- [CART User’s Guide](https://github.com/jneme910/CART/blob/master/documents/CART_Resource_Concern_Assessment_Draft.docx)
- [CART Overview](https://github.com/jneme910/CART/blob/master/documents/CART_Overview.pdf)
- [Outcomes Design Concept](https://jneme910.github.io/CART/chapters/Outcomes)
- [CART-NPAD data connections](https://github.com/jneme910/CART/blob/master/documents/npad_70_051419.pdf)
- [Soil Data Access Metrics](https://jneme910.github.io/CART/chapters/Metric)

---

## Technologies and data themes

- Soil Data Access (SDA)
- SQL / T-SQL
- SSURGO-derived soils information
- soil interpretations
- NRCS conservation workflows
- GitHub Pages documentation
- map-based decision support

---

## Acknowledgements

This repository reflects collaboration across NRCS staff, developers, cartographers, analysts, and technical specialists supporting CART and related conservation planning efforts.

---

## Best-practice improvement ideas

To strengthen this repository further for professional visibility, consider adding:

- a short architecture or workflow diagram
- screenshots grouped into a quick visual overview
- a “Who this helps” section with primary user types
- a changelog or release history for major updates

---

If you work with **soil data systems, NRCS workflows, conservation planning, or geospatial decision support**, this repository provides a detailed view into how soils information can be operationalized for program and planning use.
