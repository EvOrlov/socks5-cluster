import asyncio
import random
import time
import aiohttp
import statistics
from aiohttp_socks import ProxyConnector


TEST_SITES = [
    "https://httpbin.org/html",
    "https://example.com",
    "https://reqbin.com/",
    "http://automationpractice.com/",
    "https://demo.applitools.com/"
]


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1)"
}


async def fetch(session, url):

    start = time.perf_counter()

    try:

        async with session.get(url, timeout=20) as resp:

            resp_text = await resp.text()

            latency = time.perf_counter() - start

            resp_lower = resp_text[:200].lower()

            if "<html" in resp_lower or "<!doctype" in resp_lower:
                return True, latency
            else:
                print(f"Bad response: {resp_lower[:120]}")
                return False, latency

    except Exception as e:

        latency = time.perf_counter() - start
        print(f"Exception: {e}")

        return False, latency


async def user_worker(proxies, stats, lock):

    sites = TEST_SITES[:]
    random.shuffle(sites)

    for site in sites:

        proxy = random.choice(proxies)

        ip, port, user, password = proxy.split(":")

        proxy_url = f"socks5://{user}:{password}@{ip}:{port}"

        connector = ProxyConnector.from_url(proxy_url)

        async with aiohttp.ClientSession(
            connector=connector,
            headers=HEADERS
        ) as session:

            ok, latency = await fetch(session, site)

        async with lock:

            stats["total"] += 1
            stats["latencies"].append(latency)
            stats["used_proxies"].add(proxy)

            if ok:
                stats["success"] += 1
            else:
                stats["errors"] += 1

            if stats["total"] % 50 == 0:

                print(
                    f"Progress: {stats['total']} requests | "
                    f"Success: {stats['success']} | "
                    f"Errors: {stats['errors']}"
                )

        await asyncio.sleep(random.uniform(0.05, 0.15))


def latency_stats(latencies):

    latencies_sorted = sorted(latencies)

    p50 = latencies_sorted[int(len(latencies_sorted) * 0.50)]
    p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)]
    p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)]

    return p50, p95, p99


async def run_test(proxies, users):

    stats = {
        "total": 0,
        "success": 0,
        "errors": 0,
        "latencies": [],
        "used_proxies": set()
    }

    lock = asyncio.Lock()

    print("\n===================================")
    print(f"Running test with {users} users")
    print("===================================")

    start = time.time()

    tasks = [
        user_worker(proxies, stats, lock)
        for _ in range(users)
    ]

    await asyncio.gather(*tasks)

    duration = time.time() - start

    avg_latency = statistics.mean(stats["latencies"])

    p50, p95, p99 = latency_stats(stats["latencies"])

    print("\n==============================")
    print(f"Users: {users}")
    print("==============================")

    print(f"Requests        : {stats['total']}")
    print(f"Success         : {stats['success']}")
    print(f"Errors          : {stats['errors']}")

    print(f"Success rate    : {stats['success'] / stats['total'] * 100:.2f}%")

    print(f"\nLatency:")
    print(f"Avg             : {avg_latency:.2f}s")
    print(f"P50             : {p50:.2f}s")
    print(f"P95             : {p95:.2f}s")
    print(f"P99             : {p99:.2f}s")

    print(f"\nThroughput:")
    print(f"Requests/sec    : {stats['total'] / duration:.2f}")

    print(f"\nProxy usage:")
    print(f"Unique proxies  : {len(stats['used_proxies'])}")

    return {
        "users": users,
        "requests": stats["total"],
        "success_rate": stats["success"] / stats["total"],
        "avg_latency": avg_latency,
        "rps": stats["total"] / duration
    }


async def main(proxies, user_levels):

    print("\n========================================")
    print("SOCKS5 CLUSTER LOAD TEST")
    print("========================================\n")

    print(f"Proxies loaded : {len(proxies)}")
    print(f"Test sites     : {len(TEST_SITES)}")
    print(f"Requests/user  : {len(TEST_SITES)}")

    results = []

    for users in user_levels:

        result = await run_test(proxies, users)

        results.append(result)

        print("\nCooling down for 60 seconds...\n")
        await asyncio.sleep(60)

    print("\n===================================")
    print("FINAL SUMMARY")
    print("===================================\n")

    for r in results:

        print(
            f"Users={r['users']} | "
            f"Requests={r['requests']} | "
            f"Success={r['success_rate']*100:.2f}% | "
            f"Latency={r['avg_latency']:.2f}s | "
            f"RPS={r['rps']:.2f}"
        )


if __name__ == "__main__":

    with open("../all_proxies_ip_port.txt") as f:
        proxies = [line.strip() for line in f]

    user_levels = [20, 50, 100, 200, 500]

    asyncio.run(main(proxies, user_levels))