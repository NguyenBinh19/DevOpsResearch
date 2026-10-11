# Chuyên đề 11 - CI/CD đa công cụ, Helm và GitOps

Bốn JD đều muốn người có khả năng xây và sửa đường phát hành. Học thuộc tên GitLab CI, Jenkins, Azure DevOps, GitHub Actions, Helm và ArgoCD không đủ. Mục tiêu của chuyên đề là tự giải thích dữ liệu đi qua đâu, danh tính nào được phép làm gì, bằng chứng nào chặn một bản lỗi, và quay lại phiên bản ổn định ra sao. Sau khi học, hãy chọn **một** CI để thực hành sâu theo môi trường mục tiêu; các hệ còn lại học qua cách ánh xạ khái niệm.

```text
commit -> CI/test -> immutable image -> registry
                                      |
                               deployment Git PR
                                      |
                              Argo CD -> Kubernetes
                                      |
                              smoke test + telemetry
```

Terraform/Ansible chuẩn bị hạ tầng và máy chạy bên dưới. Sơ đồ này giúp xác định bước nào phải rollback khi lỗi: artifact, cấu hình triển khai, hay hạ tầng.

## Bài 1. Tách các trách nhiệm trong một lần phát hành

Developer tạo commit. CI lấy đúng commit, chạy kiểm tra, đóng gói artifact bất biến, gắn định danh và lưu vào registry. CD chọn artifact đã được kiểm tra, cập nhật cấu hình triển khai và xác nhận dịch vụ hoạt động. GitOps dùng Git làm nơi mô tả trạng thái mong muốn; controller so trạng thái đó với cluster và đồng bộ. Helm tạo bộ manifest Kubernetes từ chart và values. Ansible cấu hình máy chủ hoặc chạy tác vụ có thể lặp. Các công cụ này cùng nằm trong một chuỗi nhưng không thay thế nhau.

Ví dụ Notes API: commit `a1b2c3` vượt unit test; pipeline build image `notes-api@sha256:...`; một thay đổi trong repo môi trường cập nhật image digest; Argo CD phát hiện thay đổi và đồng bộ Deployment; smoke test gọi `/health` và `GET /notes`; monitoring theo dõi error rate. Nếu cùng một tag `latest` bị ghi đè, bạn khó biết chính xác mã nào đã chạy. Vì vậy trong báo cáo release cần lưu commit, digest, môi trường, thời điểm và người/phê duyệt liên quan.

**Câu hỏi kiểm tra:** Nếu CI xanh nhưng ứng dụng lỗi sau triển khai, CI đã chứng minh được điều gì? Trả lời đúng: chỉ các kiểm tra thực sự được chạy trên artifact/điều kiện cụ thể; nó không chứng minh môi trường production và đường truy cập người dùng đều hoạt động. Cần deployment verification và tín hiệu vận hành.

## Bài 2. Cấu trúc pipeline và các cổng chất lượng

Một pipeline thực dụng có các bước: kiểm tra cú pháp/định dạng; unit test; kiểm tra dependency và secret; build image; integration test với dependency thật hoặc giả lập có chủ đích; quét image; publish; triển khai vào staging; smoke/E2E; phê duyệt nếu cần; triển khai production; kiểm tra sau release. Không nhất thiết mọi dự án cần tất cả ở ngày đầu. Thứ tự nên chặn lỗi rẻ và nhanh trước lỗi đắt và chậm. Các bước phải fail khi điều kiện thất bại, không chỉ in cảnh báo.

Unit test kiểm tra một đơn vị logic. Integration test kiểm tra ranh giới như app-database. E2E chạy luồng người dùng. SAST đọc mã; SCA kiểm tra dependency; DAST tương tác với ứng dụng chạy. Kết quả quét cần được phân loại theo khả năng khai thác, bối cảnh và chính sách, thay vì coi số CVE là một điểm duy nhất. Các cổng như coverage threshold không chứng minh chất lượng nếu test chỉ chạy qua dòng mã mà không kiểm tra hành vi.

