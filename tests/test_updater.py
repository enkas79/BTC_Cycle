from btc_cycle import updater


def test_versions():
    assert updater.is_newer("v1.0.1", "1.0.0")
    assert not updater.is_newer("1.0.0", "1.0.0")
    assert updater.is_newer("1.10.0", "1.9.9")
    assert updater.parse_version("2") == (2, 0, 0)


def test_select_asset():
    assets = [{"name": n, "url": n} for n in
              ("BTC_Cycle-Setup-1.0.1.exe", "BTC_Cycle-1.0.1-macos.zip",
               "BTC_Cycle-1.0.1-linux.tar.gz")]
    assert updater.select_asset(assets, "win32")["name"].endswith(".exe")
    assert updater.select_asset(assets, "darwin")["name"].endswith("macos.zip")
    assert updater.select_asset(assets, "linux")["name"].endswith(".tar.gz")
    assert updater.select_asset([], "linux") is None
