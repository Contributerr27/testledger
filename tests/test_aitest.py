from __future__ import annotations

from pathlib import Path

from testledger.aitest import attach_mutation_scores, load_mutation_report, scan_sources
from testledger.aitest.detector import assertion_density


def test_assertion_density_java_and_python():
    java = "@Test void a(){ assertThat(x).isEqualTo(1); assertEquals(1,1);} @Test void b(){ service.run(); }"
    tests, asserts, density = assertion_density(java)
    assert tests == 2 and asserts >= 2 and density >= 1.0
    py = "def test_one():\n    assert x == 1\n\ndef test_two():\n    run()\n"
    assert assertion_density(py)[2] == 0.5


def test_scan_sources_marks_ai_and_density(tmp_path: Path):
    t = tmp_path / "src/test/java/com/acme/RecTest.java"
    t.parent.mkdir(parents=True)
    t.write_text(
        "// @ai-generated\nclass RecTest { @Test void a(){ service.run(); } @Test void b(){ x(); } }",
        encoding="utf-8",
    )
    h = tmp_path / "src/test/java/com/acme/CalcTest.java"
    h.write_text("class CalcTest { @Test void a(){ assertEquals(1,1); } }", encoding="utf-8")
    sig = scan_sources(tmp_path, ["@ai-generated"])
    assert sig["src/test/java/com/acme/RecTest.java"]["ai_generated"] is True
    assert sig["src/test/java/com/acme/RecTest.java"]["assertion_density"] == 0.0
    assert sig["src/test/java/com/acme/CalcTest.java"]["ai_generated"] is False
    attach_mutation_scores(sig, {"Rec.java": 0.3, "Calc.java": 0.9})
    assert sig["src/test/java/com/acme/RecTest.java"]["mutation_score"] == 0.3
    assert sig["src/test/java/com/acme/CalcTest.java"]["mutation_score"] == 0.9


def test_load_pit_and_stryker_reports(tmp_path: Path):
    pit = tmp_path / "mutations.xml"
    pit.write_text(
        "<mutations><mutation status='KILLED'><sourceFile>Calc.java</sourceFile></mutation>"
        "<mutation status='SURVIVED'><sourceFile>Calc.java</sourceFile></mutation>"
        "<mutation status='KILLED'><sourceFile>Calc.java</sourceFile></mutation></mutations>",
        encoding="utf-8",
    )
    assert load_mutation_report(pit) == {"Calc.java": 0.667}
    stryker = tmp_path / "mutation.json"
    stryker.write_text(
        '{"files": {"src/calc.ts": {"mutants": [{"status": "Killed"}, {"status": "Survived"}]}}}',
        encoding="utf-8",
    )
    assert load_mutation_report(stryker) == {"src/calc.ts": 0.5}
    assert load_mutation_report(tmp_path / "missing.json") == {}
