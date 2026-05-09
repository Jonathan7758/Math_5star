"""
Multi-Agent UI/UX Review Framework for Math-5star

Architecture:
  Design → Code → Test → Review Agents (UX/A11y/Perf/Content/Kid) → Arbiter

Usage:
  python -m backend.review_agents.run_review [--target <component>]
  python -m backend.review_agents.run_review --target quiz_card
  python -m backend.review_agents.run_review --all
"""

import json
import re
import os
import sys
from dataclasses import dataclass, field
from typing import Optional, Callable
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
FLUTTER_SRC = PROJECT_ROOT / "android_app" / "lib"


# ============================================================
# Review Result
# ============================================================
@dataclass
class ReviewFinding:
    id: str
    severity: str  # critical, high, medium, low
    category: str  # ux, a11y, perf, content, kid
    location: str  # file or component name
    description: str
    suggestion: str
    score_impact: int  # how many points this finding costs

@dataclass
class ReviewReport:
    target: str
    agent: str
    score: float  # 1-10
    findings: list[ReviewFinding] = field(default_factory=list)
    praise: list[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"\n{'='*50}",
            f"  {self.agent} Review: {self.target}",
            f"  Score: {self.score:.1f}/10",
            f"  Findings: {len(self.findings)}",
        ]
        for f in self.findings:
            lines.append(f"    [{f.severity.upper()}] {f.id}: {f.description[:60]}")
        if self.praise:
            lines.append("  Praise:")
            for p in self.praise:
                lines.append("    [+] " + p)
        return "\n".join(lines)


# ============================================================
# Base Review Agent
# ============================================================
class ReviewAgent:
    name: str = "base"
    weight: float = 0.2

    def review(self, target: str, files: list[str]) -> ReviewReport:
        raise NotImplementedError


# ============================================================
# UX Review Agent
# ============================================================
class UXReviewAgent(ReviewAgent):
    name = "UX"
    weight = 0.30

    RULES = {
        "touch_target": {
            "pattern": r'min-h-\[(\d+)px\]|minH:\s*(\d+)|minHeight\s*:\s*(\d+)',
            "min_size": 44,
            "message": "触控目标必须 >= 44px (Flutter: minHeight >= 48)",
            "impact": 2,
        },
        "animation_duration": {
            "pattern": r'duration:\s*(\d+)\s*(?:ms|milliseconds)|\bDuration\s*\(\s*milliseconds\s*:\s*(\d+)',
            "max_ms": 400,
            "message": "动画时长不应超过 400ms",
            "impact": 1,
        },
        "feedback_presence": {
            "check": lambda files: any(w in "".join(files).lower() for w in ["correct", "error", "iscorrect", "iswrong", "is_correct", "iswrongselected", "correctopt", "hint"]),
            "message": "每个操作必须有即时反馈(正确/错误状态)",
            "impact": 3,
        },
        "loading_state": {
            "check": lambda files: any(w in "".join(files).lower() for w in ["loading", "isloading", "submitting", "circularprogressindicator", "loadingspinner"]),
            "message": "必须有加载状态指示",
            "impact": 2,
        },
        "empty_state": {
            "check": lambda files: any(w in "".join(files) for w in ["empty", "暂无", "nodata", "noquestion", "空"]),
            "message": "必须有空状态处理",
            "impact": 1,
        },
    }

    def review(self, target: str, files: list[str]) -> ReviewReport:
        report = ReviewReport(target=target, agent=self.name, score=10.0)
        content = " ".join(files)

        for rule_id, rule in self.RULES.items():
            if "pattern" in rule:
                matches = re.findall(rule["pattern"], content)
                if not matches:
                    report.findings.append(ReviewFinding(
                        id=rule_id,
                        severity="high",
                        category="ux",
                        location=target,
                        description=rule["message"],
                        suggestion=f"添加{rule['message']}",
                        score_impact=rule["impact"],
                    ))
                    report.score -= rule["impact"]
                else:
                    # Verify min size for touch targets
                    if rule_id == "touch_target":
                        sizes = [int(n) for m in matches for n in m if n and int(n) > 0]
                        if sizes and all(s < rule.get("min_size", 44) for s in sizes):
                            report.findings.append(ReviewFinding(
                                id=rule_id, severity="low", category="ux",
                                location=target,
                                description=f"触控目标尺寸 {min(sizes)}px 小于推荐的最小值",
                                suggestion=f"增大到 {rule.get('min_size', 44)}px+",
                                score_impact=1,
                            ))
                            report.score -= 1
            elif "check" in rule:
                if not rule["check"](files):
                    report.findings.append(ReviewFinding(
                        id=rule_id,
                        severity="medium",
                        category="ux",
                        location=target,
                        description=rule["message"],
                        suggestion=f"添加{rule['message']}",
                        score_impact=rule["impact"],
                    ))
                    report.score -= rule["impact"]

        report.score = max(1.0, min(10.0, report.score))

        # Praise
        if "animate" in content.lower():
            report.praise.append("使用了动画效果")
        if "触摸" in content or "touch" in content.lower() or "min-h-" in content:
            report.praise.append("考虑了触控交互")
        if "反馈" in content or "feedback" in content.lower() or "isCorrect" in content:
            report.praise.append("有答对/答错反馈机制")

        return report


