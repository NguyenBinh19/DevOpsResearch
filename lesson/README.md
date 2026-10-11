# Thư viện bài giảng DevOps theo chủ đề

Mỗi PDF trong [topics](topics/) tập trung vào **một chủ đề hoặc một nhóm công nghệ có cùng trách nhiệm**. Không chia PDF theo giai đoạn. [Roadmap](../learning/ROADMAP.md) chỉ dùng để quyết định thứ tự học; [PROGRESS](../learning/PROGRESS.md) ghi bằng chứng thực hành. Tài liệu bám bốn JD bạn đã cung cấp, không đại diện toàn bộ thị trường Việt Nam.

**Tình trạng biên soạn:** cả 23 chủ đề đã được mở rộng với giải thích cơ chế, bài thực hành hoặc bài thiết kế, kết quả cần quan sát, ca lỗi và câu hỏi có lời giải. Kubernetes và Argo CD có bản nguồn viết lại trọn vẹn trong [topics/_master](topics/_master/); các tập còn lại được biên tập bổ sung trên nền bản cũ trong [topics/_intensive](topics/_intensive/) và [topics/_workbook](topics/_workbook/). Đây là giáo trình để bắt đầu học và luyện giải thích/vận hành; thành thạo production vẫn cần thực hành trên hệ thống thật, review và xử lý sự cố có giám sát.

## Nền tảng

| Chủ đề | PDF | Điểm cần tự chứng minh |
|---|---|---|
| DevOps và vòng đời dịch vụ | [Mở PDF](topics/01-devops.pdf) | Vẽ đường từ commit tới người dùng |
| Linux | [Mở PDF](topics/02-linux.pdf) | Đọc process, quyền, service và log |
| Networking | [Mở PDF](topics/03-networking.pdf) | Khoanh vùng DNS/TCP/TLS/HTTP |
| Git | [Mở PDF](topics/04-git.pdf) | Giải quyết conflict, review và revert |
| Notes API, Python, HTTP, SQL | [Mở PDF](topics/05-python-api.pdf) | Chạy app mẫu và kiểm tra dữ liệu |
| Docker | [Mở PDF](topics/06-docker.pdf) | Build image, giữ dữ liệu, xử lý lỗi |

## Xây và phát hành hệ thống

| Chủ đề | PDF | Điểm cần tự chứng minh |
|---|---|---|
| CI/CD | [Mở PDF](topics/07-ci-cd.pdf) | Pipeline chặn lỗi, artifact rõ phiên bản |
| Terraform | [Mở PDF](topics/08-terraform.pdf) | Đọc plan/state/drift và dọn lab |
| Cloud, IAM và mạng riêng | [Mở PDF](topics/09-cloud-iam.pdf) | Quyền tối thiểu, đường public/private |
| Kubernetes | [Mở PDF](topics/10-kubernetes.pdf) | Deploy, chẩn đoán Pod/Service, rollback |
| Helm | [Mở PDF](topics/11-helm.pdf) | Render chart, kiểm tra manifest/release |
| Argo CD | [Mở PDF](topics/12-argocd.pdf) | Phân biệt sync, health, drift và rollback |

## Vận hành và chuyên đề JD

| Chủ đề | PDF | Điểm cần tự chứng minh |
|---|---|---|
| Observability | [Mở PDF](topics/13-observability.pdf) | Dùng metric/log/trace điều tra một request |
| SRE và incident | [Mở PDF](topics/14-sre-incident.pdf) | SLO, alert, runbook, postmortem |
| DevSecOps | [Mở PDF](topics/15-security.pdf) | Threat model, secret và quyền pipeline |
| VMware và hybrid | [Mở PDF](topics/16-vmware-hybrid.pdf) | Failure domain, capacity N-1, DR |
| Storage | [Mở PDF](topics/17-storage.pdf) | Chọn block/file/object, restore thử |
| Ansible | [Mở PDF](topics/18-ansible.pdf) | Playbook idempotent và giới hạn host |
| Azure enterprise | [Mở PDF](topics/19-azure.pdf) | Identity, Private Endpoint, dịch vụ và ADO |
| Database quan hệ | [Mở PDF](topics/20-database.pdf) | Query, replication, backup/restore |
| Redis và messaging | [Mở PDF](topics/21-messaging.pdf) | Retry, idempotency, backlog và ordering |
| Edge và API gateway | [Mở PDF](topics/22-edge.pdf) | Nginx/HAProxy/ingress, tìm lỗi 502/503 |
| Portfolio/phỏng vấn | [Mở PDF](topics/23-portfolio.pdf) | Trình bày bằng chứng và giới hạn lab |

## Cách dùng

Chọn PDF theo roadmap hoặc JD mục tiêu. Mỗi tập có mô hình, ví dụ, lab hoặc bài thiết kế, lỗi thường gặp, câu hỏi tự đánh giá và tài liệu chính thức. Mã thực hành nằm trong [labs](labs/); những tập cần đọc mã offline có phụ lục. Khi làm xong, ghi bằng chứng trong `learning/PROGRESS.md` thay vì đánh dấu chỉ vì đã đọc.

Một số công nghệ doanh nghiệp trong JD như vSphere production, SAN, Ceph, ECK, Oracle, WSO2, Kafka cluster cần hạ tầng/kinh nghiệm thật để thành thạo. Tập PDF cho mô hình, failure mode và cách kiểm chứng; không biến lab nhỏ thành tuyên bố kinh nghiệm production.
