#!/usr/bin/env python3
"""
ATOMIC CONCLAVE TEST

Tests Sacred Four deliberation in isolation.
LIVE FIRE: Pure constitutional reasoning test.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.conclave import Conclave
from protoss.structures.pylon import Pylon
from protoss.khala import Khala


async def test_conclave_atomic():
    """Test Sacred Four deliberation directly."""
    print("🔮 ATOMIC CONCLAVE TEST")
    
    # Start infrastructure
    pylon = Pylon(8900)
    await pylon.start()
    
    try:
        conclave = Conclave()
        
        # Set up Khala
        khala = Khala()
        khala.set_grid_port(8900)
        conclave.khala = khala
        
        question = """Should we use JWT tokens or server-side sessions for authentication?"""
        
        print(f"🔮 Sacred Four deliberating: {question}")
        
        # Direct convene call
        guidance = await conclave.convene(question)
        
        print(f"✅ Sacred Four guidance received:")
        print(f"   Length: {len(guidance)} characters")
        print(f"   Content: {guidance}")
        
    except Exception as e:
        print(f"❌ Conclave failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await pylon.stop()


if __name__ == "__main__":
    asyncio.run(test_conclave_atomic())