Artifact phải tách khỏi pipeline chạy sau. Không build lại từ cùng branch ở mỗi môi trường vì dependency hoặc base image có thể đổi. Chuyển **cùng digest** từ staging sang production. Tài khoản CI chỉ cần quyền đọc mã, build/push vào registry và tạo thay đổi triển khai đúng phạm vi; không đặt cloud admin key dài hạn trong biến pipeline nếu có thể dùng danh tính ngắn hạn.

### Lab 1 - Vẽ pipeline có thể kiểm chứng

Đầu vào: `lesson/labs/notes-api/` và `ci-example.yml`. Đọc file cấu hình và chỉ ra trigger, job, runner, nơi gọi test và điều kiện fail. Thêm một test cố ý thất bại vào bản sao lab; chạy test local trước rồi so với kết quả pipeline nếu có repository. Ghi lại: commit gây lỗi, bước dừng, log bằng chứng và bản sửa. Sau đó viết ra ba bước chưa có trong ví dụ nhưng cần trước production: image scanning, staging smoke test và cách xác nhận rollback. **Kết quả mong đợi:** pipeline đỏ khi test lỗi; khi sửa lại, pipeline xanh cho đúng commit. **Dọn dẹp:** xóa nhánh/thử nghiệm lỗi, không xóa bằng chứng học tập đã ghi.

## Bài 3. Ánh xạ GitLab CI, Jenkins, Azure DevOps và GitHub Actions

| Ý niệm | GitLab CI | Jenkins | Azure DevOps | GitHub Actions |
|---|---|---|---|---|
| Định nghĩa | `.gitlab-ci.yml` | `Jenkinsfile` | `azure-pipelines.yml` | `.github/workflows/*.yml` |
| Đơn vị chạy | job trong stage | stage/step trên agent | stage/job/step | job/step trên runner |
| Máy thực thi | runner | agent/node | agent | runner |
| Bí mật và quyền | CI variables/identity | credentials | service connection/identity | secrets/OIDC |
| Artifact | job artifact/registry | archive/registry | pipeline artifact/registry | artifact/registry |

GitLab CI gắn chặt với merge request, stages và runners. Jenkins rất linh hoạt qua pipeline/plugin nhưng bạn phải vận hành controller/agent, cập nhật plugin, quản trị credentials và backup. Azure DevOps Pipelines dùng YAML, stages, environments và service connections; với Azure cần hiểu danh tính của service connection. GitHub Actions dùng events, jobs, runners, permissions và reusable workflows. Một hệ không tự an toàn chỉ vì YAML trông ngắn. Điểm cần đánh giá là quyền của runner, nguồn action/plugin, kiểm soát branch, cache, artifact và đường phê duyệt.

### Tình huống: pipeline chạy trên mã pull request không đáng tin

Một PR từ bên ngoài sửa script build. Nếu runner có secret production, script có thể đọc secret. Cần tách job kiểm tra mã không tin cậy khỏi job có quyền publish/deploy; chỉ cấp quyền tối thiểu cho từng job; dùng protected branches/environments và review trước bước nhạy cảm. Đừng cho job PR fork dùng credential triển khai. Trong phỏng vấn, nêu rõ ranh giới tin cậy và cách kiểm chứng cấu hình thực tế của nền tảng đang dùng.

### Bài tập chuyển công cụ

Viết trên giấy pipeline bốn bước test -> build -> push -> deploy. Với mỗi CI trên, xác định cấu hình nằm đâu, runner nào thực thi, artifact đi qua đâu, và ai giữ quyền deploy. Bạn không cần thuộc cú pháp của bốn YAML; cần biết đọc tài liệu và phát hiện chỗ thiếu kiểm soát.

## Bài 4. Helm chart và cấu hình theo môi trường

Manifest Kubernetes thuần mô tả từng resource. Helm chart là gói template và metadata tạo ra manifest từ `values`. Một chart tối thiểu có `Chart.yaml`, `values.yaml` và `templates/`. `helm template` giúp xem YAML sẽ gửi tới cluster; `helm lint` kiểm tra một số lỗi chart; `helm upgrade --install` áp dụng release. Cần phân biệt version của **chart** với version của **ứng dụng/image**. Tăng chart version khi template hoặc giá trị mặc định thay đổi; giữ image digest riêng để biết chính xác bản chạy.

