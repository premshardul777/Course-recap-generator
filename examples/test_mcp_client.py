"""Real MCP round-trip: spawn mcp/pdf_server.py over stdio and call its tools.
Usage: python examples/test_mcp_client.py <pdf> <outdir> [mermaid_file]"""
import asyncio, json, sys, pathlib
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = pathlib.Path(__file__).resolve().parent.parent

async def main(pdf, outdir, mmd=None):
    params = StdioServerParameters(command=sys.executable, args=[str(ROOT / "mcp" / "pdf_server.py")])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print("TOOLS:", [t.name for t in (await s.list_tools()).tools])
            d = json.loads((await s.call_tool("extract_pdf", {"pdf_path": pdf, "output_dir": outdir})).content[0].text)
            print("extract_pdf ->", {k: d[k] for k in ("file", "pages", "chars", "scanned_warning", "written_to")})
            if mmd:
                print("render_diagram ->", (await s.call_tool("render_diagram", {"mermaid_path": mmd})).content[0].text)

asyncio.run(main(*sys.argv[1:4]))
