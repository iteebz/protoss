#!/usr/bin/env python3
"""STRESS TEST: Break Archon or prove it works."""

import asyncio
import tempfile
import sqlite3
from pathlib import Path

from protoss.units import Archon
from protoss.structures.pylon import Psi


async def stress_test_archon():
    """Brutal stress testing of Archon implementation."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        protoss_dir = Path(tmp_dir) / ".protoss"
        archon = Archon(protoss_dir)
        
        print("🔥 STRESS TESTING ARCHON...")
        
        # Test 1: Concurrent task logging 
        print("\n💥 Test 1: Concurrent task logging")
        tasks = []
        for i in range(100):
            tasks.append(archon.log_task(f"zealot_{i}", f"task_{i}", f"result_{i}", i % 2 == 0))
        
        await asyncio.gather(*tasks)
        
        # Verify database integrity
        with sqlite3.connect(archon.db_path) as db:
            count = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            assert count == 100, f"Expected 100 tasks, got {count}"
        print(f"✅ Logged {count} tasks concurrently")
        
        # Test 2: Edge case messages
        print("\n💥 Test 2: Edge case PSI messages")
        edge_cases = [
            Psi(target="archon", source="", type="empty", content=""),
            Psi(target="archon", source="test", type="unicode", content="🤖 Unicode test with émojis"),
            Psi(target="archon", source="test", type="massive", content="x" * 10000),
            Psi(target="archon", source="test", type="sql", content="'; DROP TABLE tasks; --"),
            Psi(target="archon", source="test", type="newlines", content="line1\nline2\nline3"),
            Psi(target="archon", source="test", type="markdown", content="# Header\n**bold** *italic*"),
        ]
        
        for msg in edge_cases:
            try:
                await archon.process_psi_message(msg)
                print(f"✅ Handled {msg.type} message")
            except Exception as e:
                print(f"❌ Failed on {msg.type}: {e}")
                raise
        
        # Test 3: Message type as domain
        print("\n💥 Test 3: Message type domain mapping")
        test_messages = [
            ("error", "some error content"),
            ("report", "status report content"), 
            ("insight", "learned something new"),
            ("debug", "debugging information"),
        ]
        
        for msg_type, content in test_messages:
            msg = Psi(target="archon", source="test", type=msg_type, content=content)
            await archon.process_psi_message(msg)
            
            # Check that domain file exists
            domain_file = archon.knowledge_dir / f"{msg_type}.md"
            assert domain_file.exists(), f"Domain {msg_type} not created"
            print(f"✅ Domain created for type: {msg_type}")
        
        # Test 4: File system stress
        print("\n💥 Test 4: File system operations")
        
        # Rapid pattern learning on same domain
        for i in range(50):
            await archon.learn_pattern("stress_test", f"Insight #{i}")
        
        # Check file integrity
        stress_file = archon.knowledge_dir / "stress_test.md"
        with open(stress_file, 'r') as f:
            content = f.read()
            insight_count = content.count("Insight #")
            assert insight_count == 50, f"Expected 50 insights, found {insight_count}"
        print(f"✅ Wrote 50 rapid insights to same domain")
        
        # Test 5: Query robustness
        print("\n💥 Test 5: Query edge cases")
        
        # Query non-existent domain
        empty_result = await archon.query_knowledge("nonexistent")
        assert "No wisdom recorded" in empty_result
        print("✅ Handles non-existent domain queries")
        
        # Query after file manipulation
        await archon.learn_pattern("test_domain", "Original content")
        original = await archon.query_knowledge("test_domain")
        
        # Manually corrupt file (simulate filesystem issues)
        test_file = archon.knowledge_dir / "test_domain.md"
        with open(test_file, 'w') as f:
            f.write("Manually corrupted content")
        
        corrupted = await archon.query_knowledge("test_domain")
        assert "Manually corrupted" in corrupted
        print("✅ Handles file system changes")
        
        # Test 6: Database integrity under stress
        print("\n💥 Test 6: Database integrity checks")
        
        # Log SQL injection attempt
        await archon.log_task("test", "injection_test", "'; DROP TABLE tasks; --", False)
        
        # Verify all logged tasks are intact
        with sqlite3.connect(archon.db_path) as db:
            # Check for SQL injection attempts
            injection_count = db.execute(
                "SELECT COUNT(*) FROM tasks WHERE result LIKE '%DROP TABLE%'"
            ).fetchone()[0]
            assert injection_count == 1, "SQL injection protection failed"
            
            # Verify data types
            sample = db.execute("SELECT * FROM tasks LIMIT 1").fetchone()
            assert len(sample) == 6, f"Expected 6 columns, got {len(sample)}"
            assert isinstance(sample[4], int), f"Success should be boolean/int, got {type(sample[4])}"
            assert isinstance(sample[5], float), f"Timestamp should be float, got {type(sample[5])}"
        
        print("✅ Database integrity maintained")
        
        # Test 7: Knowledge file count and structure
        print("\n💥 Test 7: File structure verification")
        
        knowledge_files = list(archon.knowledge_dir.glob("*.md"))
        print(f"📁 Total knowledge files: {len(knowledge_files)}")
        
        for file in knowledge_files:
            with open(file, 'r') as f:
                content = f.read()
                # Skip validation for manually corrupted test file
                if file.name == "test_domain.md":
                    continue
                # Every knowledge file should have header and content
                assert content.startswith("#"), f"File {file.name} missing header"
                assert len(content.strip()) > 0, f"File {file.name} is empty"
        
        print(f"✅ All {len(knowledge_files)} knowledge files properly formatted")
        
        # Final verification
        print(f"\n🎯 STRESS TEST COMPLETE")
        print(f"   Tasks logged: {count}")
        print(f"   Knowledge domains: {len(knowledge_files)}")
        print(f"   Database size: {archon.db_path.stat().st_size} bytes")
        print(f"   Knowledge dir size: {sum(f.stat().st_size for f in knowledge_files)} bytes")
        
        return True


if __name__ == "__main__":
    asyncio.run(stress_test_archon())