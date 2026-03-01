#!/usr/bin/env python3
import time, asyncio, aiohttp, statistics

API_BASE = "http://localhost:8400"
CHAT_URL = API_BASE + "/v1/chat/completions"

TESTS = [
    {"name": "短文本", "msg": "写一个 Python 函数计算斐波那契数列", "max_tokens": 128, "repeat": 3},
    {"name": "中等代码", "msg": "写一个二叉搜索算法，带注释", "max_tokens": 512, "repeat": 3},
    {"name": "长上下文", "msg": "解释注意力机制和Transformer架构，各100字", "max_tokens": 1024, "repeat": 2},
]

async def do_test(session, test):
    try:
        start = time.time()
        async with session.post(CHAT_URL, json={"model": "glm-4.7-flash", "messages": [{"role": "user", "content": test["msg"]}], "max_tokens": test["max_tokens"]}, timeout=300) as resp:
            if resp.status != 200:
                return None
            first = time.time()
            data = await resp.json()
            end = time.time()
            usage = data["usage"]
            pt = usage.get("prompt_tokens", 0)
            ct = usage.get("completion_tokens", 0)
            first_time = first - start
            gen_time = end - first
            return {
                "success": True, 
                "total": end-start, 
                "first_time": first_time, 
                "gen_time": gen_time, 
                "pt": pt, 
                "ct": ct, 
                "ps": pt/first_time if first_time > 0 else 0, 
                "gs": ct/gen_time if gen_time > 0 else 0
            }
    except Exception as e:
        return None

async def main():
    async with aiohttp.ClientSession() as session:
        print("=" * 50)
        print("GLM-4.7-Flash 性能测试")
        print("=" * 50)
        
        try:
            async with session.get(API_BASE + "/health", timeout=5) as resp:
                if resp.status == 200:
                    print("API 正常")
                else:
                    print("API 错误")
                    return
        except Exception as e:
            print(f"连接失败: {e}")
            return
        
        all_ps = []
        all_gs = []
        
        for idx, t in enumerate(TESTS, 1):
            print(f"\n[{idx}] {t['name']}")
            results = []
            for j in range(t["repeat"]):
                r = await do_test(session, t)
                if r and r["success"]:
                    results.append(r)
                    all_ps.append(r["ps"])
                    all_gs.append(r["gs"])
                    print(f"  {j+1}/{t['repeat']} OK: {r['ct']}t {r['gs']:.1f}t/s")
                else:
                    print(f"  {j+1}/{t['repeat']} FAIL")
            if results:
                print(f"  平均: {statistics.mean([r['gs'] for r in results]):.1f}t/s")
        
        print("\n" + "=" * 50)
        print("汇总")
        print("=" * 50)
        if all_ps:
            print(f"Prompt 速度: {statistics.mean(all_ps):.1f}t/s")
        if all_gs:
            print(f"生成速度: {statistics.mean(all_gs):.1f}t/s")

asyncio.run(main())
