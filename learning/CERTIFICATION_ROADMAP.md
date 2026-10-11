# Lộ trình chứng chỉ DevOps: từ nền tảng đến nâng cao

> Mục đích của tài liệu này là chọn chứng chỉ có ích cho mục tiêu học và ứng tuyển DevOps, dựa trên bốn JD người học đã cung cấp. Bốn JD này không đại diện toàn bộ thị trường Việt Nam. Chứng chỉ xác nhận một phần kiến thức; không thay thế kinh nghiệm xử lý hệ thống, dự án, portfolio hay khả năng giải thích quyết định kỹ thuật.

## Kết luận nhanh: học và thi chứng chỉ nào đầu tiên?

**Chứng chỉ đầu tiên nên nhắm đến: RHCSA.** Các JD của bạn đều coi trọng Linux/server; một JD còn yêu cầu Linux và hạ tầng on-premise/VMware. RHCSA giúp xây nền quản trị Linux bằng bài thi thực hành. Nếu bạn muốn chứng chỉ Linux trung lập nhà cung cấp hơn, chọn **LFCS thay RHCSA**. Không cần lấy cả hai ngay từ đầu.

Thứ tự khuyến nghị mặc định:

1. **RHCSA** — nền tảng Linux (hoặc LFCS thay thế).
2. **Một chứng chỉ Cloud Associate** — chọn Azure nếu ưu tiên JD Azure; chọn AWS nếu quyết định theo AWS. Không học thi hai cloud cùng lúc lúc mới bắt đầu.
3. **HashiCorp Terraform Associate** — sau khi đã tự viết và áp dụng Terraform trong lab.
4. **CKA** — sau Linux, mạng, container và Kubernetes căn bản.
5. **Một chứng chỉ DevOps chuyên sâu theo cloud** — AZ-400 cho nhánh Azure; AWS DevOps Engineer Professional cho nhánh AWS, nên để khi đã có kinh nghiệm thực hành đáng kể.
6. **CKS** — chuyên sâu bảo mật Kubernetes, sau CKA.

**CCNA** là nhánh cộng thêm có giá trị nếu định ứng tuyển hybrid/on-prem, xử lý mạng nội bộ hoặc muốn vững network. **CKAD** là nhánh cộng thêm nếu công việc thiên về đóng gói và triển khai workload/app trên Kubernetes.

## Bảng ưu tiên

| Ưu tiên | Chứng chỉ | Khi nào học/thi | Nhận xét |
|---|---|---|---|
| Bắt đầu | **RHCSA** | Sau khi đã học Linux căn bản và tự quản trị được một máy Linux lab | Lựa chọn đầu tiên mình đề xuất vì bám yêu cầu Linux/on-prem trong JD. Bài thi tập trung thực hành trên Red Hat Enterprise Linux. |
| Thay thế | **LFCS** | Cùng thời điểm dự định học RHCSA | Thi thực hành, trung lập nhà cung cấp. Chọn một trong RHCSA/LFCS trước; chỉ lấy chứng chỉ còn lại nếu công việc mục tiêu có lý do rõ ràng. |
| Cloud — Azure | **AZ-104: Azure Administrator Associate** | Sau nền tảng Linux, mạng, IAM và khi đã làm lab Azure | Khớp JD Azure: quản trị identity, storage, compute, networking và monitoring. Đây là nhánh cloud nên chọn nếu JD Azure là mục tiêu gần nhất. |
| Cloud — AWS | **AWS Certified Solutions Architect – Associate (SAA-C03)** | Sau khi hiểu networking, IAM, compute, storage, database và HA trên AWS | Hợp nếu chọn AWS. Chứng chỉ thiên về thiết kế giải pháp AWS, tạo nền cho DevOps chuyên sâu sau này. |
| IaC | **HashiCorp Certified: Terraform Associate (004)** | Sau khi tự viết cấu hình, module nhỏ, biến/output, plan/apply/destroy và hiểu state | Bám trực tiếp yêu cầu Terraform/IaC. Ôn bằng lab có thể tái tạo và dọn sạch; đừng chỉ học câu hỏi trắc nghiệm. |
| Kubernetes quản trị | **CKA: Certified Kubernetes Administrator** | Sau khi chạy workload, Service, storage, RBAC và tự chẩn đoán lỗi trên cluster lab | Chứng chỉ Kubernetes mình ưu tiên đầu tiên trong nhóm K8s; bài thi thực hành command line. Rất sát các JD yêu cầu vận hành Kubernetes. |
| Azure DevOps nâng cao | **Microsoft Certified: DevOps Engineer Expert (AZ-400)** | Sau AZ-104 và sau khi đã xây pipeline, IaC, deployment, security và observability trên Azure | Đường đi phù hợp JD Azure. Theo yêu cầu hiện được Microsoft công bố, cần AZ-104 hoặc Azure Developer Associate cùng AZ-400; với người mới bắt đầu, chọn AZ-104 làm prerequisite thực tế. Kiểm tra lại điều kiện trước ngày đăng ký thi. |
| AWS DevOps nâng cao | **AWS Certified DevOps Engineer – Professional (DOP-C02)** | Sau AWS Associate và kinh nghiệm thực tế xây/vận hành môi trường AWS | Để sau cùng: AWS mô tả ứng viên mục tiêu có từ hai năm kinh nghiệm provisioning, vận hành và quản lý môi trường AWS. Không nên xem đây là chứng chỉ nhập môn. |
| Kubernetes security | **CKS: Certified Kubernetes Security Specialist** | Sau khi đạt CKA và đã học RBAC, network policy, supply-chain/image security, runtime security | Chuyên sâu, có ích khi muốn nổi bật về Kubernetes security. Không cần là mục tiêu đầu tiên. |

