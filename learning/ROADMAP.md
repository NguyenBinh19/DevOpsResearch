# Lộ trình DevOps bám theo 4 JD người học cung cấp

## Phạm vi và mục tiêu

Đây là lộ trình rút ra từ **bốn JD cụ thể**: (1) Hybrid VMware/Kubernetes/MySQL, (2) Azure DevOps và bảo mật, (3) on-prem/cloud cho hệ thống vận hành liên tục, (4) cloud native/Kubernetes/IaC. Bốn JD không đại diện cho toàn bộ thị trường Việt Nam. Chúng có yêu cầu 2-4 năm kinh nghiệm, nên lộ trình này đặt mục tiêu xây nền tảng, lab và portfolio trước, rồi tiếp tục tích lũy kinh nghiệm vận hành thực tế. Đọc PDF không tự tạo ra kinh nghiệm production.

Người học bắt đầu từ con số 0. Mỗi module cần có bài giảng giải thích từ đầu, sơ đồ, ví dụ xuyên suốt, lab an toàn, kết quả mong đợi, tình huống lỗi, câu hỏi phỏng vấn và nguồn chính thức. Nếu một chủ đề đã biết, làm bài kiểm tra năng lực rồi chuyển nhanh; chưa đạt thì học và làm lab.

**Cách đóng gói tài liệu:** Roadmap dưới đây sắp thứ tự học. PDF không đóng gói theo giai đoạn; mỗi tập tập trung vào một chủ đề như Kubernetes, Helm hoặc Argo CD. Xem [danh mục PDF theo chủ đề](../lesson/README.md) để chọn tài liệu cụ thể.

## Bản đồ năng lực rút từ JD

| Nhóm năng lực | Công nghệ trong JD | Mức học |
|---|---|---|
| Hệ thống và mạng | Linux, Bash/PowerShell, DNS, TLS, firewall, Nginx, HAProxy, PHP-FPM | Hiểu sâu, chẩn đoán được |
| Phần mềm và dữ liệu | Python/TypeScript, API, webhook, SQL, MySQL/MariaDB/PostgreSQL, Redis | Đọc/sửa app nhỏ; vận hành sâu một DB quan hệ |
| Container và orchestration | Docker, Kubernetes, Helm, autoscaling, HA, self-healing | Tự triển khai và xử lý lỗi |
| Delivery | Git, GitLab CI, Jenkins, Azure DevOps, GitHub Actions, ArgoCD | Học sâu một CI theo nhánh; hiểu và so sánh các công cụ còn lại |
| Hạ tầng tự động | Terraform, Pulumi, Bicep/ARM, Ansible, kubespray | Terraform + Ansible thực hành; các công cụ khác học theo nhánh |
| Cloud và hybrid | AWS/Azure/GCP, VMware, Azure App Service/Functions/Storage/SQL/Service Bus, VNet/Private Endpoint/NSG | Học sâu một cloud; lab hybrid/VMware theo điều kiện máy |
| Quan sát và vận hành | Prometheus, Grafana, ELK/ECK/EFK, Loki, Zabbix, OpenTelemetry, App Insights/KQL | Tự xây luồng metric/log/trace và điều tra sự cố |
| Bảo mật | IAM/RBAC, Entra ID, Vault/Key Vault, OWASP, SAST/DAST/SCA, CVE | Áp dụng xuyên suốt lab và release |
| Dữ liệu/middleware chuyên sâu | Oracle, MongoDB, Kafka/Connect, RabbitMQ, ActiveMQ, Ceph, MinIO, NFS, SAN | Hiểu mô hình và failure mode; chọn hệ phù hợp để thực hành sâu |
| AI tự động hóa | Azure OpenAI, agent, MCP, RAG, Copilot/Power Automate | Nhánh tùy chọn sau nền tảng tự động hóa và bảo mật |

## Thứ tự học bắt buộc

### 0. Định hướng và mô hình hệ thống

Hiểu DevOps giải quyết vấn đề gì; đường đi từ commit đến người dùng; cách học/làm lab; đánh giá đầu vào. Đầu ra: hồ sơ học, lịch học và ứng dụng mẫu.

### 1. Linux, mạng, Git, scripting và ứng dụng

Tiến trình/service, filesystem/quyền, log, SSH, DNS/TCP/HTTP/TLS, Git, Python/Bash/PowerShell căn bản, API và SQL. Đầu ra: ứng dụng nhỏ chạy local, một sự cố được điều tra theo lớp, Git history và test.

### 2. Docker, kiểm thử và CI/CD