# ============================================================
# A11y Review Agent
# ============================================================
class A11yReviewAgent(ReviewAgent):
    name = "A11y"
    weight = 0.10

    def review(self, target: str, files: list[str]) -> ReviewReport:
        report = ReviewReport(target=target, agent=self.name, score=10.0)
        content = " ".join(files)

        checks = {
            "aria_labels": (r'aria-label|ariaLabel|Semantics\s*\(|semanticsLabel|semantics\s*label',
                           "缺少无障碍标签 (React: aria-label, Flutter: Semantics)", 2),
            "keyboard_nav": (r'onKeyDown|onKey|tabIndex|tabindex|FocusNode|focusNode|Focus\(',
                            "缺少键盘导航支持 (React: onKeyDown, Flutter: FocusNode)", 2),
            "live_regions": (r'aria-live|ariaLive|LiveRegion|announce',
                            "缺少动态内容通知", 1),
            "role_attr": (r'role\s*[=:]|Semantics\(.*button|Semantics\(.*alert|semantics.*role',
                         "缺少语义化角色 (React: role=, Flutter: Semantics)", 1),
            "color_independent": (r'semanticsLabel|tooltip|Tooltip|aria-describedby|label:',
                                 "颜色信息需要文字辅助 (React: aria, Flutter: semantics label)", 1),
        }

        for check_id, (pattern, msg, impact) in checks.items():
            if not re.search(pattern, content, re.IGNORECASE):
                report.findings.append(ReviewFinding(
                    id=check_id,
                    severity="medium" if impact > 1 else "low",
                    category="a11y",
                    location=target,
                    description=msg,
                    suggestion=f"添加 {check_id} 支持",
                    score_impact=impact,
                ))
                report.score -= impact

        report.score = max(1.0, min(10.0, report.score))
        return report


# ============================================================
# Performance Review Agent
# ============================================================
class PerfReviewAgent(ReviewAgent):
    name = "Perf"
    weight = 0.10

    def review(self, target: str, files: list[str]) -> ReviewReport:
        report = ReviewReport(target=target, agent=self.name, score=10.0)
        content = " ".join(files)

        checks = {
            "image_optimization": (r'loading="lazy"|cacheNetworkImage|cached_network_image|memCache',
                                   "图片/资源应使用缓存和懒加载", 1),
            "avoid_rebuilds": (r'const\s|@immutable|shouldRebuild|RepaintBoundary',
                              "应使用 const/RepaintBoundary 减少重绘", 2),
            "debounce_throttle": (r'debounce|throttle|timer|setTimeout|Future\.delayed',
                                 "频繁操作应有防抖/节流", 1),
        }

        for check_id, (pattern, msg, impact) in checks.items():
            if not re.search(pattern, content, re.IGNORECASE):
                report.findings.append(ReviewFinding(
                    id=check_id,
                    severity="low",
                    category="perf",
                    location=target,
                    description=msg,
                    suggestion=f"添加 {check_id}",
                    score_impact=impact,
                ))
                report.score -= impact

        report.score = max(1.0, min(10.0, report.score))
        return report


