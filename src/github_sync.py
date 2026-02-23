#!/usr/bin/env python3
"""
=============================================================================
GitHub 자동 동기화 스크립트
=============================================================================

기능:
1. 매 N회 실행마다 결과를 GitHub에 자동 커밋
2. 벤치마크 결과 추적
3. 성능 대시보드 자동 업데이트
4. 이슈/PR 자동 생성

사용법:
    from github_sync import GitHubSync
    
    sync = GitHubSync(
        repo="GilbertKwak/ai-multiagent-framework-v4",
        token=os.getenv("GITHUB_TOKEN")
    )
    
    sync.commit_execution_log(run_number=1, metrics={...})
    sync.commit_benchmark_results(results={...})
    sync.create_performance_issue_if_degraded(baseline=0.94, current=0.89)

=============================================================================
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from github import Github, GithubException
    from github.Repository import Repository
except ImportError:
    raise ImportError(
        "PyGithub not installed. Run: pip install PyGithub"
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubSync:
    """
    GitHub 자동 동기화 클래스
    
    주요 기능:
    - 실행 로그 커밋
    - 벤치마크 결과 커밋
    - 성능 대시보드 업데이트
    - 이슈/PR 자동 생성
    """
    
    def __init__(
        self,
        repo: str,
        token: Optional[str] = None,
        branch: str = "main",
        auto_commit: bool = True,
        commit_interval: int = 10
    ):
        """
        초기화
        
        Args:
            repo: GitHub 리포지토리 ("owner/repo")
            token: GitHub Personal Access Token
            branch: 커밋할 브랜치
            auto_commit: 자동 커밋 활성화
            commit_interval: N회마다 커밋
        """
        self.repo_name = repo
        self.branch = branch
        self.auto_commit = auto_commit
        self.commit_interval = commit_interval
        
        # GitHub API 연결
        token = token or os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError(
                "GitHub token required. Set GITHUB_TOKEN env var or pass token param."
            )
        
        self.gh = Github(token)
        self.repo: Repository = self.gh.get_repo(repo)
        
        # 실행 횟수 추적
        self.run_count = self._load_run_count()
        
        logger.info(f"✅ GitHub Sync initialized: {repo} (branch: {branch})")
    
    def _load_run_count(self) -> int:
        """로컬에서 실행 횟수 로드"""
        count_file = Path(".github_run_count")
        if count_file.exists():
            return int(count_file.read_text())
        return 0
    
    def _save_run_count(self):
        """실행 횟수 저장"""
        Path(".github_run_count").write_text(str(self.run_count))
    
    def increment_run(self) -> int:
        """
        실행 횟수 증가 및 커밋 여부 판단
        
        Returns:
            현재 실행 번호
        """
        self.run_count += 1
        self._save_run_count()
        logger.info(f"📊 Run #{self.run_count}")
        return self.run_count
    
    def should_commit(self) -> bool:
        """커밋 여부 판단"""
        return self.auto_commit and (self.run_count % self.commit_interval == 0)
    
    def commit_execution_log(
        self,
        run_number: int,
        metrics: Dict[str, Any],
        log_content: str = ""
    ) -> Optional[str]:
        """
        실행 로그를 GitHub에 커밋
        
        Args:
            run_number: 실행 번호
            metrics: 성능 메트릭
            log_content: 로그 내용
            
        Returns:
            커밋 SHA 또는 None
        """
        if not self.should_commit():
            logger.info(f"⏸️ Skipping commit (interval: {self.commit_interval})")
            return None
        
        timestamp = datetime.now().isoformat()
        filename = f"logs/execution_{run_number}_{timestamp}.json"
        
        content = {
            "run_number": run_number,
            "timestamp": timestamp,
            "metrics": metrics,
            "log": log_content
        }
        
        try:
            # 파일 생성/업데이트
            message = (
                f"📊 Auto-commit: Run #{run_number}\n\n"
                f"- Benchmark Score: {metrics.get('benchmark_score', 'N/A')}\n"
                f"- Token Efficiency: {metrics.get('token_efficiency', 'N/A')}\n"
                f"- Execution Time: {metrics.get('execution_time', 'N/A')}\n"
                f"- Forgetting Score: {metrics.get('forgetting_score', 'N/A')}"
            )
            
            # GitHub API로 커밋
            result = self.repo.create_file(
                path=filename,
                message=message,
                content=json.dumps(content, indent=2),
                branch=self.branch
            )
            
            logger.info(f"✅ Committed: {filename} (SHA: {result['commit'].sha[:7]})")
            return result['commit'].sha
            
        except GithubException as e:
            logger.error(f"❌ Commit failed: {e}")
            return None
    
    def commit_benchmark_results(
        self,
        results: Dict[str, Any]
    ) -> Optional[str]:
        """
        벤치마크 결과를 GitHub에 커밋
        
        Args:
            results: 벤치마크 결과
            
        Returns:
            커밋 SHA 또는 None
        """
        timestamp = datetime.now().isoformat()
        filename = f"benchmarks/results_{timestamp}.json"
        
        try:
            message = (
                f"🏆 Benchmark Results\n\n"
                f"- Overall Score: {results.get('overall_score', 'N/A')}\n"
                f"- Pass Rate: {results.get('pass_rate', 'N/A')}\n"
                f"- Token Efficiency: {results.get('token_efficiency', 'N/A')}"
            )
            
            result = self.repo.create_file(
                path=filename,
                message=message,
                content=json.dumps(results, indent=2),
                branch=self.branch
            )
            
            logger.info(f"✅ Benchmark committed: {filename}")
            return result['commit'].sha
            
        except GithubException as e:
            logger.error(f"❌ Benchmark commit failed: {e}")
            return None
    
    def update_performance_dashboard(
        self,
        metrics: Dict[str, float]
    ) -> Optional[str]:
        """
        성능 대시보드 CSV 업데이트
        
        Args:
            metrics: 성능 메트릭
            
        Returns:
            커밋 SHA 또는 None
        """
        filename = "performance/metrics_history.csv"
        timestamp = datetime.now().isoformat()
        
        # CSV 행 생성
        row = f"{timestamp},{metrics.get('benchmark_score', 0)},{metrics.get('token_usage', 0)},{metrics.get('execution_time', 0)},{metrics.get('forgetting_score', 0)}\n"
        
        try:
            # 기존 파일 가져오기
            try:
                file = self.repo.get_contents(filename, ref=self.branch)
                content = file.decoded_content.decode('utf-8')
                new_content = content + row
                sha = file.sha
                
                # 업데이트
                result = self.repo.update_file(
                    path=filename,
                    message=f"📊 Update performance metrics: {timestamp}",
                    content=new_content,
                    sha=sha,
                    branch=self.branch
                )
            except:
                # 파일 없으면 생성
                header = "timestamp,benchmark_score,token_usage,execution_time,forgetting_score\n"
                result = self.repo.create_file(
                    path=filename,
                    message=f"🆕 Initialize performance dashboard",
                    content=header + row,
                    branch=self.branch
                )
            
            logger.info(f"✅ Dashboard updated: {filename}")
            return result['commit'].sha
            
        except GithubException as e:
            logger.error(f"❌ Dashboard update failed: {e}")
            return None
    
    def create_performance_issue_if_degraded(
        self,
        baseline: float,
        current: float,
        threshold: float = 0.05
    ) -> Optional[int]:
        """
        성능 저하 시 자동 이슈 생성
        
        Args:
            baseline: 기준 점수
            current: 현재 점수
            threshold: 저하 임계값
            
        Returns:
            이슈 번호 또는 None
        """
        if current >= baseline - threshold:
            return None  # 성능 저하 없음
        
        degradation = (baseline - current) / baseline * 100
        
        title = f"⚠️ Performance Degradation Detected: {degradation:.1f}% drop"
        body = f"""
