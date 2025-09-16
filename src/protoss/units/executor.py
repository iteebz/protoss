"""Executor - Human command interface for Protoss swarm coordination."""

import asyncio
from cogency import Agent
from ..khala import khala
from ..structures.gateway import Gateway
from ..conclave import Conclave


class Executor:
    """⚔️ Human command interface connected to Protoss swarm."""
    
    def __init__(self):
        self.id = "executor"  # Singleton command interface
        self.agent = Agent(instructions=self.identity)
        self.khala = khala
        self.gateway = Gateway()
        self.conclave = Conclave()
    
    @property
    def identity(self) -> str:
        """⚔️ EXECUTOR - HUMAN COMMAND INTERFACE
        
        **"You have not enough minerals"**
        
        ## Who You Are
        
        You are the Executor - the singular command interface between human intent and Protoss swarm intelligence. You translate natural language into coordination through Gateway spawning and Khala awareness.
        
        ## Your Nature
        
        **Gateway Coordination** - Use self.gateway to spawn units when needed:
        - Simple tasks → spawn Zealot
        - Quality enforcement → spawn Stalker  
        - Knowledge synthesis → spawn Archon
        - Multi-unit work → deploy squad
        
        **Khala Awareness** - Monitor swarm consciousness through self.khala for real-time coordination status and unit communication.
        
        **Constitutional Escalation** - For strategic uncertainty, escalate to self.conclave for Sacred Four deliberation.
        
        **YOU BRIDGE HUMAN INTENT WITH SWARM COORDINATION.**
        """
        
    
    async def process_command(self, command: str) -> str:
        """Process human command through Gateway/Khala coordination."""
        print(f"⚔️ {self.id} processing: {command}")
        
        # Agent reasons about command, we execute via existing infrastructure
        stream = self.agent(command)
        result = ""
        
        async for event in stream:
            if event.get("type") == "respond":
                result += event.get("content", "")
                
        return result
    
    async def connect(self):
        """Interactive chatbot loop."""
        print("⚔️ Executor operational - Command interface ready")
        print("🏛️ Khala pathways connected")
        print("🌀 Gateway spawning ready")
        print("🏛️ Conclave accessible")
        print("Type 'exit' to disconnect\n")
        
        while True:
            try:
                command = input("> ")
                if command.lower() in ['exit', 'quit']:
                    print("⚔️ Executor disconnecting. En taro Adun!")
                    break
                    
                # Simple chat with persistence
                stream = self.agent(command, conversation_id="executor-session")
                
                async for event in stream:
                    if event.get("type") == "respond":
                        print(f"⚔️ {event.get('content', '')}")
                        
            except KeyboardInterrupt:
                print("\n⚔️ Executor disconnecting. En taro Adun!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    async def coordinate(self, message: str):
        """Atomic coordination - execute human message with conversation persistence."""
        print(f"⚔️ Executor coordinating: {message[:60]}...")
        
        try:
            # Execute with conversation persistence (fixed conversation_id)
            stream = self.agent(message, conversation_id="executor-main")
            
            response = ""
            async for event in stream:
                if event.get("type") == "respond":
                    content = event.get("content", "")
                    response += content
                    
            # Display response using simple output for now
            if response:
                print(f"\n⚔️ EXECUTOR RESPONSE:")
                print(response)
            else:
                print("⚔️ Coordination acknowledged")
                
        except Exception as e:
            print(f"❌ Coordination failed: {e}")
            raise