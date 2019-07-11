---
title: "Depth to Water Table"
author: "Jason Nemecek"
date: "2019-07-11"
output: 
  html_document: 
    keep_md: true
  bibliography: POX_bib.bibtex
  csl: nature.csl
---



<style>
   tbody tr:nth-child(odd){
    background-color: #F7FBFF;
  }
</style>

**"Water table"** refers to a saturated zone in the soil. It occurs during specified months. Estimates of the upper limit are based mainly on observations of the water table at selected sites and on evidence of a saturated zone, namely grayish colors (redoximorphic features) in the soil. A saturated zone that lasts for less than a month is not considered a water table.    This attribute is actually recorded as three separate values in the database. A low value and a high value indicate the range of this attribute for the soil component. A "representative" value indicates the expected value of this attribute for the component. For this soil property, only the representative value is used.


## Seasonal High Water Table

### Description:  
Groundwater or a perched water table causing saturated conditions near the surface degrades water resources or restricts capability of land to support its intended use.

### Objective:  Reduce seasonally high water table.

### Analysis within CART:
Each PLU regardless of land use will default to a "not assessed" status for seasonal high water table. The planner will identify this resource concern based on site specific conditions. If the planner identifies the resource concern it will trigger a soil data web service to determine if the water table is within 18 inches of the surface.  If a high water table is identified a threshold of 50 will be set. 








