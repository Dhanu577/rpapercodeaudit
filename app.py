"""Streamlit human-review UI. Run: streamlit run app.py"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from rpapercodeaudit.export import export_csv, export_xlsx
from rpapercodeaudit.schema import SCHEMA_FIELDS, VERDICTS

st.set_page_config(page_title="RPaperCodeAudit", layout="wide")
st.title("RPaperCodeAudit — human review")
st.caption("All imported verdicts remain drafts until you tick Checked by me. This tool does not present automatic findings as final.")
config_path=Path("config.json")
config=json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {"issue_categories":["other"]}
if "records" not in st.session_state: st.session_state.records=[]
upload=st.file_uploader("Load pipeline results.json", type=["json"])
if upload:
    data=json.loads(upload.getvalue().decode("utf-8")); st.session_state.records=data.get("records", data.get("accepted", []))
records=st.session_state.records
if not records:
    st.info("Load a pipeline results.json or enter a pipeline output directory below.")
    directory=st.text_input("Pipeline output directory", "outputs")
    result_path=Path(directory)/"results.json"
    if st.button("Load directory") and result_path.exists():
        data=json.loads(result_path.read_text(encoding="utf-8")); st.session_state.records=data.get("records", [])
        st.rerun()
else:
    edited=[]
    for i, row in enumerate(records):
        st.divider(); left,right=st.columns(2)
        with left: st.markdown("**Paper sentence**"); st.write(row.get("paper_sentence", row.get("verbatim_sentence", ""))); st.caption(row.get("paper_section", ""))
        with right: st.markdown("**Code excerpt**"); st.code(row.get("code_excerpt", "") or "No validated location", language="r")
        row=dict(row); row["verdict"]=st.selectbox("Verdict", VERDICTS, index=VERDICTS.index(row.get("verdict", "not verified")) if row.get("verdict") in VERDICTS else 4, key=f"v{i}")
        row["issue_category"]=st.selectbox("Issue category", config.get("issue_categories", ["other"]), index=(config.get("issue_categories", ["other"]).index(row.get("issue_category")) if row.get("issue_category") in config.get("issue_categories", ["other"]) else 0), key=f"c{i}")
        row["notes"]=st.text_area("Notes", row.get("notes", ""), key=f"n{i}")
        row["checked_by_me"]=st.checkbox("Checked by me", value=bool(row.get("checked_by_me", False)), key=f"x{i}")
        if not row["checked_by_me"]: row["notes"]="DRAFT - unverified: "+row["notes"].removeprefix("DRAFT - unverified: ")
        edited.append(row)
    st.session_state.records=edited
    if st.button("Save progress"):
        Path("outputs").mkdir(exist_ok=True); Path("outputs/review_progress.json").write_text(json.dumps(edited,indent=2),encoding="utf-8"); st.success("Progress saved.")
    if st.button("Export reviewed rows"):
        from rpapercodeaudit.schema import ClaimRecord
        normalized=[ClaimRecord(**{field: row.get(field, "") if field != "checked_by_me" else bool(row.get(field, False)) for field in SCHEMA_FIELDS}) for row in edited]
        export_csv(normalized,"outputs/reviewed_claims.csv"); export_xlsx(normalized,"outputs/reviewed_claims.xlsx"); st.success("CSV and XLSX exported to outputs/.")
