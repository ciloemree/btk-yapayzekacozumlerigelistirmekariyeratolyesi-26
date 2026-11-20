"""MCP Client: stdio üzerinden araçları keşfet ve çağır."""
import asyncio
import json
import os
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).with_name("d7_04_mcp_server.py")

async def mcp_call(tool_name: str, arguments: dict):
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)], env=os.environ.copy())
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            if result.isError:
                raise RuntimeError(f"MCP araç hatası: {result.content}")
            texts = [c.text for c in result.content if getattr(c, "type", "") == "text"]
            if not texts:
                raise RuntimeError("MCP sunucusundan metin sonucu gelmedi")
            return json.loads(texts[0])

async def list_mcp_tools():
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)], env=os.environ.copy())
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.list_tools()
            return [(tool.name, tool.description) for tool in result.tools]

if __name__ == "__main__":
    print("SUNULAN ARAÇLAR:", asyncio.run(list_mcp_tools()))
    print("BELGE ARAMA:", asyncio.run(mcp_call("dokuman_ara", {"soru": "Kayıp eşya nereye teslim edilir?", "k": 3})))