## Nhánh cộng thêm theo hướng việc làm

### Nếu nhắm Hybrid, VMware, On-premise (gần JD 1 và 3)

- **CCNA** — học nếu kiến thức routing, switching, VLAN, DNS, firewall và troubleshooting mạng còn yếu hoặc công việc yêu cầu vận hành mạng nội bộ.
- **VMware Cloud Foundation certification (VCP/VCAP theo vai trò và phiên bản hiện hành)** — chỉ đầu tư khi nhà tuyển dụng mục tiêu thực sự dùng VMware/VCF và bạn có môi trường lab hoặc kinh nghiệm liên quan. Chương trình VMware/Broadcom có thể thay đổi, vì vậy kiểm tra danh mục chứng nhận chính thức trước khi trả phí.
- Sau nền tảng: RHCSA → CCNA (nếu cần) → Terraform → CKA. Có thể bổ sung Ansible/RHCE theo công việc tự động hóa Linux; ưu tiên kỹ năng và dự án trước khi mua thêm kỳ thi.

### Nếu nhắm Azure DevOps (gần JD 2)

- Có thể học nội dung **AZ-900: Azure Fundamentals** để làm quen thuật ngữ nếu hoàn toàn mới với cloud. Đây là chứng chỉ nhập môn, tùy chọn; nếu đã học được kiến thức và tự làm lab thì có thể bỏ qua kỳ thi.
- Nhánh chính: **AZ-104 → AZ-400**. Học thêm Terraform hoặc Bicep theo nhu cầu JD; thực hành Key Vault, managed identity, VNet/private endpoint, Azure DevOps YAML, monitoring, security scan và xử lý incident.
- JD nhắc AI/agent như điểm cộng. Chưa cần lấy chứng chỉ AI trước khi có nền tảng cloud, pipeline, security và scripting; hãy làm một automation project có human approval và audit trail trước.

### Nếu nhắm Cloud-native / đa cloud

- Chọn một cloud Associate (**AWS SAA** hoặc **AZ-104**) để học sâu trước.
- Terraform Associate → CKA → CKS là nhánh vendor-neutral tương đối phù hợp.
- **CKAD** có thể thêm nếu vai trò tập trung vào phát triển cấu hình ứng dụng, probes, resources, deployment strategies và Helm. Với mục tiêu vận hành cluster, ưu tiên CKA trước.

## Chứng chỉ nhập môn tùy chọn

| Chứng chỉ | Khi nào đáng thi | Khi nào có thể bỏ qua |
|---|---|---|
| **AZ-900: Azure Fundamentals** | Cần một khung khái niệm cloud có cấu trúc, chưa từng dùng Azure | Đã hiểu cloud cơ bản và đang cần thời gian cho AZ-104/lab. |
| **AWS Certified Cloud Practitioner** | Muốn làm quen thuật ngữ và mô hình dịch vụ AWS trước khi học Associate | Có thể học tài liệu nền rồi đi thẳng SAA nếu tự học được. |
| **KCNA: Kubernetes and Cloud Native Associate** | Muốn một mốc kiến thức cloud-native nhẹ trước CKA | Nếu đã học Kubernetes căn bản và sẵn sàng lab, dành công sức cho CKA sẽ sát công việc hơn. |

