#!/usr/bin/env python3
"""
ATOMIC STALKER TEST

Tests Stalker unit spawning and quality review.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.structures.gateway import Gateway


async def test_stalker_spawning():
    """Test Stalker unit spawning and review method."""
    print("🛡️ ATOMIC STALKER TEST")
    
    gateway = Gateway()
    
    # Spawn stalker
    stalker = gateway.spawn("stalker")
    print(f"🛡️ Spawned: {type(stalker).__name__} with ID {stalker.id}")
    
    # Verify it has review method
    if hasattr(stalker, 'review'):
        print("✅ Stalker has review method")
        
        # Test review with mock work report
        work_report = "Implemented simple authentication function with proper error handling"
        try:
            review_result = await stalker.review(work_report)
            print(f"✅ Stalker review completed:")
            print(f"   Length: {len(review_result)} characters")
            print(f"   Preview: {review_result[:100]}...")
            
            if "APPROVED" in review_result.upper():
                print("✅ Stalker APPROVED the work")
            elif "REJECTED" in review_result.upper():
                print("❌ Stalker REJECTED the work")
            else:
                print("⚠️  Unclear Stalker decision")
                
        except Exception as e:
            print(f"❌ Stalker review failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Stalker missing review method")


if __name__ == "__main__":
    asyncio.run(test_stalker_spawning())