Values theo môi trường nên chứa những khác biệt thật như replica count, hostname, resource requests, endpoint. Đừng copy một chart thành ba thư mục staging/preprod/prod rồi sửa tay; chúng sẽ lệch dần. Không đưa password vào `values.yaml` trong Git. Với secret, chọn cơ chế phù hợp như external secret/Vault/Key Vault và kiểm tra quyền service account. `helm template` có thể hiển thị secret nếu đưa secret vào values; vì vậy log build cũng cần tránh in giá trị nhạy cảm.

### Lab 2 - Chart tối thiểu cho Notes API

Tạo thư mục `chart/notes-api`; định nghĩa Deployment và Service từ `lesson/labs/kubernetes-local/web.yaml` làm mẫu. Cho `image.repository`, `image.digest`, `replicaCount`, port và resources vào values. Chạy `helm lint chart/notes-api` và `helm template notes chart/notes-api`; đọc đầu ra, xác nhận Service selector khớp label pod, containerPort đúng, và image trỏ đúng digest. Đổi `replicaCount` từ 1 thành 2 rồi render lại, giải thích **chỉ desired replicas đổi**; chưa có bằng chứng cluster đã scale. Nếu chưa cài Helm, phác cấu trúc và đọc output ví dụ từ tài liệu chính thức trước. Dọn dẹp release lab bằng `helm uninstall notes` nếu đã cài trên cluster local.

**Lỗi có chủ đích:** đặt selector `app: notes-v2` nhưng pod label `app: notes`. Pod vẫn Running, Service không có endpoint. Dùng `kubectl get endpoints`, `kubectl describe service` và `kubectl get pods --show-labels` để chứng minh, sau đó sửa template.

## Bài 5. Argo CD và GitOps: vòng đồng bộ, drift, rollback

Argo CD theo dõi nguồn Git/Helm và áp trạng thái mong muốn lên cluster. Application chỉ ra repo, revision, path/chart và destination. Giao diện có thể báo `OutOfSync` khi live state khác desired state; `Healthy` nói về kiểm tra sức khỏe resource theo quy tắc của Argo, không bảo đảm request nghiệp vụ đúng. `Synced` cũng không có nghĩa test E2E đã qua. Cần thêm smoke test và observability.

Nếu ai sửa Deployment trực tiếp bằng `kubectl edit`, cluster có drift. Khi auto-sync bật, Argo có thể kéo về trạng thái Git. Nếu sửa production khẩn cấp, cần quy trình ghi nhận và đưa sửa đổi về Git, tránh lần reconcile sau ghi đè. Rollback GitOps thường là revert commit cấu hình rồi đồng bộ; tuy nhiên nếu migration database không tương thích bản cũ, chỉ revert image có thể làm lỗi nặng hơn. Trước release phải phân loại migration, khả năng rollback và chiến lược expand/contract schema.

### Lab 3 - Mô phỏng đồng bộ không cần cluster

Giả sử Git khai báo replicas=2, cluster đang chạy 1, trong khi HPA muốn 3. Hãy viết ai sở hữu trường replicas, điều gì có thể xảy ra nếu hai controller cùng ghi nó, và cấu hình cần thay đổi thế nào. Sau đó mô tả trình tự: CI tạo digest mới -> PR sửa repo triển khai -> review -> merge -> Argo sync -> smoke test -> giám sát. Nêu bằng chứng ở từng bước. Nếu có cluster local và Argo CD, thử trên namespace riêng; dọn dẹp Application và namespace lab sau khi ghi lại kết quả.

## Bài 6. Ansible, kubespray và ranh giới với Terraform

Terraform quản lý resource qua provider và state: network, VM, cluster managed, tài nguyên cloud. Ansible chạy playbook idempotent để cấu hình hệ điều hành, cài gói, tạo file, thiết lập service. Trong on-prem, có thể dùng Terraform tạo VM, Ansible cấu hình VM rồi kubespray (tập playbook Ansible) dựng Kubernetes. Trình tự này không tuyệt đối; sản phẩm cloud managed sẽ khác. Điều cốt lõi là phân định ownership để Terraform và Ansible không cùng sửa một cấu hình theo hai hướng.