# ============================================================
# Content Review Agent
# ============================================================
class ContentReviewAgent(ReviewAgent):
    name = "Content"
    weight = 0.20

    LANGUAGE_RULES = {
        "too_long": (r'[\u4e00-\u9fff]{80,}', "中文字符超过80字，对儿童太长"),
        "no_explanation": (r'解释|说明|because|所以|因为', "缺少解释性文字"),
        "difficult_words": (r'抽象|递归|归纳|演绎|无穷|极限', "包含对儿童太难的概念词"),
    }

    def review(self, target: str, files: list[str]) -> ReviewReport:
        report = ReviewReport(target=target, agent=self.name, score=10.0)
        content = " ".join(files)

        for rule_id, (pattern, msg) in self.LANGUAGE_RULES.items():
            if rule_id == "no_explanation":
                if not re.search(pattern, content):
                    report.findings.append(ReviewFinding(
                        id=rule_id, severity="high", category="content",
                        location=target, description=msg,
                        suggestion="添加解释或引导文字",
                        score_impact=2,
                    ))
                    report.score -= 2
            elif rule_id in ("too_long", "difficult_words"):
                matches = re.findall(pattern, content)
                if matches:
                    report.findings.append(ReviewFinding(
                        id=rule_id, severity="medium", category="content",
                        location=target,
                        description=f"{msg} (发现{len(matches)}处)",
                        suggestion="简化语言或降低难度",
                        score_impact=1,
                    ))
                    report.score -= 1

        report.score = max(1.0, min(10.0, report.score))
        return report


# ============================================================
# Kid Perspective Review Agent
# ============================================================
class KidReviewAgent(ReviewAgent):
    name = "Kid"
    weight = 0.30

    FUN_FACTORS = {
        "has_character": (r'精灵|启小星|sprite|mascot|avatar|角色|character|themeIcon|spriteStage',
                          "有角色/精灵陪伴", 3),
        "has_reward": (r'XP|xp|coin|星币|reward|奖励|achievement|成就|badge|徽章',
                       "有奖励/成就系统", 3),
        "has_sound": (r'playSound|play_sound|sound|audio|音效|BGM|onCorrectSound|onWrongSound|audioplayer',
                      "有音效/声音反馈", 2),
        "has_color": (r'gradient|color|Color|rainbow|色彩|渐变|彩色|LinearGradient|RadialGradient|BoxShadow',
                      "使用了丰富色彩(非纯黑/灰)", 1),
        "has_animation": (r'animate|Animation|bounce|scale|slide|fade|wiggle|pulse|AnimationController|Tween',
                          "有动画效果", 2),
        "has_theme": (r'theme|主题|story|故事|adventure|冒险|space|太空|animal|动物|fruit|水果|themeIcon',
                      "有主题/故事包装", 3),
        "encouragement": (r'加油|很棒|不错|厉害|太棒|再接再厉|鼓励|encourage|cheer|Encouragement|encMsg|_encMsg|correctMsg',
                          "有鼓励性文字", 2),
    }

    def review(self, target: str, files: list[str]) -> ReviewReport:
        report = ReviewReport(target=target, agent=self.name, score=10.0)
        content = " ".join(files)
        total_impact = 0

        for factor_id, (pattern, msg, impact) in self.FUN_FACTORS.items():
            if re.search(pattern, content, re.IGNORECASE):
                report.praise.append(msg)
            else:
                report.findings.append(ReviewFinding(
                    id=factor_id, severity="high" if impact >= 3 else "medium",
                    category="kid", location=target,
                    description=f"缺少: {msg}",
                    suggestion=f"添加{factor_id}",
                    score_impact=impact,
                ))
                report.score -= impact
                total_impact += impact

        report.score = max(1.0, min(10.0, report.score))
        return report


# ============================================================
# Arbiter Agent
# ============================================================
class ArbiterAgent:
    """Combines all review results and produces final score + recommendations"""

    def arbitrate(self, reports: list[ReviewReport]) -> dict:
        # Find all agents
        agents = {r.agent: r for r in reports}

        # Weighted score
        weights = {"UX": 0.30, "A11y": 0.10, "Perf": 0.10, "Content": 0.20, "Kid": 0.30}
        total_weight = sum(weights.values())
        weighted_score = sum(
            agents[k].score * v for k, v in weights.items() if k in agents
        ) / total_weight if total_weight > 0 else 0

        # Collect critical/high findings
        critical = [f for r in reports for f in r.findings if f.severity == "critical"]
        high = [f for r in reports for f in r.findings if f.severity == "high"]
        medium = [f for r in reports for f in r.findings if f.severity == "medium"]
        low = [f for r in reports for f in r.findings if f.severity == "low"]

        # Generate priority recommendations
        recommendations = []
        for f in critical + high[:5]:
            recommendations.append({
                "priority": "P0" if f.severity == "critical" else "P1",
                "finding": f.id,
                "suggestion": f.suggestion,
                "location": f.location,
            })

        verdict = "PASS" if weighted_score >= 7.0 else "NEEDS_IMPROVEMENT"

        return {
            "verdict": verdict,
            "score": round(weighted_score, 1),
            "max_score": 10.0,
            "weights": weights,
            "agent_scores": {k: agents[k].score if k in agents else None for k in weights},
            "findings_summary": {
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "low": len(low),
            },
            "recommendations": recommendations,
            "praise": [p for r in reports for p in r.praise],
        }


