#!/usr/bin/env python3
"""Test Archon knowledge evolution patterns."""

import asyncio
import tempfile
from pathlib import Path

import pytest
from protoss.units import Archon
from protoss.structures.pylon import Psi


@pytest.mark.asyncio
async def test_knowledge_evolution():
    """Test how Archon accumulates and organizes knowledge."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        protoss_dir = Path(tmp_dir) / ".protoss"
        archon = Archon(protoss_dir)
        
        print("🧬 Testing knowledge evolution...")
        
        # Simulate multi-session learning
        sessions = [
            # Session 1: Basic coordination failures
            [
                Psi(target="archon", source="zealot_1", type="error", content="Failed to coordinate attack - units scattered"),
                Psi(target="archon", source="zealot_2", type="error", content="Coordination breakdown during retreat"),
            ],
            # Session 2: Strategy insights  
            [
                Psi(target="archon", source="zealot_3", type="insight", content="Strategy works: scout before engage"),
                Psi(target="archon", source="zealot_1", type="pattern", content="Group movement reduces casualties"),
            ],
            # Session 3: Mixed coordination events
            [
                Psi(target="archon", source="zealot_2", type="success", content="Coordination successful - flanking maneuver completed"),
                Psi(target="archon", source="zealot_4", type="error", content="Communication failed during multi-unit coordination"),
            ]
        ]
        
        # Process each session
        for session_num, messages in enumerate(sessions, 1):
            print(f"\n📊 Processing session {session_num}...")
            for msg in messages:
                await archon.process_psi_message(msg)
            
            # Check knowledge accumulation
            coord_wisdom = await archon.query_knowledge("coordination")
            debug_wisdom = await archon.query_knowledge("debugging") 
            strategy_wisdom = await archon.query_knowledge("strategy")
            
            print(f"  Coordination: {len(coord_wisdom)} chars")
            print(f"  Debugging: {len(debug_wisdom)} chars") 
            print(f"  Strategy: {len(strategy_wisdom)} chars")
        
        # Verify knowledge files exist and contain expected content
        knowledge_files = list((protoss_dir / "knowledge").glob("*.md"))
        print(f"\n📁 Knowledge files created: {len(knowledge_files)}")
        
        for file in knowledge_files:
            with open(file, 'r') as f:
                content = f.read()
                lines = content.count('\n')
                print(f"  {file.name}: {lines} lines")
        
        # Test emergent domain organization
        domains_found = set()
        for file in knowledge_files:
            domain = file.stem
            domains_found.add(domain)
        
        print(f"\n🏗️ Emergent domains: {sorted(domains_found)}")
        
        # Verify domains match message types (no predefined categories)
        expected_domains = {"error", "insight", "pattern", "success"}
        assert domains_found == expected_domains, f"Expected {expected_domains}, got {domains_found}"
        
        print("✅ Knowledge evolution patterns verified")
        return True


if __name__ == "__main__":
    asyncio.run(test_knowledge_evolution())