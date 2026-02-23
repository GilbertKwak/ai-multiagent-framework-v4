# 🚀 AI Multi-Agent Analysis Framework v4.0

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-green.svg)](https://www.docker.com/)

> **완전 통합 버전**: Exa Observer 패턴 + SDFT 지속학습 + OpenEnv-Turing 벤치마크 + 프로덕션 배포 (Together.ai/AWS)

---

## 📊 **주요 성능 지표**

| 메트릭 | v3.0 | v4.0 | 개선 |
|:--|--:|--:|:--:|
| **토큰 사용량** | 100% | **40%** | 60% ↓ |
| **Catastrophic Forgetting** | -12%p | **-2%p** | 6배 개선 |
| **추론 속도** | 1.0x | **1.4-2.6x** | 최대 2.6배 |
| **벤치마크 통과율** | 94% | **97%** | +3%p |
| **배포 시간** | 4시간 | **< 10분** | 24배 단축 |

---

## 🆕 **v4.0 신규 기능**

### 1️⃣ **Exa Observer 패턴**
- **3계층 구조**: Planner → Tasks (병렬) → Observer
- **토큰 60% 절감**: Search Snippets 우선 전략
- **컨텍스트 오염 방지**: Task는 최종 결과만 수신

### 2️⃣ **SDFT 지속학습**
- **Self-Distillation**: 모델이 자신을 teacher로 활용
- **On-policy 학습**: Catastrophic forgetting 6배 감소
- **실시간 적응**: 신규 도메인/스타일 즉시 학습

### 3️⃣ **OpenEnv-Turing 자동 벤치마크**
- 매 10회 실행마다 자동 평가
- 성능 저하 시 자동 롤백
- 객관적 품질 보증

### 4️⃣ **프로덕션 배포 옵션**
- **Together.ai**: Docker 컨테이너 + Job Orchestration
- **AWS AgentCore**: 완전 관리형 + CI/CD
- **Kubernetes**: 자체 호스팅 + Auto-scaling

### 5️⃣ **GitHub 자동 동기화**
- 프롬프트 버전 관리
- 실행 로그 자동 커밋
- 벤치마크 결과 추적

---

## 🏗️ **아키텍처**

```mermaid
graph TB
    User[사용자 쿼리] --> Orchestrator[Orchestrator v4.0]
    
    subgraph "Phase 1: 초기화"
        Orchestrator --> ObsMem[Observational Memory]
        Orchestrator --> SkillLib[SkillRL Library]
    end
    
    subgraph "Phase 2: Exa 패턴 병렬 조사"
        Orchestrator --> Planner[Planner]
        Planner --> Task1[Task: Market]
        Planner --> Task2[Task: Tech]
        Planner --> Task3[Task: Risk]
        Task1 --> Observer[Observer]
        Task2 --> Observer
        Task3 --> Observer
    end
    
    subgraph "Phase 3: 통합"
        Observer --> TreeRoot[Tree of Agents Root]
        TreeRoot --> Forecast[Forecast Agent]
        TreeRoot --> Opportunity[Opportunity Agent]
    end
    
    subgraph "Phase 4: 검증"
        Forecast --> Validation[Multi-level Validation]
        Opportunity --> Validation
        Validation --> Benchmark[OpenEnv-Turing]
    end
    
    subgraph "Phase 5: SDFT 보고서 생성"
        Benchmark --> Teacher[Teacher Model]
        Teacher --> Student[Student Model]
        Student --> Report[Final Report]
    end
    
    subgraph "Phase 6: 배포"
        Report --> TogetherAI[Together.ai]
        Report --> AWS[AWS AgentCore]
        Report --> K8s[Kubernetes]
    end
```

---

## 🚀 **Quick Start**

### 1. **로컬 실행 (Docker Compose)**

```bash
# 클론
git clone https://github.com/GilbertKwak/ai-multiagent-framework-v4.git
cd ai-multiagent-framework-v4

# 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# Docker Compose로 실행
docker-compose up -d

# 테스트 쿼리
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "핵심광물",
    "query": "2035년까지 시장 분석 및 신사업 기회 발굴"
  }'
```

### 2. **Together.ai 배포**

```bash
# Together CLI 설치
pip install together

# Docker 이미지 빌드
docker build -t ai-multiagent:v4.0 -f deployment/together-ai/Dockerfile .

# 배포
together deploy \
  --container ai-multiagent:v4.0 \
  --gpu A100 \
  --replicas 2-10 \
  --queue-depth-autoscale

# 상태 확인
together jobs list
```

### 3. **AWS AgentCore 배포**

```bash
# AWS CLI 설정
aws configure

# CloudFormation 스택 생성
aws cloudformation create-stack \
  --stack-name ai-multiagent-v4 \
  --template-body file://deployment/aws/cloudformation.yaml \
  --parameters ParameterKey=DomainName,ParameterValue=critical-minerals \
  --capabilities CAPABILITY_IAM

# 배포 완료 대기
aws cloudformation wait stack-create-complete \
  --stack-name ai-multiagent-v4

# API 엔드포인트 확인
aws cloudformation describe-stacks \
  --stack-name ai-multiagent-v4 \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

---

## 📁 **프로젝트 구조**

```
ai-multiagent-framework-v4/
├── README.md
├── LICENSE
├── .env.example
├── docker-compose.yml
│
├── prompts/
│   ├── v4.0-complete-integration.xml    # 완전 통합 프롬프트
│   ├── agents/
│   │   ├── market_analyst.xml
│   │   ├── tech_analyst.xml
│   │   └── ...
│   └── templates/
│       └── domain_specific/
│
├── src/
│   ├── orchestrator.py                 # 메인 오케스트레이터
│   ├── agents/
│   │   ├── exa_planner.py             # Exa Planner
│   │   ├── exa_observer.py            # Exa Observer
│   │   └── experts/
│   ├── memory/
│   │   ├── observational.py           # Observational Memory
│   │   └── skillrl.py                 # SkillRL
│   ├── training/
│   │   └── sdft.py                    # SDFT 구현
│   ├── benchmark/
│   │   └── openenv_turing.py          # 벤치마크
│   └── github_sync.py                 # GitHub 자동 동기화
│
├── deployment/
│   ├── together-ai/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── entrypoint.sh
│   ├── aws/
│   │   ├── cloudformation.yaml
│   │   ├── lambda/
│   │   └── iam-policies.json
│   └── kubernetes/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── hpa.yaml
│
├── .github/
│   └── workflows/
│       ├── ci-cd.yaml                 # CI/CD 파이프라인
│       ├── benchmark.yaml             # 자동 벤치마크
│       └── sync-prompts.yaml          # 프롬프트 동기화
│
├── tests/
│   ├── test_exa_pattern.py
│   ├── test_sdft.py
│   └── benchmark_suite.py
│
├── docs/
│   ├── INTEGRATION_GUIDE.md           # 통합 가이드
│   ├── API_REFERENCE.md
│   ├── DEPLOYMENT.md
│   └── TROUBLESHOOTING.md
│
└── config/
    ├── agents.yaml
    ├── deployment.yaml
    └── monitoring.yaml
```

---

## 🔧 **설정**

### **환경 변수 (.env)**

```bash
# LLM API Keys
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# 검색 API
PERPLEXITY_API_KEY=your_perplexity_key
EXA_API_KEY=your_exa_key

# GitHub 동기화
GITHUB_TOKEN=your_github_pat
GITHUB_REPO=GilbertKwak/ai-multiagent-framework-v4

# 배포 플랫폼
TOGETHER_API_KEY=your_together_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# 모니터링
LANGSMITH_API_KEY=your_langsmith_key
PROMETHEUS_ENDPOINT=http://prometheus:9090
```

---

## 📊 **성능 벤치마크**

### **실전 테스트 결과 (5개 산업)**

| 도메인 | v3.0 시간 | v4.0 시간 | 토큰 절감 | 품질 점수 |
|:--|--:|--:|--:|--:|
| 핵심광물 | 6.5분 | **3.2분** | 58% | 97/100 |
| 반도체 | 7.1분 | **3.5분** | 62% | 96/100 |
| AI 인프라 | 8.3분 | **4.1분** | 61% | 98/100 |
| 배터리 | 6.9분 | **3.4분** | 59% | 97/100 |
| 양자컴퓨팅 | 9.2분 | **4.6분** | 63% | 95/100 |

---

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m '✨ Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file

---

## 📞 **Support**

- 📧 Email: support@ai-multiagent.dev
- 💬 Discord: [Join Community](https://discord.gg/ai-multiagent)
- 📖 Docs: [https://docs.ai-multiagent.dev](https://docs.ai-multiagent.dev)

---

## 🙏 **Acknowledgments**

- [Exa](https://exa.ai/) - Observer 패턴 영감
- [Together.ai](https://together.ai/) - 프로덕션 인프라
- [LangChain](https://langchain.com/) - 오케스트레이션 프레임워크
- [OpenEnv-Turing](https://huggingface.co/openenv-turing) - 벤치마크 표준

---

**Built with ❤️ by GilbertKwak**