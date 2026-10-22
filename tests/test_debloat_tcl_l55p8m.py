"""Validate debloat_tcl_l55p8m.txt against this unit's real inventory, offline.

The list is checked against the 149 packages `pm list packages` reported on the
TCL L55P8M (retail name; the unit reports "BeyondTV") and against its own
"Deliberately NOT disabled" block. No TV is contacted and no network is used.

Run from the repository root:
    python -m unittest discover -s tests -p "test_debloat_tcl_l55p8m.py" -v
"""
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIST = ROOT / "debloat_tcl_l55p8m.txt"
PACKAGE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$")
# A kept line is a comment of the form "# <package>   # <reason>": the first hash opens the
# comment, the second one separates the package from its reason.
KEPT_LINE = re.compile(r"^#\s+([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+)\s+#")

# Frozen counts for this exact unit: 40 packages to disable, 44 deliberately kept.
EXPECTED_ACTIVE = 40
EXPECTED_KEPT = 44
# `pm list packages` on the unit at 192.168.100.2, 149 lines of "package:<name>".
EXPECTED_INVENTORY = 149

INVENTORY = """\
com.android.cts.priv.ctsshim
com.google.android.ext.services
com.google.android.apps.mediashell
de.blinkt.openvpn
com.google.android.katniss
com.tcl.esticker
com.android.dynsystem
uk.co.freeview.mdsclient
com.tcl.initsetup
com.android.providers.calendar
com.android.tv.settings
com.tcl.tvinput
uk.co.freeview.amc_catchup
com.android.providers.media
com.google.android.onetimeinitializer
com.google.android.ext.shared
uk.co.freeview.onnow
com.tcl.factory.view
au.com.stan.and
com.android.externalstorage
uk.co.freeview.uktv
com.directv.dtvlatam
com.android.htmlviewer
com.android.companiondevicemanager
com.android.providers.downloads
com.android.providers.tv
com.android.networkstack.inprocess
com.google.android.backdrop
com.android.tv.settings.gms.resoverlay
com.tcl.useragreement
com.tcl.miracast
com.google.android.tungsten.setupwraith
com.saltamontes.app
com.tcl.gallery
com.google.android.overlay.modules.permissioncontroller
com.android.vending
com.android.pacprocessor
uk.co.freeview.fvpconfigauth
com.google.android.youtube.tvkids
com.android.certinstaller
com.google.android.marvin.talkback
android
com.xuper.netxxus
com.tcl.browser
uk.co.freeview.systemdistributor
com.tcl.inputmethod.international
uk.co.freeview.bbc_sounds
com.android.backupconfirm
com.tcl.xian.StartandroidService
com.tvos
com.espn.score_center
com.tcl.overlay.systemui
com.tcl.guard
com.android.statementservice
com.android.settings.intelligence
com.google.android.permissioncontroller
com.tcl.videocall
com.amazon.amazonvideo.livingroom
com.tcl.tv.tclhome_master
com.android.providers.settings
com.tcl.versionUpdateApp
com.android.sharedstoragebackup
uk.co.freeview.tifbridge
com.tcl.waterfall.overseas
com.google.android.music
com.android.printspooler
com.tcl.assistant
com.android.dreams.basic
com.google.android.overlay.modules.ext.services
com.tcl.copydatatotv
com.tcl.micmanager
com.android.se
com.android.inputdevices
com.tcl.notereminder
com.google.android.tvrecommendations
com.disney.starplus
uk.co.freeview.explore
com.tcl.MultiScreenInteraction_TV
com.google.android.modulemetadata
com.google.android.tvlauncher
com.google.android.webview
com.android.keychain
com.google.android.youtube.tvmusic
com.hbo.hbonow
com.google.android.packageinstaller
com.google.android.gms
com.google.android.gsf
com.google.android.tts
com.android.wifi.resources
com.google.android.partnersetup
com.android.localtransport
com.google.android.videos
com.tcl.systemserver
com.tcl.partnercustomizer
com.android.proxyhandler
com.google.android.overlay.modules.permissioncontroller.forframework
com.google.android.feedback
com.google.android.syncadapters.calendar
android.autoinstalls.config.tcl.device
com.android.soundpicker
tv.wuaki.apptv
uk.co.freeview.bbc
uk.co.freeview.ch5
uk.co.freeview.itv
uk.co.freeview.stv
com.android.tethering.overlay
uk.co.freeview.amc_horror
com.tcl.tv.tclhome_passive
com.tcl.keycustomfunctionservice
com.android.wallpaper.livepicker
com.yablio.sendfilestotv
com.tcl.providers.config
com.tcl.usercenter
com.google.android.apps.nbu.smartconnect.tv
com.android.networkstack.tethering.inprocess
com.android.networkstack.permissionconfig
com.tcl.bi
com.tcl.tv
com.tcl.overseasappshow
com.google.android.sss.authbridge
com.android.cts.ctsshim
com.google.android.overlay.modules.modulemetadata.forframework
com.tcl.settings
com.tcl.autopair
com.google.android.youtube.tv
com.android.vpndialogs
com.tcl.smartalexa
com.google.android.tv.frameworkpackagestubs
com.tcl.ui_mediaCenter
com.android.shell
com.android.wallpaperbackup
com.android.providers.userdictionary
com.android.providers.media.module
com.tcl.messagebox
ar.com.flow.androidtv
com.android.hotspot2.osulogin
com.google.android.tv.assistant
com.google.android.tv.remote.service
com.android.location.fused
com.android.systemui
com.google.android.play.games
com.netflix.ninja
com.android.bluetooth
com.android.providers.contacts
com.android.captiveportallogin
com.disney.disneyplus
uk.co.freeview.ch4_vod
com.android.tethering.overlay.gsi
com.google.android.inputmethod.latin
"""