Idempotent nghĩa chạy lại với cùng desired state không tạo thay đổi ngoài ý muốn. Kiểm chứng bằng cách chạy playbook lần hai và xem số task `changed`. Không coi `changed=0` là chứng minh ứng dụng khỏe; vẫn cần health check. Quản lý inventory, secret (Ansible Vault hoặc secret manager), version collection/role và giới hạn host để tránh chạy nhầm môi trường. Với kubespray, phải xem ma trận phiên bản Kubernetes, OS, container runtime và network plugin trước khi triển khai.

### Tình huống phỏng vấn về release microservices

Dịch vụ A gọi B. B đổi API không tương thích. Nếu deploy A trước B hoặc rollback B sau khi A đã đổi, request lỗi dù từng pipeline đều xanh. Hãy nêu contract test, triển khai backward compatible, canary hoặc thứ tự release, theo dõi metric theo phiên bản và cách dừng. Một release an toàn là thuộc tính của **toàn hệ thống**, không chỉ của từng image.

## Case study có lời giải: deploy xanh, người dùng vẫn lỗi

**Bối cảnh:** pipeline CI xanh; Helm release báo deployed; Argo CD báo Synced/Healthy. Sau năm phút, tỷ lệ 5xx ở endpoint tạo ghi chú tăng. Hỏi đầu tiên: smoke test đã gọi endpoint nào, dùng dữ liệu/quyền gì, telemetry gắn phiên bản nào, lỗi chỉ ở Pod mới hay mọi Pod? `/health` đơn giản có thể vẫn 200 trong khi đường ghi DB thất bại. Nếu chỉ version mới lỗi, dừng promotion và rollback image/config theo runbook; nếu migration DB không tương thích, phải xử lý schema trước khi quay app cũ. Nếu mọi version lỗi cùng lúc, điều tra dependency chung như DB, Vault hoặc ingress.

**Bài học release:** định nghĩa cổng sau deploy theo luồng người dùng quan trọng, theo dõi error/latency trong khoảng đủ dài, có người/on-call nhận cảnh báo và ghi digest đang chạy. `Healthy` của controller là một tín hiệu hạ tầng, không phải xác nhận nghiệp vụ. Cổng CI phải giữ log và test report cho đúng commit để sau sự cố tái dựng được chuỗi phát hành.

## Cổng hoàn thành và câu hỏi phỏng vấn

1. Giải thích từ commit đến production: mỗi công cụ lưu trạng thái gì, ai có quyền ghi, đâu là nguồn chân lý.
2. Cho thấy một pipeline dừng khi test lỗi và một artifact có định danh bất biến.
3. Render Helm chart, đọc resource tạo ra và xử lý lỗi Service không có endpoint.
4. Mô tả drift của Argo CD, rollback kèm migration database và giới hạn của trạng thái `Healthy`.
5. Trả lời: "Tại sao một PR từ fork không nên có quyền deploy?" và "Làm sao chứng minh staging và production chạy cùng artifact?"

Nếu chưa có môi trường để chạy Argo/Jenkins/kubespray, nộp sơ đồ, cấu hình mẫu và phân tích failure mode; ghi rõ đây là bài thiết kế chứ chưa phải kinh nghiệm vận hành thật.

## Tài liệu chính thức để đối chiếu cú pháp theo phiên bản

- GitLab CI pipelines: https://docs.gitlab.com/ci/pipelines/
- Jenkins Pipeline: https://www.jenkins.io/doc/book/pipeline/syntax/
- Azure Pipelines YAML schema: https://learn.microsoft.com/azure/devops/pipelines/yaml-schema/?view=azure-pipelines
- GitHub Actions: https://docs.github.com/en/actions
- Helm documentation: https://helm.sh/docs/
- Argo CD documentation: https://argo-cd.readthedocs.io/en/stable/
- Kubespray documentation: https://github.com/kubernetes-sigs/kubespray/tree/master/docs
