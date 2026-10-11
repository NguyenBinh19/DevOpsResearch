"""Curate topic-first Markdown from the existing teaching chapters."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEST = ROOT.parent / "topics" / "_source"
DEST.mkdir(parents=True, exist_ok=True)


def sections(name: str) -> dict[str, str]:
    source = (ROOT / name).read_text(encoding="utf-8")
    parts = re.split(r"(?m)(?=^## )", source)
    result = {}
    for part in parts[1:]:
        heading = part.splitlines()[0][3:].strip()
        result[heading] = part.strip()
    return result


CATALOG = [
    ("01-devops", "DevOps: tư duy và vòng đời dịch vụ", [
        ("00-dinh-huong.md", ["Bài 1.", "Bài 2.", "Bài 4.", "Bài 5.", "Thuật ngữ"]),
    ]),
    ("02-linux", "Linux: tiến trình, quyền, service và điều tra lỗi", [
        ("01-nen-tang-he-thong.md", ["Bài 1."]),
    ]),
    ("03-networking", "Mạng cho DevOps: DNS, TCP, HTTP, TLS và chẩn đoán", [
        ("01-nen-tang-he-thong.md", ["Bài 2.", "Bài 6."]),
        ("03-cloud-iac.md", ["Bài 7."]),
        ("12-edge-observability.md", ["Bài 1."]),
    ]),
    ("04-git", "Git và quản trị thay đổi", [
        ("01-nen-tang-he-thong.md", ["Bài 3.", "Bài 7."]),
        ("02-container-ci.md", ["Bài 1."]),
    ]),
    ("05-python-api", "Ứng dụng Notes API: Python, HTTP và SQL", [
        ("01-nen-tang-he-thong.md", ["Bài 4.", "Bài 5.", "Bài 8."]),
        ("02-container-ci.md", ["Bài 7."]),
    ]),
    ("06-docker", "Docker: image, container, volume và network", [
        ("02-container-ci.md", ["Bài 2.", "Bài 4."]),
    ]),
    ("07-ci-cd", "CI/CD: pipeline, artifact, release và rollback", [
        ("02-container-ci.md", ["Bài 1.", "Bài 3.", "Bài 5.", "Bài 6.", "Bài 8.", "Bài 9."]),
        ("11-delivery-gitops.md", ["Bài 1.", "Bài 2.", "Bài 3.", "Case study"]),
    ]),
    ("08-terraform", "Terraform: IaC, state, drift và review plan", [
        ("03-cloud-iac.md", ["Bài 3.", "Bài 4.", "Bài 8.", "Bài 9."]),
        ("09-azure-enterprise.md", ["Bài 4."]),
    ]),
    ("09-cloud-iam", "Cloud, IAM và mạng riêng", [
        ("03-cloud-iac.md", ["Bài 1.", "Bài 2.", "Bài 5.", "Bài 6.", "Bài 7."]),
    ]),
    ("10-kubernetes", "Kubernetes: từ kiến trúc đến vận hành", [
        ("05-kubernetes.md", ["Bài 1.", "Bài 2.", "Bài 3.", "Bài 4.", "Bài 5.", "Bài 6.", "Bài 7.", "Bài 8.", "Bài 9."]),
        ("08-hybrid-onprem.md", ["Bài 7."]),
    ]),
    ("11-helm", "Helm: chart, template, values và release", [
        ("11-delivery-gitops.md", ["Bài 4."]),
    ]),
    ("12-argocd", "Argo CD và GitOps", [
        ("11-delivery-gitops.md", ["Bài 5.", "Case study"]),
    ]),
    ("13-observability", "Observability: metrics, logs, traces và alert", [
        ("04-van-hanh-sre.md", ["Bài 2.", "Bài 3.", "Bài 5.", "Bài 8.", "Bài 9."]),
        ("12-edge-observability.md", ["Bài 4.", "Bài 5.", "Case study"]),
    ]),
    ("14-sre-incident", "SRE: SLO, incident, runbook và phục hồi", [
        ("04-van-hanh-sre.md", ["Bài 1.", "Bài 3.", "Bài 4.", "Bài 5.", "Bài 6.", "Bài 7."]),
        ("06-bao-mat-tin-cay.md", ["Bài 3.", "Bài 4.", "Bài 7.", "Bài 8."]),
    ]),
    ("15-security", "DevSecOps: quyền, secret và chuỗi cung ứng", [
        ("06-bao-mat-tin-cay.md", ["Bài 1.", "Bài 2.", "Bài 5.", "Bài 6."]),
        ("09-azure-enterprise.md", ["Bài 6."]),
    ]),
    ("16-vmware-hybrid", "VMware và hạ tầng hybrid", [
        ("08-hybrid-onprem.md", ["Bài 1.", "Bài 5.", "Bài 6.", "Bài 7.", "Case study"]),
    ]),
    ("17-storage", "Storage cho DevOps: block, file, object và backup", [
        ("08-hybrid-onprem.md", ["Bài 2."]),
        ("05-kubernetes.md", ["Bài 7."]),
        ("10-du-lieu-messaging.md", ["Bài 8."]),
    ]),
    ("18-ansible", "Ansible và tự động hóa máy chủ", [
        ("08-hybrid-onprem.md", ["Bài 4."]),
        ("11-delivery-gitops.md", ["Bài 6."]),
    ]),
    ("19-azure", "Azure DevOps: identity, network, services và pipeline", [
        ("09-azure-enterprise.md", ["Bài 1.", "Bài 2.", "Bài 3.", "Bài 4.", "Bài 5.", "Bài 6.", "Bài 7.", "Case study"]),
    ]),
    ("20-database", "Database quan hệ: MySQL, PostgreSQL và phục hồi", [
        ("10-du-lieu-messaging.md", ["Bài 1.", "Bài 2.", "Bài 3.", "Bài 8."]),
    ]),
    ("21-messaging", "Redis, queue và Kafka", [
        ("10-du-lieu-messaging.md", ["Bài 4.", "Bài 5.", "Bài 7.", "Bài 9.", "Case study"]),
    ]),
    ("22-edge", "Nginx, HAProxy, ingress và API gateway", [
        ("12-edge-observability.md", ["Bài 1.", "Bài 2.", "Bài 3."]),
    ]),
    ("23-portfolio", "Portfolio và phỏng vấn DevOps", [
        ("07-portfolio-phong-van.md", ["Bài 1.", "Bài 2.", "Bài 3.", "Bài 4.", "Bài 5.", "Bài 6.", "Bài 7.", "Bài 8."]),
    ]),
]


def source_urls(names: set[str]) -> list[str]:
    urls = set()
    for name in names:
        for url in re.findall(r"https?://[^\s)]+", (ROOT / name).read_text(encoding="utf-8")):
            urls.add(url.rstrip(".,"))
    return sorted(urls)


BIBLIO = {
    "01-devops": ["https://dora.dev/capabilities/", "https://sre.google/workbook/monitoring/"],
    "02-linux": ["https://www.kernel.org/doc/", "https://www.freedesktop.org/software/systemd/man/latest/"],
    "03-networking": ["https://www.rfc-editor.org/rfc/rfc1035", "https://www.rfc-editor.org/rfc/rfc9110", "https://www.rfc-editor.org/rfc/rfc8446"],
    "04-git": ["https://git-scm.com/docs", "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository"],
    "05-python-api": ["https://docs.python.org/3/", "https://www.sqlite.org/docs.html"],
    "06-docker": ["https://docs.docker.com/get-started/docker-concepts/", "https://docs.docker.com/compose/"],
    "07-ci-cd": ["https://docs.gitlab.com/ci/pipelines/", "https://www.jenkins.io/doc/book/pipeline/", "https://learn.microsoft.com/azure/devops/pipelines/yaml-schema/?view=azure-pipelines", "https://docs.github.com/en/actions"],
    "08-terraform": ["https://developer.hashicorp.com/terraform/language/state", "https://developer.hashicorp.com/terraform/cli/commands/plan"],
    "09-cloud-iam": ["https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html", "https://learn.microsoft.com/azure/role-based-access-control/overview", "https://docs.cloud.google.com/iam/docs/overview"],
    "10-kubernetes": ["https://kubernetes.io/docs/concepts/", "https://kubernetes.io/docs/tasks/debug/"],
    "11-helm": ["https://helm.sh/docs/"],
    "12-argocd": ["https://argo-cd.readthedocs.io/en/stable/"],
    "13-observability": ["https://prometheus.io/docs/", "https://opentelemetry.io/docs/", "https://grafana.com/docs/grafana/latest/", "https://www.elastic.co/guide/en/cloud-on-k8s/current/index.html"],
    "14-sre-incident": ["https://sre.google/workbook/alerting-on-slos/", "https://sre.google/workbook/incident-response/"],
    "15-security": ["https://owasp.org/www-project-top-ten/", "https://csrc.nist.gov/pubs/sp/800/218/final", "https://developer.hashicorp.com/vault/docs"],
    "16-vmware-hybrid": ["https://techdocs.broadcom.com/us/en/vmware-cis/vsphere.html"],
    "17-storage": ["https://docs.ceph.com/en/latest/", "https://kubernetes.io/docs/concepts/storage/", "https://min.io/docs/minio/linux/operations/concepts.html"],
    "18-ansible": ["https://docs.ansible.com/projects/ansible/latest/getting_started/index.html", "https://github.com/kubernetes-sigs/kubespray/tree/master/docs"],
    "19-azure": ["https://learn.microsoft.com/azure/well-architected/", "https://learn.microsoft.com/azure/private-link/private-endpoint-overview", "https://learn.microsoft.com/azure/devops/pipelines/yaml-schema/?view=azure-pipelines"],
    "20-database": ["https://dev.mysql.com/doc/refman/8.4/en/backup-and-recovery.html", "https://www.postgresql.org/docs/current/"],
    "21-messaging": ["https://www.rabbitmq.com/docs", "https://kafka.apache.org/documentation/", "https://redis.io/docs/latest/"],
    "22-edge": ["https://docs.nginx.com/nginx/admin-guide/", "https://www.haproxy.org/documentation/", "https://kubernetes.io/docs/concepts/services-networking/ingress/", "https://www.keycloak.org/documentation"],
    "23-portfolio": ["https://dora.dev/capabilities/", "https://sre.google/workbook/"],
}


for slug, title, includes in CATALOG:
    master = ROOT.parent / "topics" / "_master" / f"{slug}.md"
    if master.exists():
        content = master.read_text(encoding="utf-8")
        (DEST / f"{slug}.md").write_text(content, encoding="utf-8")
        print(slug, len(content.split()), "words (master)")
        continue
    blocks = [f"# {title}", "", "Tài liệu độc lập theo một chủ đề. Đọc mô hình trước, làm lab trên môi trường riêng, ghi bằng chứng và tự giải thích failure mode. Các ví dụ dựa trên ứng dụng Notes API và bốn JD đã cung cấp.", ""]
    used = set()
    for name, prefixes in includes:
        used.add(name)
        available = sections(name)
        for prefix in prefixes:
            matches = [(key, value) for key, value in available.items() if key.startswith(prefix)]
            if len(matches) != 1:
                raise ValueError(f"Selection ambiguous: {slug} {name} {prefix}: {len(matches)}")
            heading, body = matches[0]
            body = re.sub(r"(?m)^## Bài \d+\. ", "## ", body, count=1)
            blocks.extend([body, ""])
    deep = ROOT.parent / "topics" / "_deep" / f"{slug}.md"
    if deep.exists():
        blocks.extend([deep.read_text(encoding="utf-8").strip(), ""])
    intensive = ROOT.parent / "topics" / "_intensive" / f"{slug}.md"
    if intensive.exists():
        blocks.extend([intensive.read_text(encoding="utf-8").strip(), ""])
    workbook = ROOT.parent / "topics" / "_workbook" / f"{slug}.md"
    if workbook.exists():
        blocks.extend([workbook.read_text(encoding="utf-8").strip(), ""])
    blocks.extend(["## Tự đánh giá", "", "1. Giải thích mô hình bằng lời của bạn, không dựa vào tên công cụ.", "2. Làm lab và lưu kết quả mong đợi cùng kết quả thực tế.", "3. Tạo một lỗi có kiểm soát, dùng bằng chứng để khoanh vùng và phục hồi.", "4. Trả lời một câu hỏi thiết kế: tại sao chọn phương án này, tradeoff và giới hạn là gì?", "", "## Nguồn chính thức và đọc thêm", ""])
    blocks.extend(f"- {url}" for url in BIBLIO[slug])
    (DEST / f"{slug}.md").write_text("\n".join(blocks) + "\n", encoding="utf-8")
    print(slug, len(" ".join(blocks).split()), "words")
