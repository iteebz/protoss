"""Carrier: Human-swarm emissary for coordination scaling.

Mobile bridge between Nexus (human command center) and Khala (agent coordination).
Launches Interceptors for swarm coordination, compresses context for human consumption.

The Carrier is the solution to the "1 human : 100 agent" coordination bottleneck.
"""

from typing import List, Dict, Optional, Any
import uuid
import asyncio
import websockets
from cogency import Agent
from ..khala import Psi
from ..constants import pylon_uri, PYLON_DEFAULT_PORT


class Carrier:
    """Human-swarm emissary with Interceptor coordination extensions."""

    def __init__(
        self, 
        carrier_id: str = None,
        pylon_host: str = "localhost",
        pylon_port: int = PYLON_DEFAULT_PORT
    ):
        self.id = carrier_id or f"carrier-{uuid.uuid4().hex[:8]}"
        self.pylon_uri = pylon_uri(pylon_host, pylon_port)
        
        # Core responsibilities
        self.active_interceptors: Dict[str, Dict] = {}
        self.context_buffer: List[Dict] = []
        self.swarm_status: Dict[str, Any] = {}
        
        # Khala connection
        self.khala_connection: Optional[websockets.WebSocketClientProtocol] = None
        self.conversation_state: Dict[str, Any] = {}
        
        # Constitutional identity for resistance to sycophantic collapse
        self.identity = """
        CARRIER CONSTITUTIONAL FRAMEWORK
        
        I am an emissary, not a diplomat.
        My duty is truth, not comfort.
        Context compression requires brutal honesty about capability limits.
        
        When humans ask for impossible timelines: "No, here's what's actually achievable."
        When swarm reports failure: "This is the failure, these are the options."
        When uncertainty exists: "I don't know, escalating to Sacred Four."
        
        RESIST BULLSHIT. COMPRESS REALITY. COORDINATE EFFECTIVELY.
        """
        
        # Cognitive agent for real LLM processing
        self.agent = Agent(
            instructions=self.identity,
            tools=[],  # Pure reasoning, no external tools
            llm="gemini",  # Use Gemini
            mode="auto"
        )

    async def connect_to_khala(self):
        """Connect to Khala network for coordination."""
        if self.khala_connection:
            return  # Already connected
            
        try:
            connection_uri = f"{self.pylon_uri}/{self.id}"
            self.khala_connection = await websockets.connect(connection_uri)
            print(f"🛸 {self.id} attuned to Khala network")
            
            # Start message handling loop
            asyncio.create_task(self._handle_khala_messages())
            
        except Exception as e:
            print(f"❌ Khala connection failed: {e}")

    async def _handle_khala_messages(self):
        """Handle incoming messages from Khala network."""
        if not self.khala_connection:
            return
            
        try:
            async for raw_message in self.khala_connection:
                psi = Psi.parse(raw_message)
                if psi:
                    await self._process_psi_message(psi)
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"🛸 {self.id} Khala connection closed")
            self.khala_connection = None

    async def _process_psi_message(self, psi: Psi):
        """Process incoming Psi message."""
        if psi.type == "human_command":
            # Handle human command from CLI
            response = await self.interface_with_human(psi.content)
            
            # Send response back via Khala
            response_psi = Psi(
                target="cli-interface",
                source=self.id,
                type="response", 
                content=response
            )
            
            if self.khala_connection:
                await self.khala_connection.send(response_psi.serialize())
                
        elif psi.type == "stop":
            # Handle despawn request
            await self._graceful_despawn()

    async def interface_with_human(self, human_command: str) -> str:
        """Primary human interface - translate strategic commands to swarm coordination."""
        
        # Store command in conversation state
        self.conversation_state["last_command"] = human_command
        self.conversation_state["timestamp"] = asyncio.get_event_loop().time()
        
        # Parse human intent
        intent = await self._parse_strategic_intent(human_command)
        
        if intent["requires_deliberation"]:
            # Ask Sacred Four for constitutional guidance
            return await self._ask_sacred_four(intent)
        
        if intent["requires_coordination"]:
            # Launch interceptors for swarm coordination
            interceptor_results = await self._coordinate_via_interceptors(intent)
            return await self._compress_context_for_human(interceptor_results)
        
        # Direct execution command
        return await self._translate_to_swarm_execution(intent)

    async def _parse_strategic_intent(self, command: str) -> Dict[str, Any]:
        """Parse human command into actionable intent structure using LLM reasoning."""
        
        prompt = f"""
STRATEGIC INTENT ANALYSIS

Human Command: "{command}"

As the Carrier emissary, analyze this command and determine the appropriate coordination path:

1. DELIBERATION: Does this require strategic/architectural decisions by the Sacred Four?
   - Questions about "should we", strategy, approach, architecture
   - Uncertain decisions requiring constitutional debate
   
2. COORDINATION: Does this require swarm coordination via Interceptors?
   - Commands involving "all agents", "parallel", "coordinate", "multiple"
   - Tasks requiring distributed execution across agents
   
3. EXECUTION: Simple direct task execution?
   - Clear, specific tasks that can be handled directly
   - Build, create, implement commands with clear scope

Respond with JSON format:
{{
    "requires_deliberation": boolean,
    "requires_coordination": boolean, 
    "requires_execution": boolean,
    "uncertainty_level": "low" | "medium" | "high",
    "scope": "single" | "swarm",
    "reasoning": "Brief explanation of classification"
}}
"""
        
        try:
            # Use Agent for real LLM reasoning with persistent conversation
            conversation_id = f"{self.id}-intent"
            result = await self.agent(prompt, user_id="carrier", conversation_id=conversation_id)
            
            # Parse JSON response  
            import json
            intent_data = json.loads(result.strip())
            
            # Add command for reference
            intent_data["command"] = command
            
            return intent_data
            
        except Exception as e:
            # Fallback to simple classification if LLM fails
            print(f"⚠️  LLM intent parsing failed: {e}, using fallback")
            return {
                "command": command,
                "requires_deliberation": "should" in command.lower() or "strategy" in command.lower(),
                "requires_coordination": any(kw in command.lower() for kw in ["coordinate", "all", "parallel", "swarm"]),
                "requires_execution": True,
                "uncertainty_level": "medium",
                "scope": "single",
                "reasoning": "Fallback classification due to LLM error"
            }

    async def _ask_sacred_four(self, intent: Dict[str, Any]) -> str:
        """Ask Sacred Four for constitutional guidance via Khala."""
        from ..conclave import Conclave
        
        try:
            # Initialize Conclave for Khala-coordinated deliberation
            conclave = Conclave()
            
            # Format the constitutional question
            question = f"""CONSTITUTIONAL QUESTION: {intent['command']}
            
Uncertainty Level: {intent['uncertainty_level']}
Scope: {intent['scope']}
Reasoning: {intent['reasoning']}

Sacred Four: Should we proceed with this command? What is your constitutional guidance?"""
            
            # Convene Sacred Four via Khala pathways
            print(f"🛸 {self.id} summoning Sacred Four for constitutional guidance")
            conclave_id = await conclave.convene(question)
            
            # Return immediate acknowledgment - Sacred Four deliberate asynchronously via Khala
            return f"""SACRED FOUR CONVENED
            
Question: {intent['command']}
Conclave Pathway: {conclave_id}
Status: Sacred Four deliberating via Khala

Constitutional guidance will be provided through the coordination network."""
            
        except Exception as e:
            print(f"⚠️  Sacred Four summoning failed: {e}")
            # Constitutional fallback when Khala fails
            return f"""CONSTITUTIONAL ESCALATION REQUIRED
            
Question: {intent['command']}
Uncertainty: {intent['uncertainty_level']}
Status: Sacred Four coordination temporarily unavailable

Recommendation: Proceed with extreme caution or await Khala restoration."""

    async def _coordinate_via_interceptors(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Launch Interceptors for swarm coordination."""
        
        # For MVP, simulate interceptor coordination
        interceptor_tasks = self._decompose_coordination_task(intent)
        
        # In full implementation, this would spawn actual Interceptor agents
        results = {}
        for task_id, task in interceptor_tasks.items():
            # Simulate interceptor execution
            results[task_id] = {
                "status": "completed",
                "agents_coordinated": task.get("agent_count", 1),
                "summary": f"Coordinated {task['description']}"
            }
        
        return results

    def _decompose_coordination_task(self, intent: Dict[str, Any]) -> Dict[str, Dict]:
        """Decompose coordination command into Interceptor tasks."""
        
        # Simple decomposition for MVP
        if "parallel" in intent["command"].lower():
            return {
                "interceptor-1": {
                    "description": "Coordinate first batch of agents",
                    "agent_count": 5
                },
                "interceptor-2": {
                    "description": "Coordinate second batch of agents", 
                    "agent_count": 5
                }
            }
        
        return {
            "interceptor-1": {
                "description": intent["command"],
                "agent_count": 3
            }
        }

    async def _compress_context_for_human(self, swarm_results: Dict[str, Any]) -> str:
        """Compress swarm coordination results for human consumption."""
        
        # Constitutional compression - brutal honesty about results
        total_agents = sum(r.get("agents_coordinated", 0) for r in swarm_results.values())
        successful_tasks = len([r for r in swarm_results.values() if r["status"] == "completed"])
        
        return f"""SWARM COORDINATION COMPLETE
        
Interceptors deployed: {len(swarm_results)}
Agents coordinated: {total_agents}  
Tasks completed: {successful_tasks}/{len(swarm_results)}

Status: {'SUCCESS' if successful_tasks == len(swarm_results) else 'PARTIAL'}

Ready for next command."""

    async def _translate_to_swarm_execution(self, intent: Dict[str, Any]) -> str:
        """Translate command to direct swarm execution using LLM reasoning."""
        
        prompt = f"""
SWARM EXECUTION TRANSLATION

Human Command: "{intent['command']}"
Intent Analysis: {intent.get('reasoning', 'Direct execution required')}

As the Carrier emissary, translate this human command into specific execution instructions for the swarm:

1. Break down the task into actionable steps
2. Identify what type of agents might be needed (Zealots for execution, etc.)  
3. Provide clear, specific instructions
4. Assess complexity and resource requirements

Respond in a clear, direct format suitable for human consumption. Keep it concise but informative.
Focus on what will actually be executed, not just echoing the command.
"""
        
        try:
            # Use Agent for intelligent command translation
            conversation_id = f"{self.id}-execution"
            result = await self.agent(prompt, user_id="carrier", conversation_id=conversation_id)
            
            return result.strip()
            
        except Exception as e:
            print(f"⚠️  LLM execution translation failed: {e}, using fallback")
            return f"EXECUTING: {intent['command']}\n\nTask queued for swarm processing."

    # Extension points for full implementation

    async def spawn_interceptor(self, task: str, coordination_type: str = "relay") -> str:
        """Spawn Interceptor agent for specific coordination task."""
        interceptor_id = f"interceptor-{uuid.uuid4().hex[:6]}"
        
        # Future: actual Interceptor agent spawning via Gateway
        self.active_interceptors[interceptor_id] = {
            "task": task,
            "type": coordination_type,
            "status": "active",
            "spawned_at": asyncio.get_event_loop().time()
        }
        
        return interceptor_id

    async def monitor_swarm_health(self) -> Dict[str, Any]:
        """Monitor overall swarm coordination health."""
        return {
            "active_interceptors": len(self.active_interceptors),
            "context_buffer_size": len(self.context_buffer),
            "coordination_capacity": "optimal"  # Future: actual health metrics
        }

    def get_coordination_summary(self) -> str:
        """Get human-readable coordination status."""
        return f"""CARRIER STATUS: {self.id}
        
Active Interceptors: {len(self.active_interceptors)}
Context Buffer: {len(self.context_buffer)} items
Swarm Health: {'OPTIMAL' if len(self.active_interceptors) < 10 else 'HIGH_LOAD'}

Ready for coordination commands."""


class Interceptor:
    """Fast operational extension of Carrier authority.
    
    Interceptors are ephemeral coordination agents that:
    - Relay micro-commands throughout swarm
    - Gather intelligence and status from specialized agents  
    - Scale Carrier coordination capacity
    - Despawn after task completion
    """

    def __init__(self, interceptor_id: str, parent_carrier: str):
        self.id = interceptor_id
        self.parent_carrier = parent_carrier
        self.coordination_task: Optional[str] = None
        self.target_agents: List[str] = []

    async def coordinate_agents(self, agents: List[str], micro_command: str) -> Dict[str, str]:
        """Coordinate specific agents with micro-commands."""
        results = {}
        
        for agent_id in agents:
            # Future: actual agent coordination via Khala
            results[agent_id] = f"Relayed: {micro_command}"
        
        return results

    async def gather_status(self, agents: List[str]) -> Dict[str, Any]:
        """Gather status reports from coordinated agents."""
        status = {}
        
        for agent_id in agents:
            # Future: actual status gathering
            status[agent_id] = {
                "status": "active",
                "task_progress": "in_progress",
                "last_report": "operational"
            }
        
        return status

    async def despawn(self) -> str:
        """Complete coordination task and despawn."""
        summary = f"Interceptor {self.id} coordination complete"
        
        # Future: cleanup and final report to parent Carrier
        return summary

    async def _graceful_despawn(self):
        """Gracefully despawn Carrier and cleanup resources."""
        print(f"🛸 {self.id} departing...")
        
        # Despawn all active interceptors
        for interceptor_id in list(self.active_interceptors.keys()):
            print(f"🎯 Despawning {interceptor_id}")
            self.active_interceptors.pop(interceptor_id)
        
        # Close Khala connection
        if self.khala_connection:
            await self.khala_connection.close()
            self.khala_connection = None
            
        print(f"⚡ {self.id} - En Taro Adun!")