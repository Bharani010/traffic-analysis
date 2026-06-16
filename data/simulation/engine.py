"""
Simulation orchestration engine.

Orchestrates the generation of users, sessions, and events at scale,
injecting attacks according to configured ratios, and saving output.
"""

import math
import random
from datetime import datetime, timedelta

import pandas as pd
from pyspark.sql import SparkSession

from data.simulation import ATTACK_TYPES, SimulationConfig
from data.simulation.generator import EventGenerator
from data.simulation.models import TrafficEvent
from data.simulation.profiles import (
    create_sessions_for_user,
    create_user_population,
)


class SimulationEngine:
    """Orchestrates traffic simulation and attack injection."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.rng = random.Random(config.seed)
        self.generator = EventGenerator(self.rng)
        
        # Calculate attack targets based on config ratios
        self.attack_targets = {
            attack_key: int(config.total_events * data["ratio"])
            for attack_key, data in ATTACK_TYPES.items()
        }
        self.attacks_generated = {k: 0 for k in ATTACK_TYPES.keys()}
        self.total_generated = 0
        
    def _needs_attack(self, attack_key: str) -> bool:
        return self.attacks_generated[attack_key] < self.attack_targets[attack_key]

    def _generate_batch(self, batch_size: int, start_time: datetime) -> list[dict]:
        """Generate a batch of events."""
        events: list[TrafficEvent] = []
        
        # 1. Generate user population for this batch
        # We don't generate the full population at once to save memory. 
        # But for consistency, we'll generate a subset of users.
        num_users_batch = max(1, int(self.config.num_users * (batch_size / self.config.total_events)))
        users = create_user_population(num_users_batch, rng=self.rng)
        
        current_time = start_time
        
        # Loop until batch is full
        while len(events) < batch_size:
            # Pick a random user
            user = self.rng.choice(users)
            
            # Decide what to do: normal session or attack
            if self._needs_attack("credential_stuffing") and self.rng.random() < 0.05:
                count = min(100, self.attack_targets["credential_stuffing"] - self.attacks_generated["credential_stuffing"])
                new_events = list(self.generator.inject_credential_stuffing(current_time, count, []))
                events.extend(new_events)
                self.attacks_generated["credential_stuffing"] += len(new_events)
                
            elif self._needs_attack("brute_force") and self.rng.random() < 0.05:
                count = min(50, self.attack_targets["brute_force"] - self.attacks_generated["brute_force"])
                new_events = list(self.generator.inject_brute_force(user, current_time, count))
                events.extend(new_events)
                self.attacks_generated["brute_force"] += len(new_events)
                
            elif self._needs_attack("bot_crawling") and self.rng.random() < 0.05:
                count = min(200, self.attack_targets["bot_crawling"] - self.attacks_generated["bot_crawling"])
                new_events = list(self.generator.inject_bot_crawling(current_time, count))
                events.extend(new_events)
                self.attacks_generated["bot_crawling"] += len(new_events)
                
            elif self._needs_attack("api_abuse") and self.rng.random() < 0.05:
                count = min(150, self.attack_targets["api_abuse"] - self.attacks_generated["api_abuse"])
                new_events = list(self.generator.inject_api_abuse(user, current_time, count))
                events.extend(new_events)
                self.attacks_generated["api_abuse"] += len(new_events)
                
            elif self._needs_attack("ddos_burst") and self.rng.random() < 0.05:
                count = min(500, self.attack_targets["ddos_burst"] - self.attacks_generated["ddos_burst"])
                new_events = list(self.generator.inject_ddos_burst(current_time, count))
                events.extend(new_events)
                self.attacks_generated["ddos_burst"] += len(new_events)
                
            elif self._needs_attack("geo_account_takeover") and self.rng.random() < 0.05:
                count = min(10, self.attack_targets["geo_account_takeover"] - self.attacks_generated["geo_account_takeover"])
                new_events = list(self.generator.inject_geo_takeover(user, current_time, count))
                events.extend(new_events)
                self.attacks_generated["geo_account_takeover"] += len(new_events)
                
            elif self._needs_attack("session_hijacking") and self.rng.random() < 0.05:
                sessions = create_sessions_for_user(user, 1, self.rng)
                if sessions:
                    count = min(20, self.attack_targets["session_hijacking"] - self.attacks_generated["session_hijacking"])
                    new_events = list(self.generator.inject_session_hijacking(sessions[0], current_time, count))
                    events.extend(new_events)
                    self.attacks_generated["session_hijacking"] += len(new_events)
                    
            else:
                # Normal Session
                sessions = create_sessions_for_user(user, 1, self.rng)
                for session in sessions:
                    new_events = list(self.generator.generate_normal_session(session, current_time))
                    events.extend(new_events)

            # Advance time slightly to spread out sessions
            current_time += timedelta(minutes=self.rng.randint(1, 15))
            
        # Return exactly batch_size (truncate if we overshot)
        return [e.to_dict() for e in events[:batch_size]]

    def run(self, spark: SparkSession) -> pd.DataFrame:
        """Run the simulation engine and return PySpark DataFrame."""
        print(f"Starting simulation for {self.config.total_events} events...")
        print(f"Attack targets: {self.attack_targets}")
        
        batches = math.ceil(self.config.total_events / self.config.batch_size)
        start_time = datetime.now() - timedelta(days=self.config.time_span_days)
        
        all_data = []
        
        for i in range(batches):
            remaining = self.config.total_events - self.total_generated
            current_batch_size = min(self.config.batch_size, remaining)
            
            print(f"Generating batch {i+1}/{batches} ({current_batch_size} events)...")
            batch_data = self._generate_batch(current_batch_size, start_time)
            
            # Append to list. (For a truly massive dataset, we would write directly to disk per batch.
            # Using Pandas DataFrame for intermediate aggregation since 1M rows is fine in memory)
            all_data.extend(batch_data)
            self.total_generated += len(batch_data)
            
            # Advance start time for next batch
            time_advance_per_batch = timedelta(days=self.config.time_span_days) / batches
            start_time += time_advance_per_batch

        print(f"Simulation complete. Generated {self.total_generated} events.")
        print(f"Final attack counts: {self.attacks_generated}")
        
        return pd.DataFrame(all_data)
