"""Conclave: The Sacred Four provide constitutional governance and strategic coordination.

Canonical three-phase protocol:
1. Position: Independent Sacred Four reasoning
2. Consensus: Collaborative deliberation via Khala
3. Response: Unified constitutional/strategic guidance
"""

import asyncio
import uuid
import websockets
from typing import Dict
# Conclave uses singleton Khala discovery
from .units.tassadar import Tassadar
from .units.zeratul import Zeratul
from .units.artanis import Artanis
from .units.fenix import Fenix
from .khala import Psi


class Conclave:
    """Sacred Four constitutional governance and strategic coordination.
    
    Canonical protocol: Position → Consensus → Response
    """

    def __init__(self):
        # No configuration needed - uses singleton Khala discovery
        
        # Initialize Sacred Four constitutional minds via Gateway
        from .structures.gateway import Gateway
        gateway = Gateway()
        
        self.tassadar = gateway.spawn("tassadar")
        self.zeratul = gateway.spawn("zeratul")
        self.artanis = gateway.spawn("artanis")
        self.fenix = gateway.spawn("fenix")
        
        self.sacred_four = {
            "tassadar": self.tassadar,
            "zeratul": self.zeratul, 
            "artanis": self.artanis,
            "fenix": self.fenix
        }

    async def convene(self, question: str) -> str:
        """Canonical three-phase Sacred Four coordination.
        
        Phase 1: Independent positions
        Phase 2: Consensus deliberation 
        Phase 3: Unified response
        """
        print(f"🔮 Sacred Four convening for coordination")
        print(f"📋 Question: {question}")
        
        # Phase 1: Independent positions (no cross-influence)
        positions = await self._get_positions(question)
        
        # Phase 2: Consensus deliberation via Khala pathways
        consensus = await self._deliberate(question, positions)
        
        # Phase 3: Return unified response
        return consensus
        
    async def _get_positions(self, question: str) -> Dict[str, str]:
        """Phase 1: Sacred Four form independent positions."""
        print(f"⚡ Phase 1: Sacred Four forming independent positions...")
        
        # Parallel position formation (no cross-contamination)
        position_tasks = {
            name: agent.deliberate(question) 
            for name, agent in self.sacred_four.items()
        }
        
        results = await asyncio.gather(*position_tasks.values(), return_exceptions=True)
        positions = {}
        
        for (name, _), result in zip(position_tasks.items(), results):
            if isinstance(result, Exception):
                positions[name] = f"POSITION FAILED: {result}"
                print(f"⚠️  {name} position formation failed: {result}")
            else:
                positions[name] = result
                print(f"💭 {name}: {result[:80]}...")
        
        return positions
        
    async def _deliberate(self, question: str, positions: Dict[str, str]) -> str:
        """Phase 2: Sacred Four deliberate to consensus via Khala."""
        print(f"⚡ Phase 2: Sacred Four deliberating to consensus...")
        
        conclave_id = f"conclave-{uuid.uuid4().hex[:8]}"
        
        # Sacred Four deliberate via Khala pathways until consensus
        participation_tasks = [
            self._participate(agent, positions[name], question, conclave_id)
            for name, agent in self.sacred_four.items()
        ]
        
        # Wait for consensus to emerge
        await asyncio.gather(*participation_tasks, return_exceptions=True)
        
        # Extract consensus from Khala pathway
        return await self._extract_consensus(conclave_id)
        
    async def _extract_consensus(self, conclave_id: str) -> str:
        """Extract consensus from Khala pathway memories."""
        from .khala import khala
        
        # Get pathway memories
        pathway_data = khala.pathway(conclave_id)
        if not pathway_data:
            return "CONSENSUS FAILED: No deliberation pathway found"
        
        memories = pathway_data.get('recent_memories', [])
        if not memories:
            return "CONSENSUS FAILED: No deliberation messages found"
        
        # Look for CONSENSUS messages or extract final guidance
        consensus_messages = [msg for msg in memories if 'CONSENSUS' in msg or 'consensus' in msg.lower()]
        
        if consensus_messages:
            return f"SACRED FOUR CONSENSUS:\n\n{consensus_messages[-1]}"
        else:
            # Synthesize consensus from deliberation using constitutional synthesis
            return await self._synthesize_consensus(memories)

    async def _synthesize_consensus(self, memories: list) -> str:
        """Synthesize coherent consensus from Sacred Four deliberation."""
        from cogency import Agent
        
        # Join all deliberation messages
        deliberation = "\n".join(memories[-20:])  # Last 20 messages for context
        
        synthesis_prompt = f"""
SACRED FOUR CONSTITUTIONAL SYNTHESIS

You are synthesizing the deliberation of the Sacred Four into coherent constitutional guidance.

DELIBERATION RECORD:
{deliberation}

Your task:
1. Extract the core points of agreement
2. Identify where consensus was reached
3. Synthesize into clear constitutional guidance
4. If no clear consensus, state the main competing positions

Respond with:
SACRED FOUR CONSENSUS: [Clear, actionable constitutional guidance based on the deliberation]
"""
        
        # Use basic agent for synthesis
        synthesizer = Agent(
            instructions="You synthesize complex deliberations into clear decisions. Focus on extracting actionable guidance.",
            tools=[]
        )
        
        try:
            stream = synthesizer(synthesis_prompt, conversation_id="consensus-synthesis")
            async for event in stream:
                if event.get("type") == "respond":
                    return event.get("content", "SYNTHESIS FAILED: No response generated")
            await stream.aclose()
        except Exception as e:
            return f"SYNTHESIS FAILED: {e}\n\nRAW DELIBERATION:\n{deliberation}"
        
        return "SYNTHESIS FAILED: No valid consensus extracted"

    async def _participate(self, sacred_agent, position: str, question: str, conclave_id: str):
        """Sacred Four agent participates in Khala deliberation."""
        agent_id = sacred_agent.id
        
        try:
            # Connect to conclave pathway
            from .khala import khala
            async with khala.connect(agent_id) as khala_conn:
                print(f"🔹 {agent_id} joined conclave pathway")
                
                # Present initial position
                await khala_conn.send(conclave_id, f"position:{position}")
                print(f"💭 {agent_id} presented position")
                
                # Deliberate via Khala coordination
                await self._khala_deliberation(sacred_agent.agent, agent_id, position, question, conclave_id, khala_conn)
                
        except Exception as e:
            print(f"⚠️  {agent_id} participation failed: {e}")

    async def _khala_deliberation(self, agent, agent_id: str, position: str, question: str, conclave_id: str, khala_conn):
        """Agent deliberates via Khala coordination until consensus."""
        
        discussion_context = f"""
You are participating in Sacred Four deliberation on pathway {conclave_id}.
Your constitutional position: {position}
Original question: {question}

You will receive messages from other Sacred Four members. Respond when:
- You disagree with another position
- Someone addresses you directly  
- You want to clarify or defend your stance
- You have new insights based on the discussion
- You believe consensus has been reached

Respond through Psi messages: §PSI:{conclave_id}:{agent_id}:discuss:your_response

When consensus is reached, send: §PSI:{conclave_id}:{agent_id}:CONSENSUS:final_constitutional_guidance
"""
        
        try:
            # Listen for Khala messages and respond appropriately  
            while True:
                psi_message = await khala_conn.receive()
                if not psi_message:
                    break
                message = psi_message.content
                prompt = f"{discussion_context}\n\nIncoming: {message}\n\nRespond if appropriate:"
                
                # Stream response via cogency async generator
                agent_stream = agent(prompt, conversation_id=f"{agent_id}-conclave")
                try:
                    async for event in agent_stream:
                        if event.get("type") == "respond":
                            response = event.get("content", "").strip()
                            if response and not response.lower().startswith("no response"):
                                await khala_conn.send(conclave_id, f"discuss:{response}")
                                print(f"⚡ {agent_id}: {response[:50]}...")
                            break
                finally:
                    await agent_stream.aclose()
                        
        except Exception as e:
            print(f"❌ {agent_id} deliberation error: {e}")

