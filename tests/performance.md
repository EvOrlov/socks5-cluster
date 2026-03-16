# Performance Test

## Summary:

The SOCKS5 cluster successfully handled up to 500 concurrent
users with a 100% success rate and peak throughput of ~125 requests/sec.

## Test environment

Server:
- 2 vCPU
- 2 GB RAM VPS
- Ubuntu 22.04

Cluster:
- 3000 SOCKS5 proxies
- Docker containers

Load generator:
- Python asyncio
- aiohttp + SOCKS connector
- Executed from a separate VPS (different network)

## Test scenario

Each virtual user:

1. Selects a random proxy
2. Requests a random website
3. Downloads HTML response
4. Measures latency

Test websites:

- https://httpbin.org/html
- https://example.com
- https://reqbin.com
- http://automationpractice.com
- https://demo.applitools.com

## Results

| Users | Requests | Success | Avg latency | RPS |
|------|------|------|------|------|
| 20 | 100 | 100% | 0.51s | 24 |
| 50 | 250 | 100% | 0.59s | 42 |
| 100 | 500 | 100% | 0.81s | 84 |
| 200 | 1000 | 100% | 1.31s | 109 |
| 500 | 2500 | 100% | 2.80s | 125 |


## Complete test log

Example output from a real test run:

```text
========================================
SOCKS5 CLUSTER LOAD TEST
========================================

Proxies loaded : 3000
Test sites     : 5
Requests/user  : 5

===================================
Running test with 20 users
===================================
Progress: 50 requests | Success: 50 | Errors: 0
Progress: 100 requests | Success: 100 | Errors: 0

==============================
Users: 20
==============================
Requests        : 100
Success         : 100
Errors          : 0
Success rate    : 100.00%

Latency:
Avg             : 0.51s
P50             : 0.41s
P95             : 1.04s
P99             : 1.72s

Throughput:
Requests/sec    : 24.01

Proxy usage:
Unique proxies  : 95

Cooling down for 60 seconds...


===================================
Running test with 50 users
===================================
Progress: 50 requests | Success: 50 | Errors: 0
Progress: 100 requests | Success: 100 | Errors: 0
Progress: 150 requests | Success: 150 | Errors: 0
Progress: 200 requests | Success: 200 | Errors: 0
Progress: 250 requests | Success: 250 | Errors: 0

==============================
Users: 50
==============================
Requests        : 250
Success         : 250
Errors          : 0
Success rate    : 100.00%

Latency:
Avg             : 0.59s
P50             : 0.48s
P95             : 1.26s
P99             : 1.60s

Throughput:
Requests/sec    : 42.74

Proxy usage:
Unique proxies  : 240

Cooling down for 60 seconds...


===================================
Running test with 100 users
===================================
Progress: 50 requests | Success: 50 | Errors: 0
Progress: 100 requests | Success: 100 | Errors: 0
Progress: 150 requests | Success: 150 | Errors: 0
Progress: 200 requests | Success: 200 | Errors: 0
Progress: 250 requests | Success: 250 | Errors: 0
Progress: 300 requests | Success: 300 | Errors: 0
Progress: 350 requests | Success: 350 | Errors: 0
Progress: 400 requests | Success: 400 | Errors: 0
Progress: 450 requests | Success: 450 | Errors: 0
Progress: 500 requests | Success: 500 | Errors: 0

==============================
Users: 100
==============================
Requests        : 500
Success         : 500
Errors          : 0
Success rate    : 100.00%

Latency:
Avg             : 0.81s
P50             : 0.72s
P95             : 1.41s
P99             : 2.04s

Throughput:
Requests/sec    : 84.54

Proxy usage:
Unique proxies  : 460

Cooling down for 60 seconds...


===================================
Running test with 200 users
===================================
Progress: 50 requests | Success: 50 | Errors: 0
Progress: 100 requests | Success: 100 | Errors: 0
Progress: 150 requests | Success: 150 | Errors: 0
Progress: 200 requests | Success: 200 | Errors: 0
Progress: 250 requests | Success: 250 | Errors: 0
Progress: 300 requests | Success: 300 | Errors: 0
Progress: 350 requests | Success: 350 | Errors: 0
Progress: 400 requests | Success: 400 | Errors: 0
Progress: 450 requests | Success: 450 | Errors: 0
Progress: 500 requests | Success: 500 | Errors: 0
Progress: 550 requests | Success: 550 | Errors: 0
Progress: 600 requests | Success: 600 | Errors: 0
Progress: 650 requests | Success: 650 | Errors: 0
Progress: 700 requests | Success: 700 | Errors: 0
Progress: 750 requests | Success: 750 | Errors: 0
Progress: 800 requests | Success: 800 | Errors: 0
Progress: 850 requests | Success: 850 | Errors: 0
Progress: 900 requests | Success: 900 | Errors: 0
Progress: 950 requests | Success: 950 | Errors: 0
Progress: 1000 requests | Success: 1000 | Errors: 0

==============================
Users: 200
==============================
Requests        : 1000
Success         : 1000
Errors          : 0
Success rate    : 100.00%

Latency:
Avg             : 1.31s
P50             : 1.23s
P95             : 2.11s
P99             : 2.56s

Throughput:
Requests/sec    : 109.11

Proxy usage:
Unique proxies  : 837

Cooling down for 60 seconds...


===================================
Running test with 500 users
===================================
Progress: 50 requests | Success: 50 | Errors: 0
Progress: 100 requests | Success: 100 | Errors: 0
Progress: 150 requests | Success: 150 | Errors: 0
Progress: 200 requests | Success: 200 | Errors: 0
Progress: 250 requests | Success: 250 | Errors: 0
Progress: 300 requests | Success: 300 | Errors: 0
Progress: 350 requests | Success: 350 | Errors: 0
Progress: 400 requests | Success: 400 | Errors: 0
Progress: 450 requests | Success: 450 | Errors: 0
Progress: 500 requests | Success: 500 | Errors: 0
Progress: 550 requests | Success: 550 | Errors: 0
Progress: 600 requests | Success: 600 | Errors: 0
Progress: 650 requests | Success: 650 | Errors: 0
Progress: 700 requests | Success: 700 | Errors: 0
Progress: 750 requests | Success: 750 | Errors: 0
Progress: 800 requests | Success: 800 | Errors: 0
Progress: 850 requests | Success: 850 | Errors: 0
Progress: 900 requests | Success: 900 | Errors: 0
Progress: 950 requests | Success: 950 | Errors: 0
Progress: 1000 requests | Success: 1000 | Errors: 0
Progress: 1050 requests | Success: 1050 | Errors: 0
Progress: 1100 requests | Success: 1100 | Errors: 0
Progress: 1150 requests | Success: 1150 | Errors: 0
Progress: 1200 requests | Success: 1200 | Errors: 0
Progress: 1250 requests | Success: 1250 | Errors: 0
Progress: 1300 requests | Success: 1300 | Errors: 0
Progress: 1350 requests | Success: 1350 | Errors: 0
Progress: 1400 requests | Success: 1400 | Errors: 0
Progress: 1450 requests | Success: 1450 | Errors: 0
Progress: 1500 requests | Success: 1500 | Errors: 0
Progress: 1550 requests | Success: 1550 | Errors: 0
Progress: 1600 requests | Success: 1600 | Errors: 0
Progress: 1650 requests | Success: 1650 | Errors: 0
Progress: 1700 requests | Success: 1700 | Errors: 0
Progress: 1750 requests | Success: 1750 | Errors: 0
Progress: 1800 requests | Success: 1800 | Errors: 0
Progress: 1850 requests | Success: 1850 | Errors: 0
Progress: 1900 requests | Success: 1900 | Errors: 0
Progress: 1950 requests | Success: 1950 | Errors: 0
Progress: 2000 requests | Success: 2000 | Errors: 0
Progress: 2050 requests | Success: 2050 | Errors: 0
Progress: 2100 requests | Success: 2100 | Errors: 0
Progress: 2150 requests | Success: 2150 | Errors: 0
Progress: 2200 requests | Success: 2200 | Errors: 0
Progress: 2250 requests | Success: 2250 | Errors: 0
Progress: 2300 requests | Success: 2300 | Errors: 0
Progress: 2350 requests | Success: 2350 | Errors: 0
Progress: 2400 requests | Success: 2400 | Errors: 0
Progress: 2450 requests | Success: 2450 | Errors: 0
Progress: 2500 requests | Success: 2500 | Errors: 0

==============================
Users: 500
==============================
Requests        : 2500
Success         : 2500
Errors          : 0
Success rate    : 100.00%

Latency:
Avg             : 2.80s
P50             : 2.58s
P95             : 4.96s
P99             : 5.47s

Throughput:
Requests/sec    : 125.30

Proxy usage:
Unique proxies  : 1690

Cooling down for 60 seconds...


===================================
FINAL SUMMARY
===================================

Users=20 | Requests=100 | Success=100.00% | Latency=0.51s | RPS=24.01
Users=50 | Requests=250 | Success=100.00% | Latency=0.59s | RPS=42.74
Users=100 | Requests=500 | Success=100.00% | Latency=0.81s | RPS=84.54
Users=200 | Requests=1000 | Success=100.00% | Latency=1.31s | RPS=109.11
Users=500 | Requests=2500 | Success=100.00% | Latency=2.80s | RPS=125.30

```