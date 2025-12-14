---
layout: post
title: Evolution of the Information System 2005-2012
subtitle: 
comments: true
mathjax: true
author: Slobodan Ninkov
---

# Evolution of an Information System (2005–2012)

*By Slobodan Ninkov*  
*Posted on December 7, 2025*

This short essay reflects on how a large, real-time transactional system evolved its reporting and analytics stack between 2005 and 2012, based on my work at the State Lottery of Serbia.

While the technologies have changed significantly since then, the **failure modes, trade-offs, and organizational dynamics** described here remain largely the same today.



## Phase 1: Manual reporting

The earliest phase relied on manual report generation. This worked briefly, but quickly became infeasible given the number, frequency, and urgency of reports management expected. Sales data arrived continuously from thousands of POS machines, and expectations quickly shifted toward near–real-time visibility.

This was the classic “data analyst phase”: workable at small scale, brittle at real scale.



## Phase 2: Reporting directly on live data

The next step was to run reports directly against the live transactional database. At the time, this seemed efficient and elegant.

Reality intervened quickly.

We learned the hard way that you cannot optimize simultaneously for:
- high-volume inserts from distributed systems, and
- frequent, ad-hoc analytical queries

Every report request slowed the transactional workload. The system became unpredictable under load, and the pain was immediate and visible.

This was our first practical lesson in why **OLTP and OLAP must be separated**.



## Phase 3: Nightly ETL and early near-real-time pipelines

We introduced nightly automated parsing and loading to prepare data for reporting. This stabilized most reporting needs, but management still wanted some indicators in near real time.

The result was a hybrid approach: what would today be described as an early map-reduce–style pipeline. Real-time data was parsed and aggregated into small, fast tables updated multiple times per second, while heavier reports relied on nightly-prepared data.

This worked, but at the cost of additional complexity and operational risk. Freshness was always traded against stability.



## Phase 4: Application sprawl and access control

As reports and dashboards multiplied, they spread across the company as standalone web pages. Everyone could see everything.

Predictably, top management was not enthusiastic about discovering that company-wide financial figures were accessible to anyone who happened to open the right URL.

The solution was consolidation: a single web-based Information System with authentication, permissions, and basic security controls.

This solved visibility concerns, but did nothing to slow the next problem.



## Phase 5: Report explosion and KPI overload

Once access was centralized, demand exploded.

Every department wanted more reports. At the same time, the system was expanding to support new lottery games and integrations with external partners. Reporting grew faster than development capacity.

Eventually, top management reached saturation: too many dashboards, too many KPIs, and conflicting numbers depending on who produced the report.

The business response was to define a **single, standardized set of KPIs** aligned with company goals, replacing ad-hoc departmental metrics. This helped restore trust, but reduced flexibility.



## Phase 6: Self-service and the Excel era

When sales began declining, Marketing and Sales requested increasingly exploratory reports, often best summarized as “compare everything to everything else.”

The only scalable answer was self-service analytics. We introduced Microsoft data warehouse technologies (SSIS and SSAS). Data was prepared nightly, processing took roughly six hours, and multiple consistency checks were built in.

Technically, this was a success.

Organizationally, Excel became the new Information System.

Teams built their own reports. Versions multiplied. Ownership blurred. Eventually, we noticed that almost no one logged into the centralized IS anymore.



## Phase 7: Identity, access, and the Excel incident

Despite earlier efforts, we found ourselves back where we started.

Even with good intentions, trusting people not to forward Excel files proved unrealistic. The situation peaked when the CEO shared an Excel file with CEO-level access to Payments, which was then accidentally forwarded to Sales. Overnight, half the company had visibility they were never meant to have.

That incident finally provided enough leverage to resolve a long-standing internal debate: introducing centralized identity and access management.

Active Directory was adopted. Permissions were enforced at the data level. Excel files began to respect user identity automatically.

For the first time in years, access control stopped being a guessing game.



## What still holds true today

Looking back, several patterns repeat regardless of tooling or era:

- You cannot mix high-volume transactional workloads with analytical queries without pain  
- Near-real-time reporting always increases architectural and operational complexity  
- Self-service analytics without identity and access control devolves into chaos  
- KPI proliferation erodes trust faster than lack of data  
- Excel will become a system if governance is missing  
- Identity and access management is a **data problem**, not just an IT problem  





