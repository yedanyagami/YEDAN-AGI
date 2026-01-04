"""
YEDAN AGI - Liquidity Manager
Controls Uniswap V3 / Orca LP NFT Positions
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

# Uniswap V3 Position NFT ABI (minimal for read/write)
UNISWAP_V3_POSITION_ABI = [
    {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "positions", "outputs": [
        {"name": "nonce", "type": "uint96"},
        {"name": "operator", "type": "address"},
        {"name": "token0", "type": "address"},
        {"name": "token1", "type": "address"},
        {"name": "fee", "type": "uint24"},
        {"name": "tickLower", "type": "int24"},
        {"name": "tickUpper", "type": "int24"},
        {"name": "liquidity", "type": "uint128"},
        {"name": "feeGrowthInside0LastX128", "type": "uint256"},
        {"name": "feeGrowthInside1LastX128", "type": "uint256"},
        {"name": "tokensOwed0", "type": "uint128"},
        {"name": "tokensOwed1", "type": "uint128"}
    ], "stateMutability": "view", "type": "function"},
    {"inputs": [{"components": [
        {"name": "tokenId", "type": "uint256"},
        {"name": "liquidity", "type": "uint128"},
        {"name": "amount0Min", "type": "uint256"},
        {"name": "amount1Min", "type": "uint256"},
        {"name": "deadline", "type": "uint256"}
    ], "name": "params", "type": "tuple"}], "name": "decreaseLiquidity", "outputs": [
        {"name": "amount0", "type": "uint256"},
        {"name": "amount1", "type": "uint256"}
    ], "stateMutability": "nonpayable", "type": "function"}
]

# Uniswap V3 addresses
UNISWAP_V3_POSITION_MANAGER = {
    "ethereum": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
    "arbitrum": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
    "polygon": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
    "base": "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1"
}


class LiquidityManager:
    """Controls Uniswap V3 / Orca LP NFT Positions"""
    
    def __init__(self, chain="ethereum"):
        self.chain = chain
        self.rpc_url = os.getenv(f"{chain.upper()}_RPC_URL")
        self.private_key = os.getenv(f"{chain.upper()}_PRIVATE_KEY")
        self.positions = {}  # Cache of monitored positions
        
        # Initialize web3 if available
        try:
            from web3 import Web3
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url)) if self.rpc_url else None
            if self.w3 and self.w3.is_connected():
                print(f"[LIQUIDITY] Connected to {chain}")
            else:
                self.w3 = None
        except ImportError:
            self.w3 = None
            print("[LIQUIDITY] web3 not installed, running in simulation mode")
    
    def get_position(self, token_id: int) -> dict:
        """Read position data from NFT"""
        if not self.w3:
            return self._simulate_position(token_id)
        
        try:
            manager = self.w3.eth.contract(
                address=UNISWAP_V3_POSITION_MANAGER.get(self.chain),
                abi=UNISWAP_V3_POSITION_ABI
            )
            pos = manager.functions.positions(token_id).call()
            return {
                "token_id": token_id,
                "token0": pos[2],
                "token1": pos[3],
                "fee": pos[4],
                "tick_lower": pos[5],
                "tick_upper": pos[6],
                "liquidity": pos[7],
                "fees_owed_0": pos[10],
                "fees_owed_1": pos[11],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[LIQUIDITY] Error reading position: {e}")
            return {}
    
    def _simulate_position(self, token_id: int) -> dict:
        """Simulate position for testing"""
        return {
            "token_id": token_id,
            "token0": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
            "token1": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
            "fee": 3000,  # 0.3%
            "tick_lower": -887220,
            "tick_upper": 887220,
            "liquidity": 1000000000000,
            "fees_owed_0": 1000000000000000,  # ~0.001 ETH
            "fees_owed_1": 5000000,  # ~5 USDC
            "price_lower": 1500,
            "price_upper": 2500,
            "current_price": 2000,
            "simulated": True
        }
    
    def calculate_il(self, entry_price: float, current_price: float, range_low: float, range_high: float) -> float:
        """
        Calculate Impermanent Loss for concentrated liquidity.
        Returns IL as decimal (0.05 = 5% loss).
        """
        import math
        
        # If price outside range, position is 100% one asset
        if current_price <= range_low or current_price >= range_high:
            # Full IL - calculate based on price move
            price_ratio = current_price / entry_price
            hold_value = (1 + price_ratio) / 2  # 50/50 hold
            lp_value = math.sqrt(price_ratio)    # LP value
            return (hold_value - lp_value) / hold_value
        
        # Within range - use concentrated liquidity IL formula
        sqrt_entry = math.sqrt(entry_price)
        sqrt_current = math.sqrt(current_price)
        sqrt_low = math.sqrt(range_low)
        sqrt_high = math.sqrt(range_high)
        
        # Simplified IL for concentrated positions
        price_ratio = current_price / entry_price
        il = 2 * math.sqrt(price_ratio) / (1 + price_ratio) - 1
        
        return abs(il)
    
    def calculate_fee_apr(self, position: dict, value_usd: float, days: int = 7) -> float:
        """Estimate APR from fee earnings"""
        # Simplified: assume fees_owed accumulated over `days`
        fees_usd = position.get("fees_owed_1", 0) / 1e6  # USDC decimals
        if value_usd <= 0:
            return 0
        
        daily_return = fees_usd / days / value_usd
        apr = daily_return * 365 * 100
        return apr
    
    def should_rebalance(self, position: dict, current_price: float, threshold: float = 0.1) -> tuple:
        """
        Determine if position should be rebalanced.
        Returns (should_rebalance: bool, reason: str)
        """
        range_low = position.get("price_lower", 0)
        range_high = position.get("price_upper", 0)
        
        if range_low == 0 or range_high == 0:
            return False, "Invalid range"
        
        # Check if price near edge
        range_size = range_high - range_low
        buffer = range_size * threshold
        
        if current_price <= range_low + buffer:
            return True, f"Price {current_price} near lower edge {range_low}"
        if current_price >= range_high - buffer:
            return True, f"Price {current_price} near upper edge {range_high}"
        
        return False, "Price within safe zone"
    
    def find_golden_range(self, current_price: float, volatility: float = 0.05) -> tuple:
        """
        Find optimal 1% concentrated range based on volatility.
        Returns (range_low, range_high)
        """
        # Golden range = current_price ± (volatility * multiplier)
        range_width = current_price * volatility
        range_low = current_price - range_width
        range_high = current_price + range_width
        return range_low, range_high
    
    def remove_liquidity(self, token_id: int, amount_percent: float = 100) -> dict:
        """Remove liquidity from position (requires signing)"""
        if not self.w3 or not self.private_key:
            return {"success": False, "simulated": True, "message": "Would remove liquidity"}
        
        # Implementation would use decreaseLiquidity + collect
        return {"success": False, "error": "Not implemented - requires production setup"}
    
    def mint_position(self, token0: str, token1: str, fee: int, tick_lower: int, tick_upper: int, amount0: int, amount1: int) -> dict:
        """Mint new LP position (requires signing)"""
        if not self.w3 or not self.private_key:
            return {"success": False, "simulated": True, "message": "Would mint new position"}
        
        # Implementation would use mint function
        return {"success": False, "error": "Not implemented - requires production setup"}
    
    def rebalance(self, token_id: int, new_range_low: float, new_range_high: float) -> dict:
        """Full rebalance cycle: Remove → Swap → Mint"""
        position = self.get_position(token_id)
        
        steps = []
        steps.append({"step": "remove", "result": self.remove_liquidity(token_id)})
        steps.append({"step": "calculate_swap", "message": "Would swap to 50/50 ratio"})
        steps.append({"step": "mint", "message": f"Would mint at {new_range_low}-{new_range_high}"})
        
        return {
            "success": True,
            "simulated": True,
            "token_id": token_id,
            "new_range": [new_range_low, new_range_high],
            "steps": steps,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    lm = LiquidityManager(chain="ethereum")
    
    # Test position read
    pos = lm.get_position(12345)
    print(f"Position: {json.dumps(pos, indent=2)}")
    
    # Test IL calculation
    il = lm.calculate_il(entry_price=2000, current_price=2200, range_low=1800, range_high=2200)
    print(f"Impermanent Loss: {il*100:.2f}%")
    
    # Test rebalance check
    should, reason = lm.should_rebalance(pos, current_price=2180)
    print(f"Should rebalance: {should} - {reason}")
    
    # Test golden range
    low, high = lm.find_golden_range(current_price=2000, volatility=0.03)
    print(f"Golden Range: ${low:.2f} - ${high:.2f}")
