"""
파트너사 연락처 Excel → Supabase 마이그레이션 스크립트
사용법: python migrate.py
"""

import os
import uuid
import json
from datetime import datetime, timezone

try:
    import openpyxl
except ImportError:
    print("openpyxl 설치 중...")
    os.system("pip install openpyxl")
    import openpyxl

try:
    import requests
except ImportError:
    print("requests 설치 중...")
    os.system("pip install requests")
    import requests

# ────────────────────────────────────────
#  설정 (여기에 입력하세요)
# ────────────────────────────────────────
SUPABASE_URL  = "YOUR_SUPABASE_URL"       # 예) https://xxxx.supabase.co
SUPABASE_ANON = "YOUR_SUPABASE_ANON_KEY"

EXCEL_FILE = "연락처파일(거래처).xlsx"    # 엑셀 파일 경로
TABLE      = "contacts"

# 엑셀 컬럼 헤더 → DB 필드 매핑
COLUMN_MAP = {
    "업체명":   "company",
    "담당자":   "name",
    "직함":     "title",
    "전화번호": "phone",
    "이메일":   "email",
    "출처채널": "source",
    "비고":     "note",
}
# ────────────────────────────────────────


def read_excel(path: str) -> list[dict]:
    wb = openpyxl.load_workbook(path)
    ws = wb.active

    headers = []
    rows = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            headers = [str(h).strip() if h else "" for h in row]
            continue
        if all(v is None for v in row):
            continue
        record = dict(zip(headers, row))
        rows.append(record)

    print(f"헤더: {headers}")
    print(f"읽은 행 수: {len(rows)}")
    return rows, headers


def to_str(v) -> str:
    if v is None:
        return ""
    return str(v).strip()


def convert_row(raw: dict) -> dict | None:
    company = to_str(raw.get("업체명") or raw.get("company"))
    if not company:
        return None

    now = datetime.now(timezone.utc).isoformat()
    return {
        "id":         str(uuid.uuid4()),
        "company":    company,
        "name":       to_str(raw.get("담당자") or raw.get("name")),
        "title":      to_str(raw.get("직함")   or raw.get("title")),
        "phone":      to_str(raw.get("전화번호") or raw.get("phone")),
        "email":      to_str(raw.get("이메일") or raw.get("email")),
        "source":     to_str(raw.get("출처채널") or raw.get("source")),
        "note":       to_str(raw.get("비고")   or raw.get("note")),
        "created_at": now,
        "updated_at": now,
    }


def insert_batch(records: list[dict], batch_size: int = 100) -> int:
    url = f"{SUPABASE_URL}/rest/v1/{TABLE}"
    headers = {
        "apikey":        SUPABASE_ANON,
        "Authorization": f"Bearer {SUPABASE_ANON}",
        "Content-Type":  "application/json",
        "Prefer":        "return=minimal",
    }

    inserted = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        res = requests.post(url, headers=headers, data=json.dumps(batch))
        if res.status_code in (200, 201):
            inserted += len(batch)
            print(f"  ✅  {i+1}~{i+len(batch)} 행 저장 완료")
        else:
            print(f"  ❌  {i+1}~{i+len(batch)} 저장 실패: {res.status_code} {res.text[:200]}")
    return inserted


def main():
    print("=" * 50)
    print("  파트너사 연락처 마이그레이션")
    print("=" * 50)

    if SUPABASE_URL == "YOUR_SUPABASE_URL":
        print("❌  SUPABASE_URL을 설정해 주세요.")
        return

    if not os.path.exists(EXCEL_FILE):
        # 현재 디렉토리 내 xlsx 파일 자동 탐색
        candidates = [f for f in os.listdir(".") if f.endswith(".xlsx")]
        if candidates:
            print(f"현재 폴더의 xlsx 파일: {candidates}")
            alt = input("사용할 파일명을 입력하세요 (Enter=취소): ").strip()
            if not alt:
                return
            excel_path = alt
        else:
            print(f"❌  파일을 찾을 수 없습니다: {EXCEL_FILE}")
            excel_path = input("엑셀 파일 전체 경로를 입력하세요: ").strip()
            if not excel_path:
                return
    else:
        excel_path = EXCEL_FILE

    print(f"\n📂  파일 읽는 중: {excel_path}")
    rows, headers = read_excel(excel_path)

    records = []
    skipped = 0
    for raw in rows:
        converted = convert_row(raw)
        if converted:
            records.append(converted)
        else:
            skipped += 1

    print(f"\n변환 결과: {len(records)}건 (업체명 없어 제외: {skipped}건)")

    if not records:
        print("삽입할 데이터가 없습니다.")
        return

    # 미리보기
    print("\n── 미리보기 (최대 3건) ──")
    for r in records[:3]:
        print(f"  {r['company']} | {r['name']} | {r['phone']} | {r['email']}")

    confirm = input(f"\n총 {len(records)}건을 Supabase에 삽입하시겠습니까? (y/N): ").strip().lower()
    if confirm != 'y':
        print("취소되었습니다.")
        return

    print("\n📤  Supabase에 업로드 중...")
    inserted = insert_batch(records)

    print(f"\n✅  완료: {inserted}/{len(records)}건 삽입")


if __name__ == "__main__":
    main()
