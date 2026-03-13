"""Regression checks for Raspberry Pi installation/update behavior (Issue #92)."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def read_script(name: str) -> str:
    """Load a lifecycle shell script from the repository root."""
    return (REPO_ROOT / name).read_text(encoding="utf-8")


class TestInstallScriptRaspberryPiBehavior:
    """Guard install.sh behavior for Raspberry Pi hosts."""

    def test_install_script_detects_raspberry_pi_hosts(self):
        script = read_script("install.sh")

        assert "/proc/device-tree/model" in script
        assert 'grep -q "Raspberry Pi"' in script
        assert 'OS="raspberry-pi"' in script

    def test_install_script_uses_dependency_helper_and_pi_apt_path(self):
        script = read_script("install.sh")

        assert 'DEPENDENCY_HELPER="$SCRIPT_DIR/scripts/unix_dependency_plan.py"' in script
        assert '--raspberry-pi --emit-shell "${PLAN_FILES[@]}"' in script
        assert 'install_apt_packages "${APT_PACKAGES[@]}"' in script
        assert 'APT_PACKAGES+=("python3-pip")' in script
        assert "Falling back to pip for any remaining packages." in script

    def test_install_script_keeps_pip_path_for_non_pi_hosts(self):
        script = read_script("install.sh")

        assert 'pip install -r "$SCRIPT_DIR/requirements.txt"' in script
        assert 'pip3 install -r "$SCRIPT_DIR/requirements.txt"' in script
        assert 'pip install -r "$SCRIPT_DIR/skill/requirements.txt"' in script
        assert 'pip3 install -r "$SCRIPT_DIR/skill/requirements.txt"' in script


class TestUpdateScriptRaspberryPiBehavior:
    """Guard update.sh dependency refresh behavior for Raspberry Pi hosts."""

    def test_update_script_detects_raspberry_pi_hosts_before_dependency_refresh(self):
        script = read_script("update.sh")

        assert "/proc/device-tree/model" in script
        assert 'grep -q "Raspberry Pi"' in script
        assert 'OS="raspberry-pi"' in script
        assert 'DEPENDENCY_HELPER="$INSTALL_DIR/scripts/unix_dependency_plan.py"' in script

    def test_update_script_skips_pi_apt_refresh_by_default(self):
        script = read_script("update.sh")

        assert 'ALLOW_PI_APT_UPDATES="${MR_PUMPKIN_ALLOW_PI_APT_UPDATE:-0}"' in script
        assert 'if [ "$ALLOW_PI_APT_UPDATES" = "1" ]; then' in script
        assert "can_install_with_apt()" in script
        assert 'install_apt_packages "${APT_PACKAGES[@]}"' in script
        assert (
            "Skipping Raspberry Pi apt-managed Python packages during update to keep update.sh non-root and cron-safe"
            in script
        )
        assert 'Re-run ./install.sh or sudo apt-get install -y ${APT_PACKAGES[*]}' in script
        assert 'APT_PACKAGES+=("python3-pip")' not in script

    def test_update_script_keeps_pip_path_for_remaining_pi_requirements(self):
        script = read_script("update.sh")

        assert 'pip_args+=("--break-system-packages")' in script

    def test_update_script_keeps_pip_path_for_non_pi_hosts(self):
        script = read_script("update.sh")

        assert 'if [ "$OS" != "raspberry-pi" ]; then' in script
        assert '"$pip_cmd" install -r requirements.txt' in script
        assert 'log "WARNING: pip not found, skipping dependency install"' in script
