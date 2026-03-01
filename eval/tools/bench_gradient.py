#!/usr/bin/env python3
import time, asyncio, aiohttp, statistics

API_BASE = "http://localhost:8400"
CHAT_URL = API_BASE + "/v1/chat/completions"

# 更保守的梯度测试
TESTS = [
    {"name": "256 tokens", "tokens": 256, "repeat": 3},
    {"name": "512 tokens", "tokens": 512, "repeat": 3},
    {"name": "1024 tokens", "tokens": 1024, "repeat": 3},
    {"name": "2048 tokens", "tokens": 2048, "repeat": 2},
    {"name": "4096 tokens", "tokens": 4096, "repeat": 2},
]

async def do_test(session, tokens, repeat):
    msg = "写一段关于机器学习的简介"
    try:
        start = time.time()
        async with session.post(CHAT_URL, json={"model": "glm-4.7-flash", "messages": [{"role": "user", "content": msg}], "max_tokens": tokens}, timeout=120) as resp:
            if resp.status != 200:
                print(f"    错误: HTTP {resp.status}")
                return None
            first = time.time()
            data = await resp.json()
            end = time.time()
            usage = data["usage"]
            pt = usage.get("prompt_tokens", 0)
            ct = usage.get("completion_tokens", 0)
            return {
                "success": True, 
                "total": end-start, 
                "first_time": first-start, 
                "gen_time": end-first, 
                "pt": pt, 
                "ct": ct, 
                "gs": ct/(end-first) if end-first>0 else 0
            }
    except asyncio.TimeoutError:
        print("    超时")
        return None
    except Exception as e:
        print(f"    错误: {e}")
        return None

async def main():
    async with aiohttp.ClientSession() as session:
        print("=" * 60)
        print("GLM-4.7-Flash 梯度性能测试")
        print("=" * 60)
        
        # 检查 API
        try:
            async with session.get(API_BASE + "/health", timeout=5) as resp:
                if resp.status == 200:
                    print("API 正常")
                else:
                    print(f"API 错误: {resp.status}")
                    return
        except Exception as e:
            print(f"连接失败: {e}")
            return
        
        # 运行梯度测试
        results = []
        for test in TESTS:
            print(f"\n[{test['name']}] {test['tokens']} tokens × {test['repeat']} 次")
            all_gs = []
            for i in range(test["repeat"]):
                r = await do_test(session, test["tokens"], test["repeat"])
                if r and r["success"]:
                    all_gs.append(r["gs"])
                    print(f"  [{i+1}] OK: {r['ct']}t {r['gs']:.1f}t/s 总:{r['total']:.1f}s", end="", flush=True)
                else:
                    print(f"  [{i+1}] FAIL")
            
            if all_gs:
                avg = statistics.mean(all_gs)
                print(f"  平均: {avg:.1f} t/s")
                results.append({"name": test['name'], "tokens": test['tokens'], "avg": avg})
        
        print("\n" + "=" * 60)
        print("梯度测试汇总")
        print("=" * 60)
        print(f"{'生成长度':>12} {'重复':>8} {'平均速度(t/s)':>18}")
        print("-" * 60)
        for r in results:
            print(f"{r['name']:12} {r['tokens']:8} {len(all_gs):4}    {r['avg']:18.1f}")
        print("-" * 60)

asyncio.run(main())