INVENTORY_SET = frozenset(INVENTORY.split())

# Load-bearing packages: they stay enabled on this unit, so they belong to the kept block and
# must never show up as an active entry.
SAFETY_KEPT = (
    "com.tcl.tv",
    "com.tcl.tvinput",
    "com.tcl.keycustomfunctionservice",
    "com.tcl.partnercustomizer",
    "com.tcl.guard",
    "com.tcl.autopair",
    "com.tcl.useragreement",
    "com.tcl.settings",
    "com.tcl.systemserver",
    "com.tcl.micmanager",
    "com.tcl.xian.StartandroidService",
    "com.tcl.initsetup",
    "com.tcl.factory.view",
    "com.tcl.providers.config",
    "com.tcl.browser",
    "com.tcl.miracast",
    "com.tcl.MultiScreenInteraction_TV",
    "com.google.android.apps.mediashell",
    "com.google.android.tv.remote.service",
    "com.google.android.tungsten.setupwraith",
    "com.android.vending",
    "com.android.tv.settings",
    "com.android.dreams.basic",
    "com.google.android.youtube.tv",
    "com.netflix.ninja",
    "com.amazon.amazonvideo.livingroom",
    "com.android.pacprocessor",
    "com.tcl.inputmethod.international",
    "com.tcl.ui_mediaCenter",
)

HOME_CLAIMANTS = (
    "com.google.android.tvlauncher/.MainActivity",
    "com.tcl.keycustomfunctionservice/.FallbackHome",
    "com.android.tv.settings/.system.FallbackHome",
)


def list_lines():
    """Lines of the list under test, newline-normalised."""
    return LIST.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")


def active_entries(lines):
    """(line number, package, reason) for every active entry.

    An entry is any line whose body -- everything before the first "#" -- is non-empty, the same
    criterion tests/test_examples.py uses. Comment and blank lines are not entries.
    """
    entries = []
    for n, line in enumerate(lines, 1):
        if "#" in line:
            body, _, reason = line.partition("#")
        else:
            body, reason = line, ""
        body = body.strip()
        if not body:
            continue
        entries.append((n, body, reason.strip()))
    return entries


def kept_entries(lines):
    """(line number, package) for the "Deliberately NOT disabled" block only.

    The block runs from its header to the first blank line, so the separately commented
    "Optional (commented out)" section is not mistaken for kept packages.
    """
    start = None
    for i, line in enumerate(lines):
        if "Deliberately NOT disabled" in line:
            start = i
            break
    if start is None:
        raise AssertionError("the 'Deliberately NOT disabled' block header is missing from the list")
    entries = []
    for n, line in enumerate(lines[start + 1:], start + 2):
        if not line.strip():
            break
        m = KEPT_LINE.match(line)
        if m:
            entries.append((n, m.group(1)))
    return entries


