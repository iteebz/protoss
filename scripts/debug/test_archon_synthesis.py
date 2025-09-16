#!/usr/bin/env python3
"""
ARCHON KNOWLEDGE SYNTHESIS TEST

Tests Archon knowledge curation, synthesis, and structural authority.
LIVE FIRE: Real LLM knowledge processing, actual docs/ manipulation.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.structures.gateway import Gateway
from protoss.units.archon import Archon
from pathlib import Path


async def test_archon_knowledge_synthesis():
    """Test Archon synthesizes agent reports into knowledge docs."""
    print("🔮 TESTING: Archon knowledge synthesis from agent reports")
    
    # Create test knowledge directory
    test_knowledge_dir = Path("test_knowledge")
    test_knowledge_dir.mkdir(exist_ok=True)
    
    try:
        gateway = Gateway()
        archon = gateway.spawn("archon")
        
        # Override knowledge directory for testing
        archon.knowledge_dir = test_knowledge_dir
        
        # Mock agent reports from coordination session
        agent_reports = [
            "zealot-abc123: Implemented JWT authentication with bcrypt hashing. Encountered issue with token expiration handling - resolved by adding refresh token mechanism.",
            
            "zealot-def456: Built React frontend components for user dashboard. Used Material-UI for consistency. Performance optimization needed for large data sets - implemented virtualization.",
            
            "stalker-xyz789: Reviewed authentication implementation. APPROVED after requesting fix for hardcoded JWT secret. Security concern: rate limiting missing on auth endpoints - added express-rate-limit middleware.",
            
            "zealot-ghi012: Database migration scripts completed. PostgreSQL setup with connection pooling. Indexing strategy implemented for user queries. Backup automation configured."
        ]
        
        context = "Sprint 1 completion - Authentication system and user interface development"
        
        print("🔮 Archon processing agent reports...")
        
        try:
            synthesis_result = await archon.synthesize(agent_reports, context)
            print(f"✅ Archon synthesis completed:")
            print(f"   Result length: {len(synthesis_result)} characters")
            print(f"   Preview: {synthesis_result[:300]}...")
            
            # Check if knowledge files were created/updated
            knowledge_files = list(test_knowledge_dir.glob("*.md"))
            print(f"✅ Knowledge files created/updated: {len(knowledge_files)}")
            for kf in knowledge_files:
                print(f"   - {kf.name}")
                
        except Exception as e:
            print(f"❌ Archon synthesis failed: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        # Cleanup test directory
        if test_knowledge_dir.exists():
            for file in test_knowledge_dir.glob("*"):
                file.unlink()
            test_knowledge_dir.rmdir()


async def test_archon_knowledge_curation():
    """Test Archon proactive knowledge curation and organization."""
    print("\n🔮 TESTING: Archon knowledge curation and structural optimization")
    
    # Create test knowledge directory with sample docs
    test_knowledge_dir = Path("test_knowledge_curation")
    test_knowledge_dir.mkdir(exist_ok=True)
    
    # Create sample messy knowledge structure
    (test_knowledge_dir / "auth_stuff.md").write_text("""
# Authentication Things

Random notes about JWT tokens and user auth.

## JWT Implementation
Basic JWT setup with Node.js.

## Password Hashing
Using bcrypt for password security.
""")
    
    (test_knowledge_dir / "database_notes.md").write_text("""
# Database Notes

PostgreSQL setup and connection pooling.
Migration scripts and backup strategies.
Query optimization techniques.
""")
    
    (test_knowledge_dir / "frontend_components.md").write_text("""
# React Components

Material-UI usage patterns.
Performance optimization with virtualization.
State management approaches.
""")
    
    try:
        gateway = Gateway()
        archon = gateway.spawn("archon")
        archon.knowledge_dir = test_knowledge_dir
        
        print("🔮 Archon curating knowledge structure...")
        
        try:
            curation_result = await archon.curate_knowledge()
            print(f"✅ Archon curation completed:")
            print(f"   Result length: {len(curation_result)} characters") 
            print(f"   Preview: {curation_result[:300]}...")
            
            # Check for structural improvements
            updated_files = list(test_knowledge_dir.glob("*.md"))
            print(f"✅ Knowledge structure after curation: {len(updated_files)} files")
            
            for file in updated_files:
                print(f"   - {file.name} ({file.stat().st_size} bytes)")
                
        except Exception as e:
            print(f"❌ Archon curation failed: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        # Cleanup test directory
        if test_knowledge_dir.exists():
            for file in test_knowledge_dir.glob("*"):
                file.unlink() 
            test_knowledge_dir.rmdir()


async def test_archon_structural_authority():
    """Test Archon's ability to reorganize and restructure knowledge."""
    print("\n🔮 TESTING: Archon structural authority over knowledge hierarchy")
    
    test_knowledge_dir = Path("test_structural_authority")
    test_knowledge_dir.mkdir(exist_ok=True)
    
    # Create deliberately bad knowledge structure
    (test_knowledge_dir / "everything.md").write_text("""
# Everything About Our System

This file contains everything and is becoming unwieldy.

## Authentication
JWT implementation details...

## Database Design  
PostgreSQL schema information...

## Frontend Components
React component patterns...

## API Endpoints
REST API documentation...

## Deployment
Docker and CI/CD setup...

## Testing
Unit and integration test strategies...

## Security
Security considerations and implementation...

## Performance
Optimization techniques and monitoring...

(This would be a 1000+ line god file in reality)
""")
    
    try:
        gateway = Gateway()
        archon = gateway.spawn("archon")
        archon.knowledge_dir = test_knowledge_dir
        
        print("🔮 Archon applying structural authority to god file...")
        
        try:
            # Curate with focus on structure
            curation_result = await archon.curate_knowledge("structure_optimization")
            print(f"✅ Structural curation completed:")
            print(f"   Result length: {len(curation_result)} characters")
            print(f"   Preview: {curation_result[:300]}...")
            
            # Check if god file was split into logical components
            final_files = list(test_knowledge_dir.glob("*.md"))
            print(f"✅ Files after structural optimization: {len(final_files)}")
            
            for file in final_files:
                content_preview = file.read_text()[:100].replace('\n', ' ')
                print(f"   - {file.name}: {content_preview}...")
                
            if len(final_files) > 1:
                print("✅ Archon successfully split god file into logical components")
            else:
                print("⚠️  Archon may not have split the god file")
                
        except Exception as e:
            print(f"❌ Structural authority test failed: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        # Cleanup
        if test_knowledge_dir.exists():
            for file in test_knowledge_dir.glob("*"):
                file.unlink()
            test_knowledge_dir.rmdir()


async def main():
    """Run all Archon knowledge synthesis tests."""
    print("🔮 ARCHON KNOWLEDGE SYNTHESIS TEST - LIVE FIRE")
    print("=" * 55)
    
    try:
        await test_archon_knowledge_synthesis()
        await test_archon_knowledge_curation()
        await test_archon_structural_authority()
        
        print("\n🔮 ARCHON SYNTHESIS TESTS COMPLETE")
        
    except Exception as e:
        print(f"\n❌ ARCHON SYNTHESIS TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())