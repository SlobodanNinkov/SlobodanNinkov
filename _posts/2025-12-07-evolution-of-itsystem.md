---



layout: post



title: Evolution of the Information System 2005-2012



subtitle: 



comments: true



mathjax: true



author: Slobodan Ninkov



---



This short essay is inspired by my job in the State Lottery of Serbia between May 2005 and May 2012. In the essay, I tried to summarize how the state lottery's Information System (IS) evolved.



First steps were manual report generation—the data analyst way. Unfortunately, this wasn’t feasible given the number and frequency of reports. Management wanted to track sales in real time.



Next, we generated reports against live data. At the time, it seemed like a great idea, but we quickly learned you can’t have both fast inserts (from 1000s of POS machines) and fast queries (needed for reports) on the same database. Every report request from anyone in the building slowed down the data server.



That’s when we learned why there is wisdom in splitting data access into OLTP and OLAP databases.



Our second phase was nightly automated data parsing and loading, preparing data for reports. Management still wanted some data in real time, so we implemented what was essentially our own early map-reduce–style pipeline. Real-time data was parsed and handled, and any report requiring real-time info hit very small tables that were updated multiple times per second.



Over time, these reports and the web pages hosting them spread across the company, and everyone could see everything. Unsurprisingly, top management didn’t love the idea that the coffee lady could check company earnings. The solution was to integrate all these separate pages into a single application with login, permissions, and proper security.



After integration, we faced an endless stream of requests for additional reports from every corner of the company. In addition to the nightly ETL and report preparation, we also developed new lottery games and integrated our system with external customers. All of this effort just accelerated the proliferation of reports.



Eventually, top management was saturated with dashboards and conflicting KPIs. The business decision was to focus on a single set of KPIs aligned with company goals, instead of ad hoc metrics defined by each department. This effort created a unified web-based Information System with a standardized set of reports.



A few years down the line, when sales started declining, Marketing and Sales began requesting reports that could be summarized as “compare everything to everything else” to try to find some light at the end of the tunnel. The only way to tame the explosion was self-service. We used Microsoft DW technology (SSAS and SSIS). With these tools, the dev team finally got ahead of the requests. The data warehouse was prepared nightly; processing took about six hours, with multiple redundancies and consistency checks.



The downside was that one Excel file became the new information system. Everyone felt in control and could do whatever they wanted. Some entrepreneurial colleagues built their own reports using data from the DW. Suddenly, we were scrambling across the company, trying to keep track of Excel versions.



After Excel’s introduction, we realized no one was logging into the IS anymore.



And hilariously, we found ourselves back where we started: the coffee lady complained about her salary after seeing how much money the company earned (while ignoring expenses). Trusting people not to share an Excel file is not a viable approach, even among top management.



We had to introduce permissions on DW tables to limit who could see what. The situation finally blew up when the CEO sent an Excel file with CEO-level privileges to Payments, and Payments accidentally forwarded the CEO Excel to Sales… and suddenly everyone had CEO-level access.



All this time, our chief IT guy was a Linux proponent, while the company ran Windows clients and a mix of Windows and Linux servers.



The Excel debacle was the final straw that gave the development team enough ammunition to push IT to adopt Active Directory. Introducing AD resolved the chaos around permissions and privileges. Suddenly, there was no need to log in to the IS; anyone could open any approved Excel file, and it worked out of the box.



It was a wild time. We were solving problems on the fly as systems ran and a 7-million-strong audience played games. There was no appetite to stop everything for a few days to roll out a new system; the only way to pause for a few hours was in the face of a significant crisis or breakdown.



Talking with a bunch of friends, it turned out that the observed sequence: manual → live on OLTP → split OLTP/OLAP → hybrid near-real-time → app consolidation → Excel self-service on SSAS → central IAM (AD), was similar to how many companies evolved in 2005–2012.



Today, most of this system could be implemented by one person, and all reporting could be handled with Power BI, Tableau, Qlik, or similar tools.