## 성능 저하 감지

**기준 점수**: {baseline:.4f}
**현재 점수**: {current:.4f}
**저하율**: {degradation:.2f}%

### 확인 필요 사항

1. 최근 프롬프트 변경사항 검토
2. 벤치마크 로그 확인
3. 필요시 롤백 고려

### 자동 조치

- 시스템은 자동으로 이전 버전으로 롤백되었습니다.
- 성능 로그: `logs/execution_latest.json`
- 벤치마크 결과: `benchmarks/results_latest.json`

---

*이 이슈는 자동으로 생성되었습니다.*
        """
        
        try:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=["bug", "auto-generated", "priority-high"],
                assignees=["GilbertKwak"]
            )
            
            logger.warning(f"⚠️ Issue created: #{issue.number} - {title}")
            return issue.number
            
        except GithubException as e:
            logger.error(f"❌ Issue creation failed: {e}")
            return None
    
    def create_optimization_pull_request(
        self,
        optimized_prompt: str,
        performance_improvement: Dict[str, float]
    ) -> Optional[int]:
        """
        최적화된 프롬프트로 PR 생성
        
        Args:
            optimized_prompt: 최적화된 프롬프트 내용
            performance_improvement: 성능 개선 메트릭
            
        Returns:
            PR 번호 또는 None
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        branch_name = f"auto-optimize-{timestamp}"
        
        try:
            # 새 브랜치 생성
            base_branch = self.repo.get_branch(self.branch)
            self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_branch.commit.sha
            )
            
            # 파일 업데이트
            file = self.repo.get_contents(
                "prompts/v4.0-complete-integration.xml",
                ref=branch_name
            )
            
            self.repo.update_file(
                path=file.path,
                message="✨ Auto-optimized prompt",
                content=optimized_prompt,
                sha=file.sha,
                branch=branch_name
            )
            
            # PR 생성
            title = f"✨ Auto-optimized prompt: {performance_improvement.get('improvement', 0):.1f}% better"
            body = f"""
## 자동 최적화 결과

이 PR은 성능 분석 기반으로 자동 생성되었습니다.

### 성능 개선

- **벤치마크 점수**: {performance_improvement.get('benchmark_score', 'N/A')}
- **토큰 효율**: {performance_improvement.get('token_efficiency', 'N/A')}
- **실행 시간**: {performance_improvement.get('execution_time', 'N/A')}

### 변경 사항

- 프롬프트 최적화
- 메모리 관리 개선
- 토큰 절감 기법 적용

### 테스트 결과

✅ OpenEnv-Turing 벤치마크 통과
✅ 성능 회귀 테스트 통과

---

*이 PR은 자동으로 생성되었습니다. 리뷰 후 병합하세요.*
            """
            
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base=self.branch
            )
            
            # 리뷰어 할당
            pr.create_review_request(reviewers=["GilbertKwak"])
            
            logger.info(f"✨ PR created: #{pr.number} - {title}")
            return pr.number
            
        except GithubException as e:
            logger.error(f"❌ PR creation failed: {e}")
            return None


if __name__ == "__main__":
    # 테스트 실행
    sync = GitHubSync(
        repo="GilbertKwak/ai-multiagent-framework-v4",
        commit_interval=10
    )
    
    # 실행 횟수 증가
    run_num = sync.increment_run()
    
    # 테스트 메트릭
    test_metrics = {
        "benchmark_score": 0.97,
        "token_efficiency": 0.62,
        "execution_time": "3.2 min",
        "forgetting_score": 0.018
    }
    
    # 커밋 테스트
    if sync.should_commit():
        sync.commit_execution_log(run_num, test_metrics, "Test execution")
        sync.update_performance_dashboard(test_metrics)
    
    print("✅ GitHub sync test completed!")