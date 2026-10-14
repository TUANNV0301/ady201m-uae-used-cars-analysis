# Project Charter

## Working title
Exploring listed prices of used cars in the UAE

## Problem and motivation
Buyers and sellers need to understand how asking prices differ across vehicle attributes and locations. This project describes relationships in a public set of used-car listings. It does not claim to estimate final transaction prices.

## Main question
How are listed prices associated with car age, mileage, make, body type, and emirate in this dataset?

## Research questions
1. How do median asking prices vary by year, mileage band, make, and body type?
2. Which numerical attributes have the strongest linear association with listed price?
3. How does a simple baseline regression using year and mileage perform on a held-out sample?

## Scope and assumptions
- One CSV row is treated as one listing; the source description reports 10,000+ listings.
- `Price` is treated as asking/listed AED price, not confirmed transaction price.
- The target is the supplied `Price`; predictors are selected from vehicle attributes available in the CSV.
- The present analysis is descriptive and exploratory. Associations are not causal claims.
- The source page identifies CC BY-SA 4.0. Attribution and share-alike terms should be followed when redistributing the source data or adaptations.
- The exact official assignment brief/rubric was not included in the request (the placeholder was left empty). Therefore the deliverables below are a course-aligned working scope, not a claim about official grading requirements.

## Method
Follow a compact data-science workflow: define the question, load and profile data, clean documented missing/whitespace values, query a normalized SQLite database, explore descriptive statistics, test a focused group comparison, fit and evaluate a baseline regression, and communicate limits and findings.

## Success criteria
- Reproducibly load the provided source CSV.
- Explain the 12 fields and document data-quality decisions.
- Demonstrate SQL filtering, aggregation, and joins from Python.
- Provide Python descriptive statistics, clear visualizations where dependencies permit, and a reproducible baseline model evaluation.
- Keep conclusions bounded to this dataset and its listed prices.
