#!/usr/bin/env python3
"""
SQUAD COORDINATION TEST

Tests Zealot + Stalker squad deployment, quality gates, and coordination.
LIVE FIRE: Real Agent spawning, actual LLM reasoning, squad dynamics.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.structures.gateway import Gateway
from protoss.structures.pylon import Pylon  
from protoss.khala import Khala


async def test_zealot_stalker_squad():
    """Test Zealot execution + Stalker quality review squad."""
    print("⚔️🛡️ TESTING: Zealot + Stalker squad coordination")
    
    pylon = Pylon(8895)
    await pylon.start()
    
    try:
        gateway = Gateway()
        
        # Test task for squad coordination
        task = """
        Build a simple Python function that calculates fibonacci numbers.
        
        Requirements:
        - Function should be efficient
        - Include proper error handling
        - Add basic documentation
        - Write a simple test
        """
        
        print(f"📋 Squad task: {task[:50]}...")
        
        # Deploy Zealot for implementation
        print("⚔️ Spawning Zealot for implementation...")
        zealot = gateway.spawn("zealot")
        
        khala = Khala()
        khala.set_grid_port(8895)
        
        async with khala.connect(zealot.id) as zealot_conn:
            zealot.khala_connection = zealot_conn
            
            try:
                # Zealot executes the task
                zealot_result = await zealot.execute(task)
                print(f"✅ Zealot completed implementation:")
                print(f"   Result length: {len(zealot_result)} characters")
                print(f"   Preview: {zealot_result[:200]}...")
                
                # Now deploy Stalker for quality review
                print("\n🛡️ Spawning Stalker for quality review...")
                stalker = gateway.spawn("stalker")
                
                async with khala.connect(stalker.id) as stalker_conn:
                    stalker.khala_connection = stalker_conn
                    
                    # Stalker reviews Zealot's work
                    review_result = await stalker.review(zealot_result)
                    print(f"✅ Stalker completed review:")
                    print(f"   Review length: {len(review_result)} characters")
                    print(f"   Preview: {review_result[:200]}...")
                    
                    # Check if approved or rejected
                    if "APPROVED" in review_result.upper():
                        print("✅ Stalker APPROVED the implementation")
                    elif "REJECTED" in review_result.upper():
                        print("❌ Stalker REJECTED the implementation")
                    else:
                        print("⚠️  Unclear Stalker decision")
                        
            except Exception as e:
                print(f"❌ Squad coordination failed: {e}")
                import traceback
                traceback.print_exc()
                
    finally:
        await pylon.stop()


async def test_squad_deployment():
    """Test Gateway squad deployment functionality."""
    print("\n🔥 TESTING: Gateway squad deployment")
    
    pylon = Pylon(8896)
    await pylon.start()
    
    try:
        gateway = Gateway()
        
        # Deploy full squad
        squad_task = "Create a simple REST API endpoint for user authentication"
        squad_composition = ["zealot", "zealot", "stalker"]
        
        print(f"🔥 Deploying squad: {squad_composition}")
        print(f"📋 Squad mission: {squad_task}")
        
        try:
            # This will spawn multiple agents on same pathway
            squad_id = await gateway.deploy_squad(squad_task, squad_composition)
            print(f"✅ Squad {squad_id} deployed successfully")
            
            # Give squad time to coordinate
            await asyncio.sleep(5)
            
            # Check squad pathway for coordination messages
            khala = Khala()
            khala.set_grid_port(8896)
            squad_messages = khala.memories.get(squad_id, [])
            
            print(f"✅ Squad generated {len(squad_messages)} coordination messages")
            for msg in squad_messages[-3:]:  # Show last 3 messages
                print(f"   {msg.sender}: {msg.content[:50]}...")
                
        except Exception as e:
            print(f"❌ Squad deployment failed: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        await pylon.stop()


async def test_zealot_uncertainty_escalation():
    """Test Zealot uncertainty detection and escalation."""
    print("\n⚔️🔮 TESTING: Zealot uncertainty escalation")
    
    pylon = Pylon(8897)
    await pylon.start()
    
    try:
        gateway = Gateway()
        zealot = gateway.spawn("zealot")
        
        khala = Khala()
        khala.set_grid_port(8897)
        
        async with khala.connect(zealot.id) as conn:
            zealot.khala_connection = conn
            
            # Task designed to trigger uncertainty
            uncertain_task = """
            Design the optimal database schema for a social media platform
            that needs to scale to 100 million users while maintaining 
            real-time performance and data consistency.
            
            Consider: ACID compliance, horizontal scaling, real-time feeds,
            content moderation, analytics, and privacy regulations.
            """
            
            print("⚔️ Testing uncertainty detection with complex task...")
            
            try:
                result = await zealot.execute(uncertain_task)
                print(f"✅ Zealot execution result:")
                print(f"   Length: {len(result)} characters")
                print(f"   Preview: {result[:200]}...")
                
                # Check if escalation occurred
                if "SACRED FOUR" in result.upper() or "ESCALATION" in result.upper():
                    print("✅ Zealot correctly escalated uncertain task")
                else:
                    print("⚠️  Zealot may not have escalated (or escalation infrastructure down)")
                    
            except Exception as e:
                print(f"❌ Uncertainty escalation test failed: {e}")
                import traceback
                traceback.print_exc()
                
    finally:
        await pylon.stop()


async def main():
    """Run all squad coordination tests."""
    print("⚔️🛡️ SQUAD COORDINATION TEST - LIVE FIRE")
    print("=" * 50)
    
    try:
        await test_zealot_stalker_squad()
        await test_squad_deployment()
        await test_zealot_uncertainty_escalation()
        
        print("\n⚔️🛡️ SQUAD COORDINATION TESTS COMPLETE")
        
    except Exception as e:
        print(f"\n❌ SQUAD COORDINATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())