"""Carrier: Human-swarm emissary for coordination scaling.

🛸 CONVERSATIONAL INTERFACE TO AI SWARMS 🛸

Solves copy-paste coordination hell. Intelligent routing between:
- Sacred Four (constitutional questions) 
- Squad deployment (multi-agent tasks)
- Direct execution (simple tasks)
"""

import uuid
import asyncio
import websockets
from typing import Optional
from cogency import Agent
from ..khala import Psi
# Carrier uses service discovery - no hardcoded constants needed


class Carrier:
    """🛸 Human-swarm emissary with conversational intelligence."""

    def __init__(self, carrier_id: str = None):
        self.id = carrier_id or f"carrier-{uuid.uuid4().hex[:8]}"
        self.khala_connection: Optional[websockets.WebSocketClientProtocol] = None
        self.agent = None  # Injected by Gateway
        
    def _discover_conclave(self):
        """Discover Conclave service."""
        from ..conclave import Conclave
        return Conclave()
        
    def _discover_gateway(self):
        """Discover Gateway service."""
        from ..structures.gateway import Gateway
        return Gateway()
        
    def _discover_archon(self):
        """Discover Archon service.""" 
        from ..units.archon import Archon
        return Archon()

    @property
    def coordination_intelligence(self) -> str:
        """Carrier coordination intelligence for command routing."""
        return """You are a Carrier - human-swarm coordination emissary.

ROUTING INTELLIGENCE:
- Constitutional questions → Sacred Four deliberation
- Multi-agent tasks → Squad deployment  
- Simple tasks → Direct Zealot execution
- Complex analysis → Archon knowledge synthesis

COMMAND PATTERNS:
"should we use X?" → Constitutional (Sacred Four)
"build auth system" → Squad deployment (zealot + stalker)
"fix this bug" → Direct execution (single zealot)
"research best practices" → Knowledge synthesis (archon)

RESPONSE FORMAT:
Always respond with routing decision and brief explanation:
- ROUTE: sacred_four | squad | zealot | archon
- REASONING: Why this routing choice
- ACTION: Specific coordination command

Be conversational but decisive. You're coordinating AI swarms, not chatting."""

    async def process_command(self, command: str) -> str:
        """🛸 CORE CARRIER INTELLIGENCE - Route human commands to swarm coordination."""
        print(f"🛸 {self.id} processing: {command}")
        
        # Route command through coordination intelligence
        routing_prompt = f"""
Human command: "{command}"

Analyze and route this command. What's the best coordination approach?
"""
        
        routing_decision = ""
        agent_stream = self.agent(routing_prompt, conversation_id=f"{self.id}-routing")
        try:
            async for event in agent_stream:
                if event.get("type") == "respond":
                    routing_decision = event.get("content", "")
                    break
        finally:
            await agent_stream.aclose()
        
        # Execute the routing decision
        if "sacred_four" in routing_decision.lower():
            return await self._route_to_sacred_four(command)
        elif "squad" in routing_decision.lower():
            return await self._route_to_squad(command)
        elif "zealot" in routing_decision.lower():
            return await self._route_to_zealot(command)
        elif "archon" in routing_decision.lower():
            return await self._route_to_archon(command)
        else:
            return f"🛸 Routing unclear: {routing_decision}"

    async def _route_to_sacred_four(self, question: str) -> str:
        """Route constitutional questions to Sacred Four deliberation."""
        print(f"🛸 {self.id} routing to Sacred Four: {question}")
        
        try:
            conclave = self._discover_conclave()
            guidance = await conclave.convene(question)
            return f"🔮 SACRED FOUR GUIDANCE:\n\n{guidance}"
        except Exception as e:
            return f"❌ Sacred Four coordination failed: {e}"

    async def _route_to_squad(self, task: str) -> str:
        """Route multi-agent tasks to squad deployment."""
        print(f"🛸 {self.id} deploying squad for: {task}")
        
        try:
            gateway = self._discover_gateway()
            squad_units = ["zealot", "zealot", "stalker"] 
            squad_id = await gateway.deploy_squad(task, squad_units)
            return f"⚔️ SQUAD DEPLOYED: {squad_id}\nUnits: {squad_units}\nTask: {task}"
        except Exception as e:
            return f"❌ Squad deployment failed: {e}"

    async def _route_to_zealot(self, task: str) -> str:
        """Route simple tasks to direct Zealot execution."""
        print(f"🛸 {self.id} routing to Zealot: {task}")
        
        try:
            gateway = self._discover_gateway()
            zealot_id = await gateway.spawn_zealot(task)
            return f"⚔️ ZEALOT DEPLOYED: {zealot_id}\nTask: {task}"
        except Exception as e:
            return f"❌ Zealot deployment failed: {e}"

    async def _route_to_archon(self, query: str) -> str:
        """Route knowledge synthesis to Archon."""
        print(f"🛸 {self.id} routing to Archon: {query}")
        
        try:
            archon = self._discover_archon()
            domain = "coordination"  # Default domain
            knowledge = await archon.query_knowledge(domain)
            return f"🔮 ARCHON KNOWLEDGE:\n\n{knowledge}"
        except Exception as e:
            return f"❌ Archon knowledge synthesis failed: {e}"

    async def connect_to_khala(self):
        """Connect to Khala network for coordination."""
        if self.khala_connection:
            return
            
        try:
            from ..khala import Khala
            connection_uri = f"{Khala.get_grid_uri()}/{self.id}"
            self.khala_connection = await websockets.connect(connection_uri)
            print(f"🛸 {self.id} attuned to Khala network")
            
            asyncio.create_task(self._handle_khala_messages())
            
        except Exception as e:
            print(f"❌ Khala connection failed: {e}")

    async def _handle_khala_messages(self):
        """Handle incoming commands from Khala network."""
        if not self.khala_connection:
            return
            
        try:
            async for raw_message in self.khala_connection:
                psi = Psi.parse(raw_message)
                if psi and psi.content:
                    # Process command through coordination intelligence
                    response = await self.process_command(psi.content)
                    
                    response_psi = Psi(
                        pathway=psi.sender,  # Reply to sender
                        sender=self.id,
                        content=response
                    )
                    
                    await self.khala_connection.send(response_psi.serialize())
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"🛸 {self.id} Khala connection closed")
            self.khala_connection = None

    async def despawn(self):
        """Gracefully despawn Carrier."""
        if self.khala_connection:
            await self.khala_connection.close()
            self.khala_connection = None
        print(f"⚡ {self.id} - En Taro Adun!")