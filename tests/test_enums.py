from __future__ import annotations

from fredtools.ENUMS import TagGroups


def test_tag_groups_values() -> None:
    assert TagGroups.FREQ.value == ("freq", "Frequency")
    assert TagGroups.CC.value == ("cc", "Citation & Copyright")
