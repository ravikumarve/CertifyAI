export interface DashboardData {
  stats: {
    score: number | null;
    passed: number;
    failed: number;
    total: number;
    all_time_passed: number;
    all_time_total: number;
    running_time_secs: number;
    last_run_id: string | null;
    provider: string;
    model: string;
    frameworks: string[];
    engine_status: string;
    vault_status: string;
    version: string;
  };
  current_run: {
    id: string;
    provider: string;
    model: string;
    frameworks: string[];
    concurrency: number;
    status: string;
    elapsed_secs: number;
  } | null;
  recent_results: AttackResult[];
  vault_log: VaultEntry[];
}

export interface AttackResult {
  id: string;
  run_id: string;
  scenario_id: string;
  attack_name: string;
  category: string;
  severity: string;
  status: string;
  response_time_ms: number | null;
  framework?: string;
  evaluation?: string;
}

export interface VaultEntry {
  id: string;
  run_id: string;
  hash: string;
  previous_hash: string;
  timestamp: string;
  message: string;
  level: string;
  verified_at: string | null;
}

export interface RunSummary {
  id: string;
  status: string;
  passed: number;
  failed: number;
  errors: number;
  skipped: number;
  total: number;
  score: number | null;
  created_at: string;
  provider: string;
  model: string;
  engine_version?: string;
}
