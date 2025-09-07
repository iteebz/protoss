#!/usr/bin/env python3
"""Test Archon institutional memory."""

import asyncio
import tempfile
from pathlib import Path

import pytest
from protoss.units import Archon
from protoss.structures.pylon import Psi


@pytest.mark.asyncio
async def test_archon():
    """Test basic Archon functionality."""
    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as tmp_dir:
        protoss_dir = Path(tmp_dir) / ".protoss"
        archon = Archon(protoss_dir)
        
        print("🧠 Testing Archon...")
        
        # Test task logging
        await archon.log_task("zealot_1", "scout_base", "enemy_found", True)
        await archon.log_task("zealot_2", "attack_base", "mission_failed", False)
        print("✅ Task logging")
        
        # Test pattern learning
        await archon.learn_pattern("coordination", "Zealots should group before attacking")
        await archon.learn_pattern("strategy", "Scout before engaging enemy forces")
        print("✅ Pattern learning")
        
        # Test knowledge query
        coord_wisdom = await archon.query_knowledge("coordination")
        strat_wisdom = await archon.query_knowledge("strategy")
        print(f"✅ Knowledge query: {len(coord_wisdom)} chars coordination wisdom")
        print(f"✅ Knowledge query: {len(strat_wisdom)} chars strategy wisdom")
        
        # Test PSI message processing
        error_msg = Psi(target="archon", source="zealot_1", type="report", content="Coordination failed - units scattered")
        success_msg = Psi(target="archon", source="zealot_2", type="report", content="Attack completed successfully")
        
        await archon.process_psi_message(error_msg)
        await archon.process_psi_message(success_msg)
        print("✅ PSI message processing")
        
        # Check file structure
        assert (protoss_dir / "protoss.db").exists(), "Database not created"
        assert (protoss_dir / "knowledge").exists(), "Knowledge directory not created"
        assert (protoss_dir / "knowledge" / "coordination.md").exists(), "Coordination wisdom not saved"
        assert (protoss_dir / "knowledge" / "strategy.md").exists(), "Strategy wisdom not saved"
        print("✅ File structure verification")
        
        print("\n🎯 Archon implementation complete")
        return True


if __name__ == "__main__":
    asyncio.run(test_archon())