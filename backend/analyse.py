from config import Config
from enum import Enum

class Status(Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    LEAK = "leak"
    UNKNOWN = "unknown"

#Expert system for flow analysis
class FlowExpert:

    def __init__(self):
        self.thresholds = Config.THRESHOLDS['flow']
        self.rules = self._create_rules()
    
    def _create_rules(self):
        t = self.thresholds
        
        return [
            # Rule 1: Pump OFF, no flow = NORMAL
            {
                "name": "pump_off_normal",
                "condition": lambda f: not f['pump_on'] and f['flow'] <= t['pump_off_max'],
                "result": Status.NORMAL,
                "priority": 1
            },
            # Rule 2: Pump OFF, flow detected = LEAK
            {
                "name": "leak_detected",
                "condition": lambda f: not f['pump_on'] and f['flow'] >= t['leak_min'],
                "result": Status.LEAK,
                "priority": 3
            },
            # Rule 3: Pump ON, very low flow = CRITICAL
            {
                "name": "flow_too_low",
                "condition": lambda f: f['pump_on'] and f['flow'] < t['critical_min'],
                "result": Status.CRITICAL,
                "priority": 3
            },
            # Rule 4: Pump ON, low flow = WARNING
            {
                "name": "flow_low",
                "condition": lambda f: f['pump_on'] and t['critical_min'] <= f['flow'] < t['pump_on_min'],
                "result": Status.WARNING,
                "priority": 2
            },
            # Rule 5: Pump ON, normal flow = NORMAL
            {
                "name": "flow_normal",
                "condition": lambda f: f['pump_on'] and t['pump_on_min'] <= f['flow'] <= t['pump_on_max'],
                "result": Status.NORMAL,
                "priority": 1
            },
            # Rule 6: Pump ON, high flow = WARNING
            {
                "name": "flow_high",
                "condition": lambda f: f['pump_on'] and t['pump_on_max'] < f['flow'] <= t['critical_max'],
                "result": Status.WARNING,
                "priority": 2
            },
            # Rule 7: Pump ON, very high flow = CRITICAL
            {
                "name": "flow_too_high",
                "condition": lambda f: f['pump_on'] and f['flow'] > t['critical_max'],
                "result": Status.CRITICAL,
                "priority": 3
            }
        ]
    
    def analyze(self, flow_value, pump_on=None):
        facts = {
            'flow': flow_value,
            'pump_on': pump_on
        }
        
        # Find all matching rules
        matches = []
        for rule in self.rules:
            try:
                if rule["condition"](facts):
                    matches.append(rule)
            except Exception:
                # Skip rules that can't be evaluated
                continue
        
        if not matches:
            return Status.UNKNOWN
        
        # Return the match with highest priority
        best = max(matches, key=lambda r: r["priority"])
        return best["result"]
    
    def get_status_message(self, status, flow_value):
        messages = {
            Status.NORMAL: f"Normal operation: {flow_value} L/min",
            Status.WARNING: f"Warning: Unusual flow {flow_value} L/min",
            Status.CRITICAL: f"CRITICAL: Abnormal flow {flow_value} L/min",
            Status.LEAK: f"LEAK DETECTED: Flow {flow_value} L/min while pump OFF",
            Status.UNKNOWN: f"Unknown status: {flow_value} L/min"
        }
        return messages.get(status, f"Status: {status.value}")

# Create a single instance (singleton pattern)
_expert = FlowExpert()

def check_status(value, pump_is_on=None):
    return _expert.analyze(value, pump_is_on).value