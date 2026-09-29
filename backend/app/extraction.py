import os,json,base64
import httpx
SCHEMA={"document_type":"po|delivery_note|invoice|quotation|grn|rejection_note|supplier_message|unknown","po_number":"string|null","supplier_name":"string|null","promised_delivery_date":"YYYY-MM-DD|null","actual_delivery_date":"YYYY-MM-DD|null","gstin":"string|null","hsn_code":"string|null","items":[{"description":"string","quantity":"number","unit":"string","unit_price":"number"}],"confidence":"number"}
async def extract_with_provider(path):
    if os.getenv("OPENAI_API_KEY"): return await openai_extract(path)
    if os.getenv("GEMINI_API_KEY"): return {"document_type":"unknown","confidence":0.0,"note":"Gemini key detected; provider adapter not enabled until its response contract is verified."}
    return {"document_type":"unknown","confidence":0.0,"items":[],"note":"No AI provider configured"}
async def openai_extract(path):
    from pathlib import Path
    data=base64.b64encode(Path(path).read_bytes()).decode()
    prompt="Extract the document into this JSON schema. Do not invent missing values. Return JSON only: "+json.dumps(SCHEMA)
    payload={"model":os.getenv("OPENAI_MODEL","gpt-4o-mini"),"input":[{"role":"user","content":[{"type":"input_text","text":prompt},{"type":"input_file","filename":Path(path).name,"file_data":"data:application/octet-stream;base64,"+data}]}]}
    async with httpx.AsyncClient(timeout=90) as client:
        r=await client.post("https://api.openai.com/v1/responses",headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"]},json=payload)
        r.raise_for_status()
        return {"provider":"openai","raw":r.json()}