Các chứng chỉ nhập môn này không phải điều kiện bắt buộc trong lộ trình. Hãy ưu tiên thời gian cho Linux, mạng, cloud lab, Terraform, CI/CD và Kubernetes thực hành.

## Mốc sẵn sàng trước khi đăng ký thi

Đừng đăng ký chỉ vì đã xem hết khóa học. Dùng các cổng năng lực này:

- **RHCSA/LFCS:** có thể tự tạo user/group, quyền, filesystem, service, process, package, SSH, firewall cơ bản, phân tích log và khôi phục cấu hình sai trong máy ảo dùng một lần.
- **AZ-104/AWS SAA:** tự giải thích được IAM, network segmentation, compute, storage, backup, HA, monitoring và chi phí; triển khai một lab nhỏ, rồi xóa tài nguyên an toàn.
- **Terraform Associate:** viết được cấu hình từ đầu, đọc plan, giải thích state/drift, tái sử dụng module nhỏ và biết cách tránh để lộ secret.
- **CKA:** triển khai workload, Service và storage; xử lý Pod Pending/CrashLoopBackOff, lỗi DNS/service, probe, resource và quyền RBAC trong cluster lab.
- **AZ-400/AWS DevOps Professional:** có một pipeline hoàn chỉnh từ commit đến deployment, kiểm thử, quản lý artifact, security gate, rollback và quan sát sau release.
- **CKS:** hiểu và thực hành hardening cluster, quyền tối thiểu, NetworkPolicy, bảo vệ image/secret và phản ứng với cấu hình nguy hiểm.

Sau mỗi lab, lưu lại repository, sơ đồ, README tái tạo, ảnh/log kết quả, lỗi đã gặp và cách khắc phục. Đây là bằng chứng hữu ích khi phỏng vấn; không ghi lab cá nhân thành kinh nghiệm production.

## Danh sách ngắn gọn để theo dõi

- [ ] **Đầu tiên: RHCSA** (hoặc LFCS nếu chọn hướng Linux trung lập)
- [ ] **Chọn một cloud:** AZ-104 *hoặc* AWS SAA
- [ ] Terraform Associate (004)
- [ ] CKA
- [ ] Chọn chứng chỉ nâng cao theo cloud: AZ-400 *hoặc* AWS DevOps Engineer Professional
- [ ] CKS
- [ ] CCNA — nếu nhắm hybrid/on-prem hoặc cần củng cố network
- [ ] CKAD — nếu công việc thiên triển khai workload/app trên Kubernetes
- [ ] VMware VCP/VCAP — nếu công việc mục tiêu thực sự yêu cầu VMware/VCF
- [ ] AZ-900, AWS Cloud Practitioner, KCNA — chứng chỉ nhập môn tùy chọn, không cần lấy tất cả

## Nguồn chính thức để kiểm tra nội dung và điều kiện hiện hành

- Red Hat RHCSA: https://www.redhat.com/en/services/training/ex200-red-hat-certified-system-administrator-rhcsa-exam
- Red Hat certification FAQ: https://www.redhat.com/en/services/training-and-certification/faq
- Linux Foundation LFCS: https://training.linuxfoundation.org/certification/linux-foundation-certified-sysadmin-lfcs/
- Microsoft AZ-104: https://learn.microsoft.com/en-us/credentials/certifications/exams/az-104/
- Microsoft DevOps Engineer Expert: https://learn.microsoft.com/en-us/credentials/certifications/devops-engineer/
- AWS Solutions Architect Associate: https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03.html
- AWS DevOps Engineer Professional: https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02.html
- Terraform Associate: https://developer.hashicorp.com/certifications/terraform-associate
- CKA: https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/
- CKS: https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/
- CKAD: https://training.linuxfoundation.org/certification/certified-kubernetes-application-developer-ckad/
- Cisco CCNA: https://www.cisco.com/site/us/en/learn/training-certifications/certifications/enterprise/ccna/index.html
- AWS certification catalog: https://docs.aws.amazon.com/aws-certification/latest/examguides/

> Trước khi thanh toán, hãy kiểm tra lại tên chứng chỉ, mã bài thi, prerequisite, phiên bản sản phẩm, ngôn ngữ thi và chính sách gia hạn trên trang chính thức. Chương trình chứng chỉ thay đổi theo thời gian.
