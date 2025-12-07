---

layout: post

title: Data handling anti-patterns

subtitle: Data

comments: true

mathjax: true

author: Slobodan Ninkov

---





1\) Synchronous paths



Red flag: UI actions freeze >3s.

Likely cause: Heavy compute in HTTP request/response; unrealistic perf testing on empty data.

Action: Push non-trivial work to queues/streams; small validations only, guarded by strict timeouts + circuit breakers.

KPI: p95/p99 latency per endpoint; queue age; error budget burn.

------------------------------------



2\) Workload isolation



Red flag: User clicks stall ingestion; GUI becomes unresponsive under sensor spikes.

Likely cause: Shared workers/ASGs for frontend and ingestion.

Action: Separate pools, autoscaling, and queues for user traffic vs. device pipelines; isolate head-of-line risk.

KPI: Separate SLOs; saturation per pool; backlog depth.

------------------------------------



3\) Caching for responsiveness



Red flag: Repeated timeouts on read-heavy screens.

Likely cause: Recomputing hot aggregates on every request.

Action: In-memory/distributed cache (Redis/Memcached) with clear TTLs, invalidation, backfill, and stampede protection.

KPI: Cache hit rate; origin QPS; p95 end-to-end.

------------------------------------



4\) Command vs. telemetry vs. data



Red flag: Devices “fixed” only by power-cycling or shelling in.

Likely cause: One channel for everything; no ACK/QoS/retry semantics.

Action: Separate command/control, telemetry, and data channels; device shadow/state sync; explicit reliability.

KPI: Command success rate; time-to-recover; shadow drift rate.

------------------------------------



5\) Data serialization



Red flag: Bandwidth ceilings hit; partial or delayed payloads.

Likely cause: Verbose text formats used on constrained links.

Action: Use compact binary (ProtoBuf/FlatBuffers/CBOR) on device/internal links; reserve JSON for public APIs.

KPI: Bytes/event; CPU/parse cost; link utilization.

------------------------------------



6\) Network stack reuse



Red flag: Random crashes every 1–12 hours; ghost disconnects.

Likely cause: DIY TCP listeners treating streams like a message bus.

Action: Use proven brokers/gateways (MQTT/NATS/Kafka/CoAP servers); extend via plugins/handlers.

KPI: Broker uptime; reconnect rate; duplicate/partial msg rate.

------------------------------------



7\) Operational vs. analytical separation



Red flag: Live app slows or times out during analytics jobs.

Likely cause: One database for OLTP and OLAP.

Action: Keep transactional/time-series stores separate; stream/replicate into OLAP lakes/warehouses.

KPI: OLTP p95 under analytics load; replication lag; query slot utilization.

------------------------------------



8\) Failure capture \& forensics



Red flag: “We don’t know why it failed.”

Likely cause: Invalid/unparseable events dropped on the floor.

Action: DLQs with full payload + error metadata; rate-limit; protect sensitive data; trace IDs end-to-end.

KPI: DLQ volume; mean time to explain (MTTX); % issues closed with root cause.

------------------------------------



9\) Reuse without coupling



Red flag: Endless debates on “the right pattern,” refactors ripple across services.

Likely cause: Over-shared and modified libraries without versioned contracts.

Action: Versioned APIs/schemas; keep services independently deployable; minimize shared runtime code.

KPI: Independent deploy rate; breakage per release; contract test pass rate.





