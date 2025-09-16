#!/usr/bin/env python3
"""
CARRIER → CONCLAVE ESCALATION TEST

Tests Sacred Four constitutional deliberation routing through Carrier.
LIVE FIRE: Real LLM calls, actual constitutional reasoning.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.structures.gateway import Gateway
from protoss.structures.pylon import Pylon
from protoss.units.carrier import Carrier
from protoss.conclave import Conclave
from protoss.khala import Khala


async def test_carrier_constitutional_routing():
    """Test Carrier recognizes constitutional questions and routes to Sacred Four."""
    print("🛸 TESTING: Carrier constitutional question routing")
    
    # Start infrastructure
    pylon = Pylon(8892)
    await pylon.start()
    
    try:
        gateway = Gateway()
        carrier = gateway.spawn("carrier")
        
        # Connect Carrier to Khala
        khala = Khala()
        khala.set_grid_port(8892)
        
        async with khala.connect(carrier.id) as conn:
            carrier.khala_connection = conn
            
            # Test constitutional questions that should route to Sacred Four
            constitutional_questions = [
                "Should we use React or Vue for this project?",
                "What's the best authentication approach?", 
                "How should we structure this codebase?",
                "What testing strategy should we use?"
            ]
            
            for question in constitutional_questions:
                print(f"\n🛸 Testing: '{question}'")
                
                try:
                    response = await carrier.process_command(question)
                    print(f"   Response: {response[:100]}...")
                    
                    # Check if Sacred Four was invoked
                    if "conclave" in response.lower() or "sacred four" in response.lower():
                        print("   ✅ Correctly identified as constitutional question")
                    else:
                        print("   ⚠️  May not have been routed to Sacred Four")
                        
                except Exception as e:
                    print(f"   ❌ Carrier failed: {e}")
                    
                await asyncio.sleep(1)  # Rate limiting
                
    finally:
        await pylon.stop()


async def test_conclave_deliberation():
    """Test Sacred Four deliberation process directly."""
    print("\n🔮 TESTING: Sacred Four deliberation")
    
    pylon = Pylon(8893)
    await pylon.start()
    
    try:
        conclave = Conclave()
        
        # Set Khala grid port for Conclave
        khala = Khala()
        khala.set_grid_port(8893)
        conclave.khala = khala
        
        constitutional_question = """
        CONSTITUTIONAL DELIBERATION REQUEST:
        
        We need to decide on the authentication strategy for our application.
        Options: JWT tokens vs server-side sessions vs OAuth2.
        
        Security, scalability, and development velocity all matter.
        What's the constitutional guidance?
        """
        
        print(f"🔮 Convening Sacred Four for: {constitutional_question[:50]}...")
        
        try:
            guidance = await conclave.convene(constitutional_question)
            print(f"✅ Sacred Four guidance received:")
            print(f"   {guidance[:200]}...")
            
            # Check if all four perspectives were represented
            perspectives = ["tassadar", "zeratul", "artanis", "fenix"]
            represented = sum(1 for p in perspectives if p in guidance.lower())
            print(f"✅ {represented}/4 Sacred Four perspectives detected")
            
        except Exception as e:
            print(f"❌ Sacred Four deliberation failed: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        await pylon.stop()


async def test_carrier_sacred_four_integration():
    """Test complete Carrier → Sacred Four → response flow.""" 
    print("\n🛸🔮 TESTING: Full Carrier → Sacred Four integration")
    
    pylon = Pylon(8894)
    await pylon.start()
    
    try:
        gateway = Gateway()
        carrier = gateway.spawn("carrier")
        
        khala = Khala()
        khala.set_grid_port(8894)
        
        async with khala.connect(carrier.id) as conn:
            carrier.khala_connection = conn
            
            # Test question that should trigger full Sacred Four flow
            complex_question = """
            We're building a new microservice and need architectural guidance:
            
            - Should we use GraphQL or REST API?
            - What database technology fits best?
            - How should we handle authentication?
            - What testing approach should we take?
            
            This affects our entire system architecture going forward.
            """
            
            print(f"🛸 Processing complex architectural question...")
            
            try:
                response = await carrier.process_command(complex_question)
                
                print(f"✅ Carrier response received:")
                print(f"   Length: {len(response)} characters")
                print(f"   Preview: {response[:300]}...")
                
                # Analyze response for Sacred Four involvement
                sacred_indicators = [
                    "sacred four", "conclave", "constitutional", "deliberation",
                    "tassadar", "zeratul", "artanis", "fenix"
                ]
                
                found_indicators = [ind for ind in sacred_indicators if ind in response.lower()]
                if found_indicators:
                    print(f"✅ Sacred Four indicators found: {found_indicators}")
                else:
                    print("⚠️  No clear Sacred Four indicators in response")
                    
            except Exception as e:
                print(f"❌ Integration test failed: {e}")
                import traceback
                traceback.print_exc()
                
    finally:
        await pylon.stop()


async def main():
    """Run all Carrier → Conclave tests."""
    print("🛸🔮 CARRIER → SACRED FOUR ESCALATION TEST - LIVE FIRE")
    print("=" * 60)
    
    try:
        await test_carrier_constitutional_routing()
        await test_conclave_deliberation()  
        await test_carrier_sacred_four_integration()
        
        print("\n🛸🔮 CARRIER → SACRED FOUR TESTS COMPLETE")
        
    except Exception as e:
        print(f"\n❌ CARRIER → SACRED FOUR TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())