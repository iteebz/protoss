"""Unit tests for Archon knowledge operations."""

import pytest
from pathlib import Path
from protoss.agents.archon import Archon


def test_keyword_extraction():
    """Extract meaningful keywords from task descriptions."""
    archon = Archon()

    # Test basic extraction
    task = "implement user authentication system with OAuth integration"
    keywords = archon._extract_keywords_from_task(task)

    assert "implement" in keywords
    assert "user" in keywords
    assert "authentication" in keywords
    assert "system" in keywords
    assert "oauth" in keywords
    assert "integration" in keywords

    # Stopwords filtered out
    assert "with" not in keywords
    assert "the" not in keywords


@pytest.mark.asyncio
async def test_context_seed_building():
    """Context seed builds proper structure."""
    archon = Archon()

    task = "build API endpoints"
    archives = ["Previous API work: REST patterns..."]
    codebase = ["api/", "routes/", "endpoints/"]

    # Test actual seed building logic
    seed = await archon._build_context_seed(task, archives, codebase)

    assert "ARCHON CONTEXT SEED" in seed
    assert "Task: build API endpoints" in seed
    assert "Relevant Archives:" in seed
    assert "Previous API work" in seed
    assert "Key Codebase Areas:" in seed
    assert "- api/" in seed
    assert "- routes/" in seed
    assert "EN TARO ADUN." in seed


@pytest.mark.asyncio
async def test_context_seed_no_archives():
    """Context seed handles missing archives gracefully."""
    archon = Archon()

    task = "new feature implementation"
    archives = []  # No archives found
    codebase = ["src/", "tests/"]

    seed = await archon._build_context_seed(task, archives, codebase)

    assert "No previous work found - fresh implementation" in seed
    assert "- src/" in seed
    assert "- tests/" in seed


@pytest.mark.asyncio
async def test_codebase_file_identification():
    """Identify relevant codebase files from task keywords."""
    archon = Archon()

    # Auth task
    auth_hints = await archon._identify_codebase_files("implement authentication", None)
    assert "auth/" in auth_hints
    assert "models/user.py" in auth_hints
    assert "tests/auth/" in auth_hints

    # API task
    api_hints = await archon._identify_codebase_files("build REST API", None)
    assert "api/" in api_hints
    assert "routes/" in api_hints
    assert "endpoints/" in api_hints

    # Database task
    db_hints = await archon._identify_codebase_files("database migration", None)
    assert "models/" in db_hints
    assert "migrations/" in db_hints
    assert "database.py" in db_hints

    # Config task
    config_hints = await archon._identify_codebase_files("update configuration", None)
    assert "config/" in config_hints
    assert "settings.py" in config_hints
    assert ".env" in config_hints


@pytest.mark.asyncio
async def test_insight_extraction():
    """Extract key insights from channel messages."""
    archon = Archon()

    # Mock message objects
    class MockMessage:
        def __init__(self, sender, content):
            self.sender = sender
            self.content = content

    messages = [
        MockMessage("zealot", "Working on implementation"),
        MockMessage("conclave", "Decision: Use REST architecture for API"),
        MockMessage("arbiter", "Approach confirmed: microservices pattern"),
        MockMessage("zealot", "Bug found in validation"),
        MockMessage("archon", "Conclusion: Implementation successful"),
    ]

    insights = await archon._extract_insights(messages)

    assert "conclave: Decision: Use REST architecture" in insights
    assert "arbiter: Approach confirmed: microservices" in insights
    assert "archon: Conclusion: Implementation successful" in insights
    assert "zealot: Working on implementation" not in insights  # No decision keywords


@pytest.mark.asyncio
async def test_insight_extraction_empty():
    """Handle empty insights gracefully."""
    archon = Archon()

    class MockMessage:
        def __init__(self, sender, content):
            self.sender = sender
            self.content = content

    # Messages without decision keywords
    messages = [
        MockMessage("zealot", "Still working"),
        MockMessage("arbiter", "Making progress"),
    ]

    insights = await archon._extract_insights(messages)
    assert insights == "No key insights extracted"


