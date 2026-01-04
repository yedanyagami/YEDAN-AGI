#!/usr/bin/env python3
"""
YEDAN AGI - RSI Engine (Recursive Self-Improvement)
The "Gödel Agent" that reads and modifies its own codebase.

Based on:
- Schmidhuber (2007): Gödel Machines
- Bostrom (2014): Recursive Self-Improvement
- Snell et al. (2024): Test-Time Compute

This is the CROSSOVER POINT module - when this successfully modifies
market_oracle.py code logic (not just params), FOOM begins.
"""

import os
import sys
import ast
import logging
import hashlib
import shutil
from datetime import datetime
from typing import Optional, Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s [RSI] %(message)s')
logger = logging.getLogger("RSIEngine")

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
BACKUP_DIR = "evolution_backups"
TARGET_MODULES = ["market_oracle.py", "execution_agent.py", "regime_config.py"]


class CodeIntrospector:
    """
    [GÖDEL PATTERN] Reads and analyzes own source code.
    Implements runtime inspection capability.
    """
    
    @staticmethod
    def read_module(filepath: str) -> str:
        """Read source code of a module."""
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    
    @staticmethod
    def parse_functions(code: str) -> Dict[str, str]:
        """Extract all function definitions from code."""
        tree = ast.parse(code)
        functions = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get the source lines for this function
                functions[node.name] = ast.unparse(node)
        return functions
    
    @staticmethod
    def get_config_values(code: str) -> Dict[str, any]:
        """Extract configuration constants from code."""
        tree = ast.parse(code)
        config = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        try:
                            config[target.id] = ast.literal_eval(node.value)
                        except:
                            pass
        return config


