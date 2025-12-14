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