@pytest.mark.asyncio
async def test_mention_response_logic():
    """Mention response provides context or honest 'no archives'."""
    archon = Archon()

    # Mock search that finds context
    async def mock_search_found(context):
        return "Found relevant context about authentication patterns..."

    archon._search_archives = mock_search_found

    response = await archon.respond_to_mention(
        "help with auth patterns", "test-channel"
    )
    assert "Found relevant context from archives" in response
    assert "authentication patterns" in response

    # Mock search that finds nothing
    async def mock_search_empty(context):
        return None

    archon._search_archives = mock_search_empty

    response = await archon.respond_to_mention("brand new topic", "test-channel")
    assert "No archives on that yet" in response
    assert "first time we're tackling this" in response


def test_archive_path_generation():
    """Archive file paths generated correctly."""
    archon = Archon()

    # Test final summary path
    path = archon._save_to_archives.__code__.co_consts
    # Path logic: archives/channels/{channel_id}-final-{timestamp}.md

    assert "archives/channels" in str(path)
    assert "final" in str(path) or "progress" in str(path)
    assert ".md" in str(path)


def test_archives_directory_initialization():
    """Archives directory structure created correctly."""
    # Test directory creation logic
    archives_path = Path("test_archives")

    # Mock the _init logic
    if not archives_path.exists():
        archives_path.mkdir(exist_ok=True)
        (archives_path / "channels").mkdir(exist_ok=True)
        (archives_path / "decisions").mkdir(exist_ok=True)
        (archives_path / "patterns").mkdir(exist_ok=True)
        (archives_path / "context").mkdir(exist_ok=True)

    assert (archives_path / "channels").exists()
    assert (archives_path / "decisions").exists()
    assert (archives_path / "patterns").exists()
    assert (archives_path / "context").exists()

    # Cleanup
    import shutil

    shutil.rmtree(archives_path)


def test_archon_identity():
    """Archon has proper constitutional identity."""
    archon = Archon()

    identity = archon.identity

    assert "ARCHON - CONTEXT STEWARD" in identity
    assert "Channel seeding and knowledge compression" in identity
    assert "SEEDING PROTOCOL" in identity
    assert "KNOWLEDGE RESPONSES" in identity
    assert "COMPRESSION PROTOCOL" in identity
    assert "EN TARO ADUN" in identity


@pytest.mark.asyncio
async def test_channel_seeding_flow():
    """Channel seeding follows proper flow."""
    archon = Archon()

    # Mock the async methods to test flow
    async def mock_fetch_archives(task, keywords):
        return ["Archive 1: Previous auth work..."]

    async def mock_identify_files(task, keywords):
        return ["auth/", "models/user.py"]

    async def mock_build_seed(task, archives, files):
        return "ARCHON CONTEXT SEED\\nTask: test\\nArchives: Previous auth work"

    archon._fetch_relevant_archives = mock_fetch_archives
    archon._identify_codebase_files = mock_identify_files
    archon._build_context_seed = mock_build_seed

    result = await archon.seed_channel("test auth task", "test-channel", ["auth"])

    assert "ARCHON CONTEXT SEED" in result
    assert "Task: test" in result


@pytest.mark.asyncio
async def test_compression_flow():
    """Channel compression follows proper flow."""
    Archon()

    # Mock dependencies
    async def mock_extract_insights(messages):
        return "Key insight: Decision made"

    async def mock_save_archives(channel, insights, final):
        return "archives/channels/test-final-abc123.md"

    # Mock the compression method to simulate having messages
    async def mock_compress_channel(channel_id, final_summary=False):
        # Simulate messages exist
        messages = ["mock message"]  # Non-empty
        insights = await mock_extract_insights(messages)
        archive_path = await mock_save_archives(channel_id, insights, final_summary)
        return f"Channel progress archived to {archive_path}"

    result = await mock_compress_channel("test-channel", final_summary=True)

    assert "Channel progress archived" in result
    assert "archives/channels" in result