# ============================================================
# Runner
# ============================================================
def run_review(target: str, files: list[str], verbose: bool = True) -> dict:
    """Run all review agents on a target component."""
    agents = [
        UXReviewAgent(),
        A11yReviewAgent(),
        PerfReviewAgent(),
        ContentReviewAgent(),
        KidReviewAgent(),
    ]

    reports = []
    for agent in agents:
        report = agent.review(target, files)
        reports.append(report)
        if verbose:
            print(report.summary())

    arbiter = ArbiterAgent()
    result = arbiter.arbitrate(reports)

    if verbose:
        print(f"\n{'='*50}")
        print(f"  FINAL VERDICT: {result['verdict']}")
        print(f"  Overall Score: {result['score']}/10")
        print(f"  Critical: {result['findings_summary']['critical']}")
        print(f"  High: {result['findings_summary']['high']}")
        print(f"  Medium: {result['findings_summary']['medium']}")
        print(f"  Low: {result['findings_summary']['low']}")
        if result['recommendations']:
            print("  Top Recommendations:")
            for r in result['recommendations'][:5]:
                print(f"    [{r['priority']}] {r['finding']}: {r['suggestion']}")

    return result


def review_component(component_name: str, framework: str = "flutter") -> dict:
    """Review a specific Flutter or React component."""
    files = []
    target_path = None

    if framework == "react":
        search_dirs = [(str(FRONTEND_SRC), [".tsx", ".ts"])]
    elif framework == "flutter":
        search_dirs = [(str(FLUTTER_SRC), [".dart"])]
    else:
        search_dirs = [
            (str(FLUTTER_SRC), [".dart"]),
            (str(FRONTEND_SRC), [".tsx", ".ts"]),
        ]

    for search_dir, exts in search_dirs:
        if not os.path.isdir(search_dir):
            continue
        for ext in exts:
            for root, _, filenames in os.walk(search_dir):
                for fn in filenames:
                    name_lower = fn.lower().replace("_", "").replace("-", "")
                    search_lower = component_name.lower().replace("_", "").replace("-", "")
                    if search_lower in name_lower and fn.endswith(ext):
                        target_path = os.path.join(root, fn)
                        break
                if target_path:
                    break
            if target_path:
                break
        if target_path:
            break

    # Search Flutter
    if not target_path:
        for ext in [".dart"]:
            for root, _, filenames in os.walk(str(FLUTTER_SRC)):
                for fn in filenames:
                    name_lower = fn.lower().replace("_", "").replace("-", "")
                    search_lower = component_name.lower().replace("_", "").replace("-", "")
                    if search_lower in name_lower and fn.endswith(ext):
                        target_path = os.path.join(root, fn)
                        break

    if not target_path:
        print(f"Component '{component_name}' not found")
        return {"verdict": "NOT_FOUND"}

    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    return run_review(component_name, [content])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Multi-Agent UI Review")
    parser.add_argument("--target", "-t", default="question_card", help="Component to review")
    parser.add_argument("--all", action="store_true", help="Review all key components")
    parser.add_argument("--framework", "-f", default="flutter", choices=["flutter", "react", "all"], help="Target framework")
    args = parser.parse_args()

    if args.all:
        components = ["quiz_screen", "question_card", "math_sprite", "diagnose_screen", "home_screen"]
        all_results = {}
        for comp in components:
            all_results[comp] = review_component(comp, args.framework)
        # Print summary
        print("\n" + "=" * 60)
        print("ALL COMPONENTS SUMMARY")
        for comp, result in all_results.items():
            status = "+" if result.get("verdict") == "PASS" else "x"
            print(f"  {status} {comp}: {result.get('score', '?')}/10")
    else:
        review_component(args.target, args.framework)