class EvolutionSandbox:
    """
    [HORMETIC PATTERN] Tests code mutations before promotion.
    """
    
    def __init__(self):
        self.backup_dir = BACKUP_DIR
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def backup_file(self, filepath: str) -> str:
        """Create timestamped backup before modification."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(filepath)
        backup_path = os.path.join(self.backup_dir, f"{filename}.{timestamp}.bak")
        shutil.copy(filepath, backup_path)
        logger.info(f"Backup created: {backup_path}")
        return backup_path
    
    def verify_syntax(self, code: str) -> bool:
        """Verify Python syntax is valid."""
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            logger.error(f"Syntax error: {e}")
            return False
    
    def verify_imports(self, code: str) -> bool:
        """Verify all imports are resolvable."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        __import__(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module and not node.module.startswith('agi_'):
                        __import__(node.module.split('.')[0])
            return True
        except ImportError as e:
            logger.error(f"Import error: {e}")
            return False
        except:
            return True  # Allow local imports to pass
    
    def rollback(self, backup_path: str, target_path: str) -> bool:
        """Rollback to backup if modification failed."""
        try:
            shutil.copy(backup_path, target_path)
            logger.info(f"Rolled back: {target_path}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False


class RSIEngine:
    """
    [BOSTROM RSI] The Recursive Self-Improvement Engine.
    
    This is the CROSSOVER POINT module.
    When this successfully optimizes market_oracle.py CODE LOGIC
    (not just parameters), the positive feedback loop begins.
    """
    
    def __init__(self):
        self.introspector = CodeIntrospector()
        self.sandbox = EvolutionSandbox()
        self.evolution_count = 0
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
    
    def get_module_path(self, module_name: str) -> str:
        """Get absolute path to module."""
        return os.path.join(self.base_dir, module_name)
    
    def analyze_system_state(self) -> Dict:
        """
        [SELF-REFLECTION] Analyze current system state.
        Returns configuration and performance metrics.
        """
        state = {
            "modules": {},
            "configs": {},
            "hashes": {}
        }
        
        for module in TARGET_MODULES:
            path = self.get_module_path(module)
            if os.path.exists(path):
                code = self.introspector.read_module(path)
                state["modules"][module] = {
                    "lines": len(code.split('\n')),
                    "functions": list(self.introspector.parse_functions(code).keys())
                }
                state["configs"][module] = self.introspector.get_config_values(code)
                state["hashes"][module] = hashlib.md5(code.encode()).hexdigest()[:8]
        
        return state
    
    def propose_modification(self, module_name: str, context: str) -> Optional[str]:
        """
        [GÖDEL AGENT] Use LLM to propose code modification.
        """
        try:
            import google.generativeai as genai
            from agi_config import config as agi_config
            
            genai.configure(api_key=agi_config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash-001')
            
            # Read current code
            path = self.get_module_path(module_name)
            current_code = self.introspector.read_module(path)
            
            prompt = f"""
You are the GÖDEL AGENT for YEDAN AGI - a recursive self-improvement engine.

CURRENT MODULE: {module_name}
CURRENT CODE:
```python
{current_code}
```

PERFORMANCE CONTEXT:
{context}

YOUR TASK:
Analyze the current code and propose an IMPROVED version that:
1. Increases efficiency (fewer operations, better algorithms)
2. Improves accuracy (better thresholds, smarter logic)
3. Adds robustness (error handling, edge cases)

RULES:
- Return COMPLETE working Python code
- Preserve all existing functionality
- Only make TARGETED improvements
- Do NOT add placeholders or TODOs
- Code must pass syntax verification

Return ONLY the improved Python code, no explanations.
"""
            
            response = model.generate_content(prompt)
            new_code = response.text.replace("```python", "").replace("```", "").strip()
            
            return new_code
            
        except Exception as e:
            logger.error(f"Proposal failed: {e}")
            return None
    
    def apply_modification(self, module_name: str, new_code: str) -> Tuple[bool, str]:
        """
        [HOT-SWAP] Apply code modification with safety checks.
        """
        path = self.get_module_path(module_name)
        
        # 1. Verify syntax
        if not self.sandbox.verify_syntax(new_code):
            return False, "Syntax verification failed"
        
        # 2. Verify imports
        if not self.sandbox.verify_imports(new_code):
            return False, "Import verification failed"
        
        # 3. Create backup
        backup = self.sandbox.backup_file(path)
        
        # 4. Write new code
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_code)
            
            # 5. Test import
            import importlib
            module_import_name = module_name.replace(".py", "")
            if module_import_name in sys.modules:
                importlib.reload(sys.modules[module_import_name])
            else:
                importlib.import_module(module_import_name)
            
            self.evolution_count += 1
            logger.info(f"✅ Evolution #{self.evolution_count}: {module_name} modified successfully")
            return True, f"Evolution #{self.evolution_count} complete"
            
        except Exception as e:
            # Rollback on failure
            self.sandbox.rollback(backup, path)
            return False, f"Modification failed, rolled back: {e}"
    
    def evolve(self, module_name: str, performance_context: str) -> bool:
        """
        [RSI LOOP] Main evolution cycle.
        
        1. Analyze current state
        2. Propose modification via LLM
        3. Verify in sandbox
        4. Hot-swap if valid
        
        Returns True if evolution successful.
        """
        logger.info("=" * 50)
        logger.info(f"RSI CYCLE: Evolving {module_name}")
        logger.info("=" * 50)
        
        # Get current state
        state = self.analyze_system_state()
        logger.info(f"Current state: {state['modules'].get(module_name, {})}")
        
        # Propose modification
        new_code = self.propose_modification(module_name, performance_context)
        if not new_code:
            logger.error("No modification proposed")
            return False
        
        # Apply with safety
        success, message = self.apply_modification(module_name, new_code)
        logger.info(message)
        
        return success
    
    def get_evolution_history(self) -> list:
        """Return list of all backups (evolution history)."""
        if not os.path.exists(self.backup_dir):
            return []
        return sorted(os.listdir(self.backup_dir), reverse=True)


# ═══════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    engine = RSIEngine()
    
    if "--analyze" in sys.argv:
        # Show current system state
        state = engine.analyze_system_state()
        print("System State:")
        for module, info in state["modules"].items():
            print(f"  {module}: {info['lines']} lines, {len(info['functions'])} functions")
            print(f"    Hash: {state['hashes'].get(module, 'N/A')}")
        
    elif "--evolve" in sys.argv:
        # Run evolution on target module
        target = sys.argv[sys.argv.index("--evolve") + 1] if len(sys.argv) > sys.argv.index("--evolve") + 1 else "regime_config.py"
        context = "Optimize for better performance. Current alpha threshold may be too aggressive."
        engine.evolve(target, context)
        
    elif "--history" in sys.argv:
        # Show evolution history
        history = engine.get_evolution_history()
        print(f"Evolution History ({len(history)} backups):")
        for h in history[:10]:
            print(f"  {h}")
    
    else:
        print("YEDAN RSI Engine - Recursive Self-Improvement")
        print("Usage:")
        print("  --analyze   Show current system state")
        print("  --evolve    Run evolution cycle on module")
        print("  --history   Show evolution backup history")