Image/container/volume/network, unit/integration/smoke test, artifact/version, pipeline, release và rollback. Lab bắt đầu bằng GitHub Actions vì dễ tái tạo, sau đó làm GitLab CI hoặc Azure DevOps theo nhánh đã chọn; Jenkins được học theo kiến trúc runner/agent. Đầu ra: app + database trong container và CI bắt được lỗi cố ý.

### 3. Cloud, IAM, network và Terraform

Chọn một cloud để học sâu; Terraform plan/state/locking/drift; quyền tối thiểu, network private/public, chi phí và cleanup. Đầu ra: môi trường lab nhỏ có thể tái tạo và hủy có kiểm soát.

### 4. Vận hành, observability và SRE

Logs/metrics/traces, SLI/SLO, alert, incident, postmortem, backup/restore, RPO/RTO và performance. Đầu ra: dashboard/runbook, một lỗi được tạo an toàn và khôi phục có bằng chứng.

### 5. Kubernetes

Cluster, workload, Service, ingress, config/secrets, storage, requests/limits, HPA, RBAC, NetworkPolicy và troubleshooting. Đầu ra: triển khai app trên cluster lab và giải thích ba loại lỗi.

### 6. Bảo mật và độ tin cậy

Threat model, hardening, pipeline permissions, dependency/image scanning, secrets, backup/DR, capacity và cost. Đầu ra: security review và diễn tập restore/incident.

### 7. Portfolio và phỏng vấn

Hoàn thiện dự án xuyên suốt, README tái tạo, ADR, release/rollback/restore, demo và phỏng vấn tình huống. Đầu ra: repo review được và câu chuyện kỹ thuật trung thực.

## Chuyên đề bám JD, học sau phần nền tảng liên quan

### 8. Hybrid, VMware, storage và on-prem

VM/hypervisor, cluster/HA, datastore, NFS/SAN/Ceph/MinIO, Harbor/Vault, Ansible và thiết kế hybrid. Bám JD 1 và 3. Không cần phần cứng doanh nghiệp để học mô hình; lab máy ảo nhỏ chỉ thực hiện khi máy đủ tài nguyên.

### 9. Azure enterprise

VNet/NSG/Private Endpoint, Entra ID/RBAC/managed identity, App Service/Functions, Storage/Key Vault/Service Bus/Azure SQL, Azure DevOps, App Insights/Log Analytics/KQL, Bicep/ARM. Bám JD 2. Tài nguyên cloud chỉ tạo sau khi có ngân sách và cleanup.

### 10. Database và messaging

MySQL/MariaDB và PostgreSQL, replication, backup/restore, query/connection tuning, Redis; sau đó so sánh Oracle/MongoDB/Kafka/Connect/RabbitMQ/ActiveMQ. Bám JD 1 và 3. Chọn một DB quan hệ để vận hành sâu trước.

### 11. CI/CD đa công cụ, Helm và GitOps

GitLab CI/Jenkins/Azure DevOps/GitHub Actions, Helm chart, ArgoCD, Ansible và release cho microservices. Bám cả bốn JD. Phân biệt rõ CI tạo artifact, Helm đóng gói manifest, ArgoCD đồng bộ trạng thái và Ansible cấu hình máy.

### 12. Edge và observability stack

Nginx/HAProxy/PHP-FPM, ingress/Kong/WSO2/Keycloak; Prometheus/Grafana, ECK/ELK, Loki, Zabbix, OpenTelemetry và Azure Monitor. Bám JD 1-4. Học từ luồng request và câu hỏi chẩn đoán, rồi mới cài stack.

## Cách đánh giá sau mỗi module

Không đánh dấu hoàn thành sau khi chỉ đọc. Cần bốn bằng chứng: (1) tự giải thích mô hình, (2) làm lab được, (3) xử lý một lỗi có kiểm soát, (4) trả lời câu hỏi thiết kế/tradeoff. Công nghệ không có lab khả thi vì chi phí hoặc phần cứng cần có bài thiết kế, phân tích log/config và ghi rõ giới hạn trải nghiệm.

## Thời lượng

Không áp một mốc 24 tuần cho toàn bộ nội dung. Với 6-8 giờ/tuần, phần lõi và các chuyên đề sẽ kéo dài nhiều tháng đến hơn một năm tùy điểm xuất phát. Chỉ chuyển module khi đạt cổng năng lực. Kiến thức từ PDF và lab là nền để ứng tuyển; năng lực mức cao cần kinh nghiệm xử lý hệ thống thật và phối hợp với nhóm.
