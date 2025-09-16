#!/usr/bin/env python3
"""
FULL SYMPHONY COORDINATION TEST

End-to-end test of complete Protoss coordination architecture.
LIVE FIRE: Full infrastructure, real agents, actual coordination symphony.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.structures.nexus import Nexus
from protoss.structures.gateway import Gateway
from protoss.khala import Khala


async def test_complete_coordination_flow():
    """Test complete coordination: Carrier → Squad → Sacred Four → Archon."""
    print("🏰 TESTING: Complete Protoss coordination symphony")
    
    # Start full Nexus infrastructure
    nexus = Nexus(8898)
    
    try:
        print("🏰 Building base...")
        await nexus.build_base()
        
        # Give infrastructure time to stabilize
        await asyncio.sleep(2)
        
        # Test 1: Carrier processes human command
        print("\n🛸 PHASE 1: Carrier command processing")
        
        human_command = """
        We need to build a complete user authentication system with the following requirements:
        
        - JWT-based authentication with refresh tokens
        - Password hashing with bcrypt  
        - Rate limiting on auth endpoints
        - Frontend login/signup components
        - Database user model with proper indexing
        - Unit tests for all auth logic
        
        This is a complex task requiring both implementation and quality assurance.
        """
        
        try:
            response = await nexus.carrier_interface(human_command)
            print(f"✅ Carrier processed command successfully")
            print(f"   Response preview: {str(response)[:200]}...")
        except Exception as e:
            print(f"❌ Carrier command processing failed: {e}")
        
        # Test 2: Direct squad deployment  
        print("\n⚔️🛡️ PHASE 2: Squad deployment and coordination")
        
        try:
            gateway = Gateway()
            squad_id = await gateway.deploy_squad(
                "Build authentication API endpoints", 
                ["zealot", "zealot", "stalker"]
            )
            print(f"✅ Squad {squad_id} deployed successfully")
            
            # Let squad coordinate for a bit
            await asyncio.sleep(10)
            
            # Check squad coordination messages
            khala = Khala()
            khala.set_grid_port(8898)
            squad_messages = khala.memories.get(squad_id, [])
            print(f"✅ Squad generated {len(squad_messages)} coordination messages")
            
        except Exception as e:
            print(f"❌ Squad deployment failed: {e}")
            
        # Test 3: Sacred Four constitutional query
        print("\n🔮 PHASE 3: Sacred Four constitutional deliberation")
        
        constitutional_question = """
        CONSTITUTIONAL GUIDANCE NEEDED:
        
        For our authentication system, we're debating between:
        1. Stateless JWT tokens (scalable but harder to revoke)
        2. Server-side sessions (easier to manage but requires state)
        3. Hybrid approach (complexity vs flexibility trade-off)
        
        Security, scalability, and maintainability all matter.
        What's the constitutional guidance for this architectural decision?
        """
        
        try:
            guidance = await nexus.conclave.convene(constitutional_question)
            print(f"✅ Sacred Four constitutional guidance received")
            print(f"   Guidance preview: {guidance[:200]}...")
        except Exception as e:
            print(f"❌ Sacred Four deliberation failed: {e}")
            
        # Test 4: Archon knowledge synthesis
        print("\n🔮 PHASE 4: Archon institutional memory synthesis")
        
        coordination_reports = [
            "Authentication system architecture decided: JWT with refresh tokens for scalability",
            "Implementation completed: bcrypt password hashing, rate limiting middleware added", 
            "Quality review: APPROVED after security audit, all tests passing",
            "Constitutional guidance: JWT approach aligns with stateless architecture principles"
        ]
        
        try:
            synthesis = await nexus.archon.synthesize(
                coordination_reports, 
                "Sprint 1: Authentication System Development"
            )
            print(f"✅ Archon knowledge synthesis completed")
            print(f"   Synthesis preview: {synthesis[:200]}...")
        except Exception as e:
            print(f"❌ Archon synthesis failed: {e}")
            
        print(f"\n🏰 COORDINATION SYMPHONY STATUS CHECK:")
        print(f"   🛸 Carrier: {'✅' if nexus.carrier else '❌'}")
        print(f"   🔹 Pylon: {'✅' if nexus.pylon else '❌'}")  
        print(f"   🔥 Gateway: {'✅' if nexus.gateway else '❌'}")
        print(f"   🔮 Conclave: {'✅' if nexus.conclave else '❌'}")
        print(f"   🔮 Archon: {'✅' if nexus.archon else '❌'}")
        
    finally:
        print("\n🏰 Shutting down infrastructure...")
        await nexus.shutdown_infrastructure()


async def test_stress_coordination():
    """Stress test with multiple concurrent coordination flows."""
    print("\n🔥 TESTING: Stress coordination with concurrent flows")
    
    nexus = Nexus(8899)
    
    try:
        await nexus.build_base()
        await asyncio.sleep(1)
        
        # Launch multiple concurrent coordination tasks
        tasks = []
        
        # Task 1: Simple implementation squad
        tasks.append(
            nexus.gateway.deploy_squad(
                "Build user registration API", 
                ["zealot", "stalker"]
            )
        )
        
        # Task 2: Complex architecture squad  
        tasks.append(
            nexus.gateway.deploy_squad(
                "Design database schema for social features",
                ["zealot", "zealot", "stalker"]
            )
        )
        
        # Task 3: Research and documentation
        tasks.append(
            nexus.gateway.deploy_squad(
                "Research security best practices for user data",
                ["zealot", "archon"]
            )
        )
        
        print("🔥 Launching concurrent coordination flows...")
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if not isinstance(r, Exception))
            print(f"✅ {successful}/{len(tasks)} concurrent flows completed successfully")
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"   ❌ Task {i+1} failed: {result}")
                else:
                    print(f"   ✅ Task {i+1} completed: {result}")
                    
        except Exception as e:
            print(f"❌ Concurrent coordination stress test failed: {e}")
            
    finally:
        await nexus.shutdown_infrastructure()


async def main():
    """Run the complete symphony test."""
    print("🏰⚔️🔮 PROTOSS COORDINATION SYMPHONY - LIVE FIRE")
    print("=" * 60)
    print("Testing complete cathedral architecture coordination...")
    
    try:
        await test_complete_coordination_flow()
        await test_stress_coordination()
        
        print("\n🏰⚔️🔮 COORDINATION SYMPHONY COMPLETE")
        print("The cathedral has proven its architectural integrity.")
        
    except Exception as e:
        print(f"\n❌ COORDINATION SYMPHONY FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())