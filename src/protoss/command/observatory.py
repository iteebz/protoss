"""Inspection utilities for Protoss system."""

import asyncio
import websockets
from ..khala import Psi
from ..constants import PYLON_DEFAULT_PORT


class PylonClient:
    """WebSocket client for connecting to running Pylon instances."""
    
    def __init__(self, host: str = "localhost", port: int = PYLON_DEFAULT_PORT):
        self.uri = f"ws://{host}:{port}/inspector"
        
    async def _request(self, command: str) -> dict:
        """Send inspection command to running Pylon."""
        try:
            async with websockets.connect(self.uri) as websocket:
                # Send inspection request
                request = f"§PSI:inspector:client:inspect:{command}"
                await websocket.send(request)
                
                # Wait for response
                response = await websocket.recv()
                psi = Psi.parse(response)
                
                if psi and psi.type == "result":
                    import json
                    return json.loads(psi.content)
                    
                return {"error": "Invalid response format"}
                
        except ConnectionRefusedError:
            return {"error": "No Pylon grid running. Start with: protoss start"}
        except Exception as e:
            return {"error": f"Connection failed: {e}"}


def _get_pylon_client():
    """Get Pylon client for inspection."""
    return PylonClient()


async def _async_inspect(command: str):
    """Async wrapper for inspection commands."""
    client = _get_pylon_client()
    return await client._request(command)


def observe():
    """Show system status."""
    result = asyncio.run(_async_inspect("status"))
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return
        
    print("⚡ Protoss Grid Status")
    print(f"  Active minds: {result.get('active_agents', 0)}")
    print(f"  Pathways: {result.get('pathways', 0)}")
    print(f"  Total minds: {result.get('total_minds', 0)}")
    print(f"  Total memories: {result.get('total_memories', 0)}")


def show_pathways():
    """Show all Khala pathways."""
    result = asyncio.run(_async_inspect("pathways"))
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return
        
    pathways = result.get("pathways", [])
    print("🧠 Khala Pathways")
    if not pathways:
        print("  No pathways active")
        return

    for pathway in pathways:
        thought = pathway.get("recent_thought", "")
        if thought:
            thought_preview = thought[:50] + "..." if len(thought) > 50 else thought
        else:
            thought_preview = "No recent thoughts"

        print(f"  🧠 {pathway['name']}")
        print(f"    Minds: {pathway['minds']}")
        print(f"    Memories: {pathway['memories']}")
        print(f"    Recent: {thought_preview}")
        print()


def show_minds():
    """Show all connected minds."""
    result = asyncio.run(_async_inspect("minds"))
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return
        
    minds = result.get("minds", [])
    print("🔹 Connected Minds")
    if not minds:
        print("  No minds connected")
        return

    for mind in minds:
        print(f"  🔹 {mind['id']}")
        print(
            f"    Pathways: {', '.join(mind['pathways']) if mind['pathways'] else 'None'}"
        )
        print(f"    Total: {mind['pathway_count']}")
        print()


def show_pathway(name: str):
    """Show pathway details."""
    result = asyncio.run(_async_inspect(f"pathway:{name}"))
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return

    details = result.get("pathway")
    if not details:
        print(f"❌ Pathway '{name}' not found")
        return

    print(f"🧠 Pathway: {details['name']}")
    print(f"  Minds: {', '.join(details['minds']) if details['minds'] else 'None'}")
    print(f"  Memories: {details['memory_count']}")
    print(f"  History limit: {details['history_limit']}")
    print()
    print("💭 Recent memories:")

    if details.get("recent_memories"):
        for msg in details["recent_memories"]:
            print(f"    {msg}")
    else:
        print("    No memories")
