# 파트너사 연락처 웹앱 — 설정 가이드

## 1. Supabase 프로젝트 생성

1. https://supabase.com 에서 무료 계정 생성 후 로그인
2. **New Project** 클릭 → 프로젝트 이름 입력 (예: `partner-contacts`)
3. 데이터베이스 비밀번호 설정 후 가장 가까운 Region 선택 (Northeast Asia 추천)
4. 프로젝트 생성 완료까지 약 1~2분 대기

## 2. contacts 테이블 생성

Supabase 대시보드 → **SQL Editor** → New Query → 아래 SQL 붙여넣기 후 실행:

```sql
create table contacts (
  id          uuid primary key default gen_random_uuid(),
  company     text not null,
  name        text,
  title       text,
  phone       text,
  email       text,
  source      text,
  note        text,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

-- 전체 접근 허용 (팀 내부 사용 목적)
alter table contacts enable row level security;
create policy "allow_all" on contacts for all using (true) with check (true);
```

## 3. API 키 확인

Supabase 대시보드 → **Project Settings** → **API** 탭에서 복사:

| 항목 | 위치 |
|------|------|
| **Project URL** | `https://xxxx.supabase.co` 형식 |
| **anon public key** | `eyJ...` 로 시작하는 긴 문자열 |

## 4. index.html 수정

`index.html` 상단 스크립트에서 두 줄 수정:

```js
const SUPABASE_URL  = 'https://xxxx.supabase.co';   // ← Project URL
const SUPABASE_ANON = 'eyJ...';                      // ← anon key
```

## 5. 데이터 마이그레이션 (선택)

```bash
# 의존성 설치
pip install openpyxl requests

# migrate.py 상단의 SUPABASE_URL, SUPABASE_ANON 입력 후 실행
python migrate.py
```

엑셀 파일을 같은 폴더에 두거나 실행 시 경로를 직접 입력합니다.

## 6. Netlify 배포

### 방법 A — GitHub 연동 (권장)
1. 이 레포를 GitHub에 push
2. https://netlify.com 로그인 → **Add new site** → **Import from Git**
3. GitHub 레포 선택 → 빌드 설정 없이 바로 **Deploy site**
4. 배포 완료 후 URL 공유

### 방법 B — 드래그 앤 드롭
1. https://netlify.com → **Sites** → **Deploy manually**
2. `index.html`, `netlify.toml` 파일이 있는 폴더를 브라우저에 드래그
3. 즉시 배포 완료

## 로그인 정보

| 항목 | 값 |
|------|-----|
| 비밀번호 | `cellphone1!` |

비밀번호 변경: `index.html` 내 `const APP_PASSWORD = 'cellphone1!';` 수정

## 동의어 확장 검색

`서버` 검색 시 dell/hpe/x86/supermicro 등도 함께 검색됩니다.
추가 동의어는 `index.html` 내 `SYNONYMS` 객체를 수정하세요.