class DebloatTclL55P8MTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lines = list_lines()
        cls.text = "\n".join(cls.lines)
        cls.active = active_entries(cls.lines)
        cls.kept = kept_entries(cls.lines)
        cls.active_names = [pkg for _, pkg, _ in cls.active]
        cls.kept_names = [pkg for _, pkg in cls.kept]

    # --- 1. header ---------------------------------------------------------------
    def test_first_line_names_the_tv(self):
        first = self.lines[0]
        self.assertTrue(first.startswith("#"),
                        f"first line must be a comment naming the TV, got {first!r}")
        self.assertIn("TCL L55P8M", first,
                      f"first line must name the TV (TCL L55P8M), got {first!r}")

    # --- 2. package-name syntax ---------------------------------------------------
    def test_every_active_entry_is_a_package_name(self):
        self.assertTrue(self.active, "the list has no active entries at all")
        for n, body, _ in self.active:
            with self.subTest(line=n, entry=body):
                self.assertRegex(body, PACKAGE,
                                 f"line {n}: not a package name: {body!r}")

    # --- 3. no duplicate active entries -------------------------------------------
    def test_no_duplicate_active_entries(self):
        dupes = sorted({p for p in self.active_names if self.active_names.count(p) > 1})
        lines_by_pkg = {}
        for n, p, _ in self.active:
            lines_by_pkg.setdefault(p, n)
        self.assertFalse(dupes,
                         f"active entries listed twice (first at line "
                         f"{[lines_by_pkg[p] for p in dupes]}): {dupes}")

    # --- 4. every active entry carries a reason ------------------------------------
    def test_every_active_entry_has_a_reason(self):
        for n, pkg, reason in self.active:
            with self.subTest(line=n, entry=pkg):
                self.assertIn("#", self.lines[n - 1],
                              f"line {n}: {pkg} has no '#' reason separator")
                self.assertTrue(reason,
                                f"line {n}: {pkg} has an empty reason after '#'")

    # --- 5. frozen counts ----------------------------------------------------------
    def test_frozen_counts(self):
        self.assertEqual(
            len(self.active), EXPECTED_ACTIVE,
            f"expected {EXPECTED_ACTIVE} active entries for this unit, found "
            f"{len(self.active)}: {self.active_names}")
        self.assertEqual(
            len(self.kept), EXPECTED_KEPT,
            f"expected {EXPECTED_KEPT} kept entries in the 'Deliberately NOT disabled' "
            f"block, found {len(self.kept)}: {self.kept_names}")

    # --- 6. every active entry exists on the real unit ------------------------------
    def test_active_entries_exist_in_the_real_inventory(self):
        self.assertEqual(
            len(INVENTORY_SET), EXPECTED_INVENTORY,
            f"embedded inventory constant must hold {EXPECTED_INVENTORY} package names, "
            f"holds {len(INVENTORY_SET)}")
        for n, pkg, _ in self.active:
            with self.subTest(line=n, entry=pkg):
                self.assertIn(pkg, INVENTORY_SET,
                              f"line {n}: {pkg} is not installed on this unit "
                              f"(absent from the {EXPECTED_INVENTORY}-package inventory)")

    # --- 7. active and kept are disjoint --------------------------------------------
    def test_active_and_kept_are_disjoint(self):
        both = sorted(set(self.active_names) & set(self.kept_names))
        self.assertFalse(
            both,
            f"packages are both disabled and deliberately kept: {both} "
            f"(active line {[n for n, p, _ in self.active if p in both]}, "
            f"kept line {[n for n, p in self.kept if p in both]})")

    # --- 8. no duplicate kept entries ------------------------------------------------
    def test_no_duplicate_kept_entries(self):
        dupes = sorted({p for p in self.kept_names if self.kept_names.count(p) > 1})
        lines_by_pkg = {}
        for n, p in self.kept:
            lines_by_pkg.setdefault(p, n)
        self.assertFalse(dupes,
                         f"kept entries listed twice (first at line "
                         f"{[lines_by_pkg[p] for p in dupes]}): {dupes}")

    # --- 9. kept block mirrors the real unit ------------------------------------------
    def test_kept_entries_exist_in_the_real_inventory(self):
        self.assertTrue(self.kept, "the 'Deliberately NOT disabled' block has no entries")
        for n, pkg in self.kept:
            with self.subTest(line=n, entry=pkg):
                self.assertIn(pkg, INVENTORY_SET,
                              f"line {n}: kept entry {pkg} is not installed on this unit; "
                              f"the kept block must document the real inventory")

    # --- 10. apply / undo documented ----------------------------------------------------
    def test_header_documents_apply_and_undo(self):
        self.assertIn("tools\\disable.ps1", self.text,
                      "the header must document the apply path: tools\\disable.ps1")
        self.assertIn("tools\\restore.ps1", self.text,
                      "the header must document the undo path: tools\\restore.ps1")

    # --- 11. the three HOME claimants ----------------------------------------------------
    def test_header_names_the_three_home_claimants(self):
        for claimant in HOME_CLAIMANTS:
            with self.subTest(claimant=claimant):
                self.assertIn(claimant, self.text,
                              f"the header must name the HOME claimant {claimant}")

    # --- 12. launcher handled separately, overseasappshow must be disabled -----------------
    def test_launcher_is_not_active_and_overseasappshow_is(self):
        self.assertNotIn(
            "com.google.android.tvlauncher", self.active_names,
            "com.google.android.tvlauncher must NOT be an active entry: it is disabled "
            "separately, only after CleanYourTV owns Home")
        self.assertIn(
            "com.tcl.overseasappshow", self.active_names,
            "com.tcl.overseasappshow must be an active entry: its BootReceiver re-enables "
            "promo packages on every boot")

    # --- 13. safety set never disabled ------------------------------------------------------
    def test_safety_set_stays_enabled(self):
        for pkg in SAFETY_KEPT:
            with self.subTest(pkg=pkg):
                self.assertIn(
                    pkg, self.kept_names,
                    f"load-bearing {pkg} must appear in the 'Deliberately NOT disabled' block")
                self.assertNotIn(
                    pkg, self.active_names,
                    f"load-bearing {pkg} must never be an active entry: disabling it breaks "
                    f"the TV")


if __name__ == "__main__":
    unittest.main()
