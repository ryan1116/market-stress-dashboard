# Google Sheets 자동 수집 연결

시트 저장과 공개 CSV 읽기 검증 완료. 남은 작업은 GitHub Actions가 시트에 쓸 수 있는 인증 설정입니다.
일반 Gmail/회사 이메일 로그인과 서비스 계정은 다릅니다. 현재 연결된 Google 계정 인증을 GitHub에 복사할 수는 없습니다.

1. [Google Cloud 프로젝트 선택/생성](https://console.cloud.google.com/projectselector2/home/dashboard)에서 사용할 프로젝트를 정합니다. [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com)를 사용 설정합니다.
2. [서비스 계정](https://console.cloud.google.com/iam-admin/serviceaccounts)에서 `market-stress-writer`를 만듭니다. 프로젝트 역할은 부여하지 않아도 됩니다. 생성된 주소는 `...@...iam.gserviceaccount.com` 형태입니다.
3. [데이터 시트](https://docs.google.com/spreadsheets/d/1KpPI7uOPcqlnxrVzkGpjlyj3hp7i0uvwrf6agqvYMAw/edit)의 공유에 그 주소를 **편집자**로 추가합니다.
4. 서비스 계정의 ‘키 → 키 추가 → 새 키 만들기 → JSON’에서 받은 키 내용을 [GitHub Actions Secrets](https://github.com/ryan1116/market-stress-dashboard/settings/secrets/actions)의 `GOOGLE_SERVICE_ACCOUNT_JSON`에 등록합니다. 키 파일을 채팅이나 저장소에 올리지 마세요. 조직 정책이 키 발급을 금지하면 우회하지 말고 Workload Identity Federation 방식으로 연결해야 합니다.

여기까지 완료되면 알려주세요. 이후 작업은 Codex가 처리합니다.
- `SHEETS_SYNC_ENABLED=true` 설정
- 예약 작업과 동일한 수집 경로 실행, 시트 쓰기 검증
- `config/data_backend.json`을 `google_sheets` 모드로 전환
- 웹 배포 및 공개 시트 값과 화면 데이터 일치 확인

공개 CSV 주소는 이미 설정 파일에 저장했습니다. 현재 웹은 인증 설정 전 데이터가 멈추지 않도록 기존 저장소 모드를 유지합니다.
시트의 `MSD_` 탭은 수집 결과입니다. 직접 수정해도 다음 수집 시 덮어씁니다. 원래 `시트1`은 자동 작업이 건드리지 않습니다.
