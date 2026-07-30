def test_dashboard_screen(snap_compare):
    assert snap_compare("../certifyai/tui/app.py", terminal_size=(120, 50))

def test_run_attack_screen(snap_compare):
    # "r" triggers action_switch_tab("run") per BINDINGS
    assert snap_compare("../certifyai/tui/app.py", press=["r"], terminal_size=(120, 50))

def test_results_screen(snap_compare):
    # "t" triggers action_switch_tab("results") per BINDINGS
    assert snap_compare("../certifyai/tui/app.py", press=["t"], terminal_size=(120, 50))

def test_settings_screen(snap_compare):
    # "s" triggers action_switch_tab("settings") per BINDINGS
    assert snap_compare("../certifyai/tui/app.py", press=["s"], terminal_size=(120, 50))