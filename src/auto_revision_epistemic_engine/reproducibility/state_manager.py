@@ class StateManager:
         # Persist to disk
         state_file = self.state_dir / f"state_{state_id}.json"
         with open(state_file, "w") as f:
             json.dump(state.model_dump(), f, indent=2)
+        # Append to checkpoints JSONL (append-only)
+        checkpoint_file = self.state_dir / "checkpoints.jsonl"
+        with open(checkpoint_file, "a") as f:
+            f.write(json.dumps(state.model_dump()) + "\n")
 
         